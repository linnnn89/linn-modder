"""Use an existing ComfyUI installation for offline SAM3 cutout; no server required."""
import argparse
import gc
import json
import os
from pathlib import Path
import sys
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--comfy', type=Path, required=True, help='ComfyUI source directory containing comfy/ and main.py')
parser.add_argument('--checkpoint', type=Path, required=True, help='Existing local SAM3/SAM3.1 checkpoint')
parser.add_argument('--image', type=Path, required=True, help='Source image; never modified')
parser.add_argument('--output', type=Path, required=True, help='New output directory; existing paths are refused')
parser.add_argument('--prompt', default='person', help='Short English object description; ignored when --box is supplied')
parser.add_argument('--box', type=float, nargs=4, metavar=('X1', 'Y1', 'X2', 'Y2'),
                    help='Optional box in source pixels, origin at top left; selects box mode instead of text')
parser.add_argument('--refine-iterations', type=int, choices=range(6), default=2,
                    help='Native SAM refinement count, 0..5; text mode 0 uses detector masks directly')
parser.add_argument('--compare-raw', action='store_true',
                    help='Also save the same selection at refinement 0, without reloading the model')
opts = parser.parse_args()
opts.comfy = opts.comfy.resolve()
opts.checkpoint = opts.checkpoint.resolve()
opts.image = opts.image.resolve()
opts.output = opts.output.resolve()
if not (opts.comfy / 'main.py').is_file() or not (opts.comfy / 'comfy_extras/nodes_sam3.py').is_file():
    parser.error('--comfy must point to an existing ComfyUI installation with native SAM3 nodes')
if not opts.checkpoint.is_file() or not opts.image.is_file():
    parser.error('--checkpoint and --image must be existing local files')
if opts.output.exists():
    parser.error('--output already exists; choose a new directory to preserve previous results')
if opts.box and not (0 <= opts.box[0] < opts.box[2] and 0 <= opts.box[1] < opts.box[3]):
    parser.error('--box requires 0 <= X1 < X2 and 0 <= Y1 < Y2')

os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'
sys.path.insert(0, str(opts.comfy))
sys.argv = [sys.argv[0], '--disable-pinned-memory', '--use-pytorch-cross-attention', '--fp16-unet']
import comfy.options
comfy.options.enable_args_parsing()
import torch
import numpy as np
from PIL import Image, ImageOps
# Windows embedded Python may omit the script directory from sys.path.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sam3_geometry import pad_to_square, box_to_padded, mask_to_source, boxes_to_source
import comfy.sd
import comfy.model_management
from comfy_extras.nodes_sam3 import SAM3_Detect
from comfy_extras.nodes_mask import InvertMask
from comfy_extras.nodes_compositing import JoinImageWithAlpha

if not torch.cuda.is_available():
    parser.error('This runner requires a working CUDA environment; CPU fallback is not implemented')
source = ImageOps.exif_transpose(Image.open(opts.image)).convert('RGB')
padded_source, padding = pad_to_square(source)
if opts.box and (opts.box[2] > source.width or opts.box[3] > source.height):
    parser.error('--box must stay within the source image dimensions')
warnings = []
if opts.box == [0.0, 0.0, float(source.width), float(source.height)]:
    warnings.append('full_canvas_box: this box adds no tighter subject location; review before trying another box')
opts.output.mkdir(parents=True, exist_ok=False)


def save_candidate(mask, prefix=''):
    # JoinImageWithAlpha inverts its input; match the official workflow polarity.
    inverse = InvertMask.execute(mask).result[0]
    rgba = JoinImageWithAlpha.execute(image, inverse).result[0]
    values = rgba[0].cpu().numpy()
    mask_values = mask[0].cpu().numpy()
    assert np.isfinite(values).all() and np.isfinite(mask_values).all(), 'Non-finite image or mask output'
    pixels = np.rint(values.clip(0, 1) * 255).astype(np.uint8)
    mask_pixels = np.rint(mask_values.clip(0, 1) * 255).astype(np.uint8)
    assert pixels.shape == (source.height, source.width, 4), 'Output dimensions changed'
    assert np.array_equal(pixels[:, :, 3], mask_pixels), 'Alpha polarity mismatch'
    assert np.array_equal(pixels[:, :, :3], np.asarray(source)), 'Source RGB changed'
    cutout = Image.fromarray(pixels)
    cutout.save(opts.output / (prefix + 'cutout.png'))
    Image.fromarray(mask_pixels).save(opts.output / (prefix + 'mask.png'))
    preview = Image.new('RGB', (source.width * 2, source.height))
    for i, color in enumerate(('white', '#202020')):
        bg = Image.new('RGBA', source.size, color)
        bg.alpha_composite(cutout)
        preview.paste(bg.convert('RGB'), (i * source.width, 0))
    preview.thumbnail((1600, 1000))
    preview.save(opts.output / (prefix + 'preview.png'))
    count = int(np.count_nonzero(mask_pixels))
    flags = []
    if count == 0:
        flags.append('empty_mask')
    elif count == mask_pixels.size:
        flags.append('full_mask')
    elif count / mask_pixels.size < 0.05:
        flags.append('foreground_below_5_percent_review_required')
    elif count / mask_pixels.size > 0.95:
        flags.append('foreground_above_95_percent_review_required')
    stats = dict(alpha_bbox=cutout.getchannel('A').getbbox(),
                 foreground_fraction=float(count / mask_pixels.size),
                 diagnostic_flags=flags)
    return stats, mask_pixels, preview


torch.cuda.reset_peak_memory_stats()
started = time.perf_counter()
with torch.inference_mode():
    model, clip, _, _ = comfy.sd.load_checkpoint_guess_config(
        str(opts.checkpoint), output_vae=False, output_clip=True)
    loaded = time.perf_counter()
    assert model is not None and clip is not None, 'Missing model or text encoder'
    family = model.model.model_config.unet_config['image_model']
    print('MODEL_LOADED', family, 'compute_dtype', model.model.get_dtype(), flush=True)
    image = torch.from_numpy(np.asarray(source).copy().astype(np.float32) / 255).unsqueeze(0)
    # Native SAM resizes to a square. Padding keeps the subject's proportions;
    # retain the original tensor separately so exports never include padding.
    model_image = torch.from_numpy(np.asarray(padded_source).copy().astype(np.float32) / 255).unsqueeze(0)
    conditioning, bboxes = None, None
    if opts.box:
        bboxes = box_to_padded(opts.box, padding)
    else:
        conditioning = clip.encode_from_tokens_scheduled(clip.tokenize(opts.prompt))
    mask, boxes = SAM3_Detect.execute(model, model_image, conditioning=conditioning, bboxes=bboxes,
                                     threshold=0.5, refine_iterations=opts.refine_iterations,
                                     individual_masks=False).result
    mask = mask_to_source(mask, source.size, padding)
    boxes = boxes_to_source(boxes, source.size, padding)
    torch.cuda.synchronize()
    inferred = time.perf_counter()
    selected, mask_pixels, preview = save_candidate(mask)
    comparison = None
    if opts.compare_raw:
        raw_started = time.perf_counter()
        if opts.refine_iterations == 0:
            raw_mask = mask
        else:
            raw_mask, _ = SAM3_Detect.execute(model, model_image, conditioning=conditioning, bboxes=bboxes,
                                             threshold=0.5, refine_iterations=0,
                                             individual_masks=False).result
            raw_mask = mask_to_source(raw_mask, source.size, padding)
        torch.cuda.synchronize()
        raw_seconds = time.perf_counter() - raw_started
        raw_stats, raw_pixels, raw_preview = save_candidate(raw_mask, 'raw-')
        raw_bool, selected_bool = raw_pixels > 0, mask_pixels > 0
        union = int(np.count_nonzero(raw_bool | selected_bool))
        comparison = dict(raw_refine_iterations=0, selected_refine_iterations=opts.refine_iterations,
                          raw_is_selected=opts.refine_iterations == 0, raw=raw_stats,
                          raw_segment_seconds=round(raw_seconds, 3),
                          changed_pixel_fraction=float(np.mean(raw_bool != selected_bool)),
                          intersection_over_union=float(np.count_nonzero(raw_bool & selected_bool) / union) if union else 1.0)
        sheet = Image.new('RGB', (preview.width, preview.height * 2))
        sheet.paste(raw_preview, (0, 0))
        sheet.paste(preview, (0, preview.height))
        sheet.save(opts.output / 'comparison.png')
    for flag in selected['diagnostic_flags']:
        warnings.append('selected_mask: ' + flag)
    for warning in warnings:
        print('WARNING:', warning, file=sys.stderr, flush=True)
    report = dict(checkpoint=str(opts.checkpoint), image=str(opts.image),
                  selection_mode='box' if opts.box else 'text', prompt=None if opts.box else opts.prompt,
                  input_box=opts.box, model_family=family, compute_dtype=str(model.model.get_dtype()),
                  refine_iterations=opts.refine_iterations, size=list(source.size), boxes=boxes,
                  preprocessing=dict(mode='pad_to_square', padded_size=list(padded_source.size),
                                     padding_ltrb=list(padding), fill_rgb=[255, 255, 255],
                                     model_input_box=bboxes, output_coordinates='source_pixels'),
                  **selected, comparison=comparison, warnings=warnings,
                  load_seconds=round(loaded-started, 3),
                  encode_and_segment_seconds=round(inferred-loaded, 3),
                  peak_allocated_mib=round(torch.cuda.max_memory_allocated()/2**20, 1),
                  peak_reserved_mib=round(torch.cuda.max_memory_reserved()/2**20, 1),
                  torch=torch.__version__, gpu=torch.cuda.get_device_name(),
                  alpha_polarity_verified=True, original_rgb_preserved=True,
                  visual_review='pending', ui_verified=False, game_verified=False)
    (opts.output / 'result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False), flush=True)
comfy.model_management.unload_all_models()
del model, clip
gc.collect()
if any(flag in ('empty_mask', 'full_mask') for flag in selected['diagnostic_flags']):
    sys.exit(2)  # Keep diagnostic artifacts, but do not treat an empty/full mask as a usable result.
