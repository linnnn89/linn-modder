"""Selection contracts run before GPU imports; workflow uses native Bbox inputs."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / 'skills/linn-modder/asset-pipeline/scripts/comfy_sam3_cutout.py'
WORKFLOW = ROOT / 'skills/linn-modder/asset-pipeline/workflows/sam3-bbox.json'


class SamDefaultsTests(unittest.TestCase):
    def command(self, directory, *selection):
        return subprocess.run(
            [sys.executable, str(RUNNER), '--comfy', str(directory / 'missing-comfy'),
             '--checkpoint', str(directory / 'missing.safetensors'),
             '--image', str(directory / 'missing.png'), '--output', str(directory / 'output'),
             *selection], capture_output=True, text=True, timeout=15)

    def test_default_requires_subject_box_before_io(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            result = self.command(directory)
            self.assertEqual(result.returncode, 2)
            self.assertIn('Bbox is the default: supply --box X1 Y1 X2 Y2', result.stderr)
            self.assertNotIn('Traceback', result.stderr)
            self.assertEqual(list(directory.iterdir()), [])

    def test_explicit_selection_and_bad_coordinates(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            for selection in [('--box', '1', '2', '30', '40'), ('--prompt', 'person')]:
                with self.subTest(selection=selection):
                    result = self.command(directory, *selection)
                    self.assertEqual(result.returncode, 2)
                    self.assertIn('--comfy must point to an existing ComfyUI', result.stderr)
                    self.assertNotIn('Bbox is the default', result.stderr)
            result = self.command(directory, '--box', '30', '2', '1', '40')
            self.assertEqual(result.returncode, 2)
            self.assertIn('--box requires 0 <= X1 < X2', result.stderr)
            self.assertEqual(list(directory.iterdir()), [])

    def test_workflow_runs_pure_bbox_and_preserves_alpha_chain(self):
        workflow = json.loads(WORKFLOW.read_text(encoding='utf-8'))
        nodes = {node['id']: node for node in workflow['nodes']}
        links = {link[0]: link for link in workflow['links']}
        detect, = [node for node in nodes.values() if node['type'] == 'SAM3_Detect']
        inputs = {item['name']: item for item in detect['inputs']}
        self.assertIsNone(inputs['conditioning']['link'])
        bbox_link = links[inputs['bboxes']['link']]
        self.assertEqual(nodes[bbox_link[1]]['type'], 'PrimitiveBoundingBox')
        self.assertEqual(bbox_link[4], detect['inputs'].index(inputs['bboxes']))
        self.assertNotIn('CLIPTextEncode', {node['type'] for node in nodes.values()})
        join, = [node for node in nodes.values() if node['type'] == 'JoinImageWithAlpha']
        image_link = links[join['inputs'][0]['link']]
        alpha_link = links[join['inputs'][1]['link']]
        self.assertEqual(nodes[image_link[1]]['type'], 'LoadImage')
        self.assertEqual(nodes[alpha_link[1]]['type'], 'InvertMask')
        for link in links.values():
            origin, target = nodes[link[1]], nodes[link[3]]
            self.assertIn(link[0], origin['outputs'][link[2]]['links'])
            self.assertEqual(target['inputs'][link[4]]['link'], link[0])


if __name__ == '__main__':
    unittest.main()
