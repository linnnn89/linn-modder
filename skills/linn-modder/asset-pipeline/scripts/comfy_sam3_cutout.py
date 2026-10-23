"""Offline SAM3 cutout, reusable image encoding and opt-in trimap matting."""
import argparse
from contextlib import redirect_stdout
import gc
from io import BytesIO
import json
import math
import os
from pathlib import Path
import sys
import time
import uuid

# Windows embedded Python may omit the script directory from sys.path.
sys.path.insert(0, str(Path(__file__).resolve().parent))


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--comfy', type=Path, help='Existing ComfyUI source directory; required for SAM')
    parser.add_argument('--checkpoint', type=Path, help='Existing local SAM3/SAM3.1 checkpoint; required for SAM')
    parser.add_argument('--image', type=Path, required=True, help='Source working image; never modified')
    parser.add_argument('--output', type=Path, help='New output directory; existing paths refused')
    parser.add_argument('--bind-inputs', type=Path, help='Only register current image/mask/trimap hashes to a NEW JSON; no inference')
    parser.add_argument('--input-manifest', type=Path, help='Previously registered input JSON; required for matting')
    parser.add_argument('--gpu-wait-seconds', type=float, default=900, help='Maximum FIFO wait before loading SAM; default 900 seconds')
    parser.add_argument('--prompt', help='Explicit text mode; ignored when --box is supplied')
    parser.add_argument('--box', type=float, nargs=4, metavar=('X1', 'Y1', 'X2', 'Y2'),
                        help='Default selection: subject box in source pixels')
    parser.add_argument('--refine-iterations', type=int, choices=range(6), default=2)
    parser.add_argument('--compare-raw', action='store_true', help='Also save refinement-0 baseline')
    parser.add_argument('--cache-dir', type=Path, help='Optional local encoding cache across CLI calls; no prompt/mask state')
    parser.add_argument('--no-encoding-cache', action='store_true', help='Disable reuse for native baseline/comparison')
    parser.add_argument('--matting', choices=['off', 'pymatting'], default='off', help='Opt-in alpha estimation; never downloads')
    parser.add_argument('--trimap', type=Path, help='Reviewed same-size L PNG: 0 background, 128 unknown, 255 opaque foreground')
    parser.add_argument('--matting-roi', type=int, nargs=4, metavar=('X1', 'Y1', 'X2', 'Y2'),
                        help='Only write unknown alpha inside this source-pixel region')
    parser.add_argument('--mask', type=Path, help='Reuse existing same-size L mask for matting only; skip SAM/GPU entirely')
    opts = parser.parse_args()
    if not math.isfinite(opts.gpu_wait_seconds) or opts.gpu_wait_seconds <= 0:
        parser.error('--gpu-wait-seconds must be a finite positive number')
    if opts.bind_inputs and (opts.input_manifest or opts.output or opts.box or opts.prompt or opts.compare_raw or opts.cache_dir):
        parser.error('--bind-inputs only registers --image/--mask/--trimap; omit output, prompts and cache')
    if not opts.bind_inputs and opts.mask is None and opts.box is None and not opts.prompt:
        parser.error('Bbox is the default: supply --box X1 Y1 X2 Y2 in source pixels; '
                     'use --prompt TEXT only to explicitly select text mode')
    if opts.box and not (0 <= opts.box[0] < opts.box[2] and 0 <= opts.box[1] < opts.box[3]):
        parser.error('--box requires 0 <= X1 < X2 and 0 <= Y1 < Y2')
    if opts.mask is not None and (opts.box or opts.prompt or opts.compare_raw or opts.cache_dir):
        parser.error('--mask is matting-only; do not also select SAM prompts, comparisons or cache')
    if not opts.bind_inputs and opts.mask is not None and opts.matting == 'off':
        parser.error('--mask requires --matting pymatting and --trimap')
    if opts.matting != 'off' and opts.trimap is None:
        parser.error('--matting requires a reviewed --trimap; no automatic erosion/fill-holes')
    if not opts.bind_inputs and opts.matting == 'off' and (opts.trimap is not None or opts.matting_roi is not None):
        parser.error('--trimap/--matting-roi require --matting pymatting')
    if opts.no_encoding_cache and opts.cache_dir is not None:
        parser.error('--cache-dir conflicts with --no-encoding-cache')
    for name in ('comfy', 'checkpoint', 'image', 'output', 'cache_dir', 'trimap', 'mask', 'bind_inputs', 'input_manifest'):
        value = getattr(opts, name)
        if value is not None:
            setattr(opts, name, value.resolve())
    if not opts.bind_inputs and opts.mask is None:
        if opts.comfy is None or not (opts.comfy / 'main.py').is_file() or not (opts.comfy / 'comfy_extras/nodes_sam3.py').is_file():
            parser.error('--comfy must point to an existing ComfyUI installation with native SAM3 nodes')
        if opts.checkpoint is None or not opts.checkpoint.is_file():
            parser.error('--checkpoint must be an existing local file')
    for name in ('image', 'mask', 'trimap', 'input_manifest'):
        path = getattr(opts, name)
        if path is not None and not path.is_file():
            parser.error(f'--{name} must be an existing local file')
    if not opts.bind_inputs and opts.output is None:
        parser.error('--output is required for processing')
    if opts.output and opts.output.exists():
        parser.error('--output already exists; choose a new directory to preserve previous results')
    if not opts.bind_inputs and opts.trimap and opts.input_manifest is None:
        parser.error('Matting requires --input-manifest; first register the reviewed files with --bind-inputs NEW.json')
    if opts.cache_dir is not None and opts.cache_dir.exists() and not opts.cache_dir.is_dir():
        parser.error('--cache-dir must be a directory')
    return opts


def save_candidate(source, alpha, output, prefix=''):
    import numpy as np
    from PIL import Image
    if alpha.shape != (source.height, source.width) or alpha.dtype != np.uint8:
        raise ValueError('Alpha must be uint8 on the original canvas')
    pixels = np.dstack((np.asarray(source), alpha))
    cutout = Image.fromarray(pixels)
    cutout.save(output / (prefix + 'cutout.png'))
    Image.fromarray(alpha).save(output / (prefix + 'mask.png'))
    with Image.open(output / (prefix + 'cutout.png')) as saved:
        saved_pixels = np.asarray(saved)
        if not np.array_equal(saved_pixels[..., :3], np.asarray(source)) or not np.array_equal(saved_pixels[..., 3], alpha):
            raise AssertionError('Saved RGB or alpha changed')
    preview = Image.new('RGB', (source.width * 2, source.height))
    for i, color in enumerate(('white', '#202020')):
        bg = Image.new('RGBA', source.size, color)
        bg.alpha_composite(cutout)
        preview.paste(bg.convert('RGB'), (i * source.width, 0))
    preview.thumbnail((1600, 1000))
    preview.save(output / (prefix + 'preview.png'))
    count = int(np.count_nonzero(alpha))
    flags = []
    if count == 0:
        flags.append('empty_mask')
    elif count == alpha.size:
        flags.append('full_mask')
    elif count / alpha.size < 0.05:
        flags.append('foreground_below_5_percent_review_required')
    elif count / alpha.size > 0.95:
        flags.append('foreground_above_95_percent_review_required')
    return dict(alpha_bbox=cutout.getchannel('A').getbbox(),
                foreground_fraction=float(count / alpha.size), diagnostic_flags=flags), preview


def comparison_sheet(before, after, path):
    from PIL import Image
    sheet = Image.new('RGB', (after.width, after.height * 2))
    sheet.paste(before, (0, 0))
    sheet.paste(after, (0, before.height))
    sheet.save(path)


def run_sam(opts, source):
    import numpy as np
    sys.path.insert(0, str(opts.comfy))
    sys.argv = [sys.argv[0], '--disable-pinned-memory', '--use-pytorch-cross-attention', '--fp16-unet']
    import comfy.options
    comfy.options.enable_args_parsing()
    import torch
    import comfy.sd
    import comfy.model_management
    from comfy_extras.nodes_sam3 import SAM3_Detect
    from sam3_geometry import pad_to_square, box_to_padded, mask_to_source, boxes_to_source
    from sam3_encoding_cache import ImageEncodingCache, model_identity
    if not torch.cuda.is_available():
        raise RuntimeError('This runner requires a working CUDA environment for SAM; CPU fallback is not implemented')
    padded_source, padding = pad_to_square(source)
    torch.cuda.reset_peak_memory_stats()
    started = time.perf_counter()
    model = clip = None
    try:
        with torch.inference_mode():
            model, clip, _, _ = comfy.sd.load_checkpoint_guess_config(
                str(opts.checkpoint), output_vae=False, output_clip=opts.box is None)
            loaded = time.perf_counter()
            if model is None or (opts.box is None and clip is None):
                raise RuntimeError('Missing SAM model or requested text encoder')
            family = model.model.model_config.unet_config['image_model']
            model_image = torch.from_numpy(np.asarray(padded_source).copy().astype(np.float32) / 255).unsqueeze(0)
            bboxes = box_to_padded(opts.box, padding) if opts.box else None
            conditioning = None if opts.box else clip.encode_from_tokens_scheduled(clip.tokenize(opts.prompt))
            backbone = model.model.diffusion_model.detector.backbone['vision_backbone']
            identity = model_identity(opts.comfy, opts.checkpoint, model.model.get_dtype(),
                                      torch.__version__, torch.cuda.get_device_name())

            def predict(iterations):
                mask, boxes = SAM3_Detect.execute(
                    model, model_image, conditioning=conditioning, bboxes=bboxes,
                    threshold=0.5, refine_iterations=iterations, individual_masks=False).result
                values = mask_to_source(mask, source.size, padding)[0].cpu().numpy()
                if not np.isfinite(values).all():
                    raise ValueError('Non-finite SAM mask')
                return np.rint(values.clip(0, 1) * 255).astype(np.uint8), boxes_to_source(boxes, source.size, padding)

            with ImageEncodingCache(backbone, identity, opts.cache_dir, not opts.no_encoding_cache) as cache:
                selected, boxes = predict(opts.refine_iterations)
                torch.cuda.synchronize()
                inferred = time.perf_counter()
                raw_started = inferred
                raw = None
                if opts.compare_raw:
                    raw = selected.copy() if opts.refine_iterations == 0 else predict(0)[0]
                torch.cuda.synchronize()
                raw_seconds = time.perf_counter() - raw_started
            report = dict(checkpoint=str(opts.checkpoint), model_family=family,
                          compute_dtype=str(model.model.get_dtype()), boxes=boxes,
                          preprocessing=dict(mode='pad_to_square', padded_size=list(padded_source.size),
                                             padding_ltrb=list(padding), fill_rgb=[255, 255, 255],
                                             model_input_box=bboxes, output_coordinates='source_pixels'),
                          encoding_cache={**cache.stats, 'directory': str(opts.cache_dir) if opts.cache_dir else None,
                                          'checkpoint_identity': 'resolved_path_size_mtime_ns',
                                          'model_loads': 1},
                          load_seconds=round(loaded-started, 3),
                          encode_and_segment_seconds=round(inferred-loaded, 3),
                          raw_segment_seconds=round(raw_seconds, 3),
                          peak_allocated_mib=round(torch.cuda.max_memory_allocated()/2**20, 1),
                          peak_reserved_mib=round(torch.cuda.max_memory_reserved()/2**20, 1),
                          torch=torch.__version__, gpu=torch.cuda.get_device_name())
            return selected, raw, report
    finally:
        comfy.model_management.unload_all_models()
        del model, clip
        gc.collect()


def main():
    opts = parse_args()
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['TRANSFORMERS_OFFLINE'] = '1'
    import numpy as np
    from PIL import Image, ImageOps
    from sam3_matting import read_mask, validate_trimap, apply_matting
    from sam3_job import snapshot_inputs, bind_inputs, verify_binding, gpu_turn, write_json, sha256
    blobs, inputs = snapshot_inputs({name: getattr(opts, name) for name in ('image', 'mask', 'trimap')})
    with Image.open(BytesIO(blobs['image'])) as opened:
        rgba = ImageOps.exif_transpose(opened).convert('RGBA')
    source = rgba.convert('RGB')
    source_alpha = np.asarray(rgba)[..., 3].copy()
    if opts.box and (not np.isfinite(opts.box).all() or opts.box[2] > source.width or opts.box[3] > source.height):
        raise ValueError('--box must stay within the source image dimensions')
    trimap = None
    if opts.trimap:
        trimap = read_mask(BytesIO(blobs['trimap']), source.size, trimap=True)
        validate_trimap(trimap, opts.matting_roi)
    base = read_mask(BytesIO(blobs['mask']), source.size) if opts.mask else None
    if opts.bind_inputs:
        binding = bind_inputs(opts.bind_inputs, inputs, source.size)
        print(json.dumps(dict(status='inputs_bound', path=str(opts.bind_inputs), **binding), ensure_ascii=False))
        return 0
    binding_id = verify_binding(opts.input_manifest, inputs, source.size) if opts.input_manifest else None
    if opts.matting != 'off':
        try:
            from pymatting import estimate_alpha_cf  # Verify before SAM or output creation.
        except ImportError as exc:
            raise RuntimeError(f'PyMatting unavailable in this interpreter: {exc}; no automatic installation/download') from exc
    # Claim before waiting: another invocation cannot write this output, even on a race.
    opts.output.mkdir(parents=True, exist_ok=False)
    job = dict(job_id=uuid.uuid4().hex, pid=os.getpid(), inputs=inputs,
               binding_id=binding_id, status='claimed', output=str(opts.output))

    def job_state(queue):
        job.update(status=queue['status'], gpu_queue=dict(queue))
        write_json(opts.output / 'job.json', job)

    try:
        write_json(opts.output / 'job.json', job)
        warnings = []
        if opts.box == [0.0, 0.0, float(source.width), float(source.height)]:
            warnings.append('full_canvas_box: review target coverage; do not crop required parts to avoid this warning')
        raw, sam = None, dict(encoding_cache={'enabled': False, 'model_loads': 0, 'trunk_encodes': 0})
        queue = dict(status='not_required', reason='existing_mask_cpu_matting')
        if base is None:
            with gpu_turn(job['job_id'], opts.output, opts.gpu_wait_seconds, on_state=job_state) as admission:
                # Import torch and load weights only after admission. CPU matting never enters this queue.
                with redirect_stdout(sys.stderr):
                    base, raw, sam = run_sam(opts, source)
                # run_sam's frame and tensor references have gone before releasing the GPU slot.
                import torch
                gc.collect()
                torch.cuda.empty_cache()
                queue = dict(admission, status='completed')
        job.update(status='processing', gpu_queue=queue)
        write_json(opts.output / 'job.json', job)
        base = np.minimum(base, source_alpha)
        alpha = base
        matting = dict(status='off')
        before_preview = None
        if trimap is not None:
            _, before_preview = save_candidate(source, base, opts.output, 'segmentation-')
            Image.fromarray(trimap).save(opts.output / 'trimap.png')
            matte_started = time.perf_counter()
            with redirect_stdout(sys.stderr):
                alpha, matting = apply_matting(np.asarray(source), base, trimap, opts.matting_roi)
            alpha = np.minimum(alpha, source_alpha)
            matting.update(seconds=round(time.perf_counter()-matte_started, 3),
                           changed_pixels=int(np.count_nonzero(alpha != base)),
                           trimap_sha256=inputs['trimap']['sha256'])
        selected, preview = save_candidate(source, alpha, opts.output)
        if before_preview is not None:
            comparison_sheet(before_preview, preview, opts.output / 'matting-comparison.png')
        comparison = None
        if raw is not None:
            raw = np.minimum(raw, source_alpha)
            raw_stats, raw_preview = save_candidate(source, raw, opts.output, 'raw-')
            raw_bool, base_bool = raw > 0, base > 0
            union = int(np.count_nonzero(raw_bool | base_bool))
            comparison = dict(raw_refine_iterations=0, selected_refine_iterations=opts.refine_iterations,
                              raw_is_selected=opts.refine_iterations == 0, raw=raw_stats,
                              compared_stage='segmentation_before_matting',
                              raw_segment_seconds=sam['raw_segment_seconds'],
                              changed_pixel_fraction=float(np.mean(raw_bool != base_bool)),
                              intersection_over_union=float(np.count_nonzero(raw_bool & base_bool) / union) if union else 1.0)
            comparison_sheet(raw_preview, before_preview or preview, opts.output / 'comparison.png')
        warnings.extend('selected_mask: ' + flag for flag in selected['diagnostic_flags'])
        artifacts = {name: sha256((opts.output / name).read_bytes())
                     for name in ('mask.png', 'segmentation-mask.png', 'raw-mask.png', 'trimap.png')
                     if (opts.output / name).is_file()}
        report = dict(image=str(opts.image), source_sha256=inputs['image']['sha256'],
                      job_id=job['job_id'], binding_id=binding_id, inputs=inputs, artifacts=artifacts,
                      gpu_queue=queue,
                      selection_mode='existing_mask' if opts.mask else ('box' if opts.box else 'text'),
                      reused_mask=str(opts.mask) if opts.mask else None,
                      reused_mask_sha256=inputs['mask']['sha256'] if opts.mask else None,
                      prompt=None if opts.box or opts.mask else opts.prompt, input_box=opts.box,
                      refine_iterations=None if opts.mask else opts.refine_iterations, size=list(source.size),
                      **sam, **selected, comparison=comparison, matting=matting, warnings=warnings,
                      alpha_polarity_verified=True, original_rgb_preserved=True,
                      source_alpha_preserved_as_upper_bound=True,
                      visual_review='pending', ui_verified=False, game_verified=False)
        write_json(opts.output / 'result.json', report)
        rejected = any(flag in ('empty_mask', 'full_mask') for flag in selected['diagnostic_flags'])
        job.update(status='rejected' if rejected else 'completed')
        write_json(opts.output / 'job.json', job)
        print(json.dumps(report, ensure_ascii=False), flush=True)
        return 2 if rejected else 0
    except BaseException as exc:
        job.update(status='failed', error=type(exc).__name__, message=str(exc))
        write_json(opts.output / 'job.json', job)
        write_json(opts.output / 'error.json', dict(job_id=job['job_id'], error=type(exc).__name__, message=str(exc)))
        raise


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as exc:
        print(json.dumps(dict(error=type(exc).__name__, message=str(exc)), ensure_ascii=False), file=sys.stderr)
        sys.exit(2)
