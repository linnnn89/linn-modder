"""Fixed coordinate examples; no model, GPU, or ComfyUI installation required."""
import importlib.util
from pathlib import Path
import unittest

from PIL import Image
import numpy as np

_path = Path(__file__).resolve().parents[1] / 'skills/linn-modder/asset-pipeline/scripts/sam3_geometry.py'
_spec = importlib.util.spec_from_file_location('sam3_geometry', _path)
geometry = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(geometry)


class SamGeometryTests(unittest.TestCase):
    def test_portrait_odd_padding_restores_pixels_masks_and_boxes(self):
        source = Image.new('RGB', (3, 6), (21, 42, 63))
        padded, padding = geometry.pad_to_square(source)
        self.assertEqual(padding, (1, 0, 2, 0))
        self.assertEqual(padded.crop((1, 0, 4, 6)).tobytes(), source.tobytes())
        self.assertEqual(padded.getpixel((0, 0)), (255, 255, 255))
        self.assertEqual(geometry.box_to_padded((0, 1, 3, 5), padding),
                         dict(x=1, y=1, width=3, height=4))
        mask = np.zeros((1, 6, 6), dtype=np.uint8)
        mask[:, 1:5, 1:4] = 1
        expected = np.zeros((1, 6, 3), dtype=np.uint8)
        expected[:, 1:5, :] = 1
        np.testing.assert_array_equal(geometry.mask_to_source(mask, source.size, padding), expected)
        boxes = [[dict(x=1, y=1, width=3, height=4, score=0.9)]]
        self.assertEqual(geometry.boxes_to_source(boxes, source.size, padding),
                         [[dict(x=0, y=1, width=3, height=4, score=0.9)]])

    def test_landscape_clips_detected_boxes_and_discards_padding_only_boxes(self):
        source = Image.new('RGB', (6, 3))
        _, padding = geometry.pad_to_square(source)
        self.assertEqual(padding, (0, 1, 0, 2))
        self.assertEqual(geometry.box_to_padded((1, 0, 5, 3), padding),
                         dict(x=1, y=1, width=4, height=3))
        boxes = [[dict(x=-1, y=0, width=8, height=6, score=0.8),
                  dict(x=0, y=4, width=2, height=2, score=0.7)]]
        self.assertEqual(geometry.boxes_to_source(boxes, source.size, padding),
                         [[dict(x=0, y=0, width=6, height=3, score=0.8)]])
        mask = np.arange(36).reshape(1, 6, 6)
        expected = np.array([[[6, 7, 8, 9, 10, 11], [12, 13, 14, 15, 16, 17],
                              [18, 19, 20, 21, 22, 23]]])
        np.testing.assert_array_equal(geometry.mask_to_source(mask, source.size, padding), expected)

    def test_square_is_unchanged_and_wrong_mask_size_is_rejected(self):
        source = Image.new('RGB', (3, 3), (9, 10, 11))
        padded, padding = geometry.pad_to_square(source)
        self.assertEqual(padding, (0, 0, 0, 0))
        self.assertEqual(padded.tobytes(), source.tobytes())
        mask = np.arange(9).reshape(1, 3, 3)
        np.testing.assert_array_equal(geometry.mask_to_source(mask, source.size, padding), mask)
        self.assertEqual(geometry.boxes_to_source([[]], source.size, padding), [[]])
        with self.assertRaises(ValueError):
            geometry.mask_to_source(np.zeros((1, 4, 3)), source.size, padding)


if __name__ == '__main__':
    unittest.main()
