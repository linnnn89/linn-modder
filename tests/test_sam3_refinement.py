"""Three workflow regressions; optional Comfy dependencies are never installed."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import numpy as np
from PIL import Image

SCRIPTS = Path(__file__).resolve().parents[1] / 'skills/linn-modder/asset-pipeline/scripts'
sys.path.insert(0, str(SCRIPTS))
from sam3_encoding_cache import ImageEncodingCache
from sam3_matting import apply_matting, validate_trimap


def fixture():
    # Independently known physical composite: constant foreground/background,
    # with a linear coverage ramp. Matting must recover coverage, not blur a mask.
    x = np.arange(40, dtype=np.float64)
    truth = np.broadcast_to(np.clip((22-x)/12, 0, 1), (24, 40)).copy()
    fg, bg = np.array([30, 100, 180]), np.array([230, 220, 210])
    rgb = np.rint(truth[..., None]*fg + (1-truth[..., None])*bg).astype(np.uint8)
    trimap = np.full(truth.shape, 128, dtype=np.uint8)
    trimap[truth == 1] = 255
    trimap[truth == 0] = 0
    base = (truth >= .5).astype(np.uint8)*255
    return rgb, base, trimap, truth


class SamRefinementTests(unittest.TestCase):
    @unittest.skipUnless(importlib.util.find_spec('torch') and importlib.util.find_spec('safetensors'), 'existing torch/safetensors required')
    def test_encoding_reuse_invalidates_pixels_models_and_recovers_corruption(self):
        import torch

        class Trunk(torch.nn.Module):
            embed_dim, patch_size = 3, 1

            def forward(self, images):
                return (images * 2).contiguous(memory_format=torch.channels_last)

        class Backbone(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.trunk = Trunk()

            def forward(self, images, cached_trunk=None, prompt=0):
                value = self.trunk(images) if cached_trunk is None else cached_trunk
                if not value.is_contiguous(memory_format=torch.channels_last):
                    raise AssertionError('Cache changed native convolution layout')
                return value + prompt

        backbone = Backbone()
        pixels = torch.ones(1, 3, 4, 4)
        with tempfile.TemporaryDirectory() as tmp, torch.inference_mode():
            with ImageEncodingCache(backbone, {'model': 'A'}, tmp) as first:
                self.assertTrue(torch.equal(backbone(pixels, prompt=3), pixels*2+3))
                self.assertTrue(torch.equal(backbone(pixels.clone(), prompt=7), pixels*2+7))
            self.assertEqual((first.stats['trunk_encodes'], first.stats['memory_hits']), (1, 1))
            self.assertNotIn('forward', vars(backbone))
            original_file, = Path(tmp).glob('*.safetensors')
            with ImageEncodingCache(backbone, {'model': 'A'}, tmp) as second:
                self.assertTrue(torch.equal(backbone(pixels, prompt=9), pixels*2+9))
                pixels[0, 0, 0, 0] = 5
                self.assertTrue(torch.equal(backbone(pixels), pixels*2))
            self.assertEqual((second.stats['disk_hits'], second.stats['trunk_encodes']), (1, 1))
            with ImageEncodingCache(backbone, {'model': 'B'}, tmp) as changed_model:
                backbone(torch.ones_like(pixels))
            self.assertEqual(changed_model.stats['trunk_encodes'], 1)
            original_file.write_bytes(b'corrupt cache')
            with ImageEncodingCache(backbone, {'model': 'A'}, tmp) as repaired:
                backbone(torch.ones_like(pixels))
            self.assertEqual((repaired.stats['invalid_disk_entries'], repaired.stats['trunk_encodes']), (1, 1))
        with self.assertRaisesRegex(RuntimeError, 'inference_mode'):
            with ImageEncodingCache(backbone, {}) as cache:
                backbone(pixels)
        self.assertNotIn('forward', vars(backbone))

    @unittest.skipUnless(importlib.util.find_spec('pymatting'), 'existing PyMatting required')
    def test_true_matting_recovers_coverage_and_preserves_protected_regions(self):
        rgb, base, trimap, truth = fixture()
        original = rgb.copy()
        roi = [0, 4, 40, 20]
        output, report = apply_matting(rgb, base, trimap, roi)
        unknown = validate_trimap(trimap, roi)
        np.testing.assert_array_equal(output[~unknown], base[~unknown])
        np.testing.assert_array_equal(rgb, original)
        self.assertLess(float(np.abs(output[unknown]/255-truth[unknown]).mean()), .015)
        self.assertGreater(report['changed_pixels'], 0)
        with self.assertRaisesRegex(ValueError, 'confirmed foreground'):
            validate_trimap(np.full_like(trimap, 128))
        unchanged, status = apply_matting(rgb, base, np.where(base > 0, 255, 0).astype(np.uint8))
        np.testing.assert_array_equal(unchanged, base)
        self.assertEqual(status['status'], 'skipped_no_unknown')

    @unittest.skipUnless(importlib.util.find_spec('pymatting'), 'existing PyMatting required')
    def test_matting_only_cli_reuses_mask_without_sam_and_preserves_png_contract(self):
        rgb, base, trimap, _ = fixture()
        source_alpha = np.full(base.shape, 255, dtype=np.uint8)
        source_alpha[8:10, 13:15] = 50
        source_alpha[0:3, :] = 0
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            Image.fromarray(np.dstack((rgb, source_alpha))).save(root/'source.png')
            Image.fromarray(base).save(root/'base.png')
            Image.fromarray(trimap).save(root/'trimap.png')
            originals = {name: (root/name).read_bytes() for name in ('source.png', 'base.png', 'trimap.png')}
            bind_command = [sys.executable, str(SCRIPTS/'comfy_sam3_cutout.py'), '--image', str(root/'source.png'),
                            '--mask', str(root/'base.png'), '--trimap', str(root/'trimap.png'),
                            '--bind-inputs', str(root/'inputs.json')]
            bound = subprocess.run(bind_command, capture_output=True, text=True, timeout=15)
            self.assertEqual(bound.returncode, 0, bound.stderr)
            command = [sys.executable, str(SCRIPTS/'comfy_sam3_cutout.py'), '--image', str(root/'source.png'),
                       '--mask', str(root/'base.png'), '--matting', 'pymatting', '--trimap', str(root/'trimap.png'),
                       '--input-manifest', str(root/'inputs.json'),
                       '--matting-roi', '0', '4', '40', '20', '--output', str(root/'result')]
            result = subprocess.run(command, capture_output=True, text=True, timeout=60)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report['encoding_cache']['model_loads'], 0)
            self.assertEqual(report['selection_mode'], 'existing_mask')
            saved = np.asarray(Image.open(root/'result/cutout.png'))
            mask = np.asarray(Image.open(root/'result/mask.png'))
            np.testing.assert_array_equal(saved[..., :3], rgb)
            np.testing.assert_array_equal(saved[..., 3], mask)
            self.assertTrue(np.all(mask <= source_alpha))
            protected = ~validate_trimap(trimap, [0, 4, 40, 20])
            np.testing.assert_array_equal(mask[protected], np.minimum(base, source_alpha)[protected])
            for name, data in originals.items():
                self.assertEqual((root/name).read_bytes(), data)
            result = subprocess.run(command, capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 2)
            self.assertIn('--output already exists', result.stderr)


if __name__ == '__main__':
    unittest.main()
