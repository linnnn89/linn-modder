"""Real process scenarios for input provenance, FIFO GPU admission and CPU isolation."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from threading import Event, Thread
import time
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image

SCRIPTS = Path(__file__).resolve().parents[1] / 'skills/linn-modder/asset-pipeline/scripts'
sys.path.insert(0, str(SCRIPTS))
from sam3_job import bind_inputs, snapshot_inputs, verify_binding, write_json, queue_root

WORKER = r'''
import pathlib, sys, time
sys.path.insert(0, sys.argv[1])
from sam3_job import gpu_turn, write_json
root, label, timeout = pathlib.Path(sys.argv[2]), sys.argv[3], float(sys.argv[4])
try:
    with gpu_turn(label, root/label, timeout, root=root,
                  on_state=lambda state: write_json(root/(label+'.json'), state)):
        while not (root/(label+'.release')).exists():
            time.sleep(.03)
except TimeoutError:
    sys.exit(3)
'''


def wait_for(predicate, timeout=15):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(.03)
    raise AssertionError('Timed out waiting for scenario handshake')


def state(root, name):
    path = root/(name+'.json')
    return json.loads(path.read_text()).get('status') if path.exists() else None


def fixture(root, color):
    root.mkdir()
    alpha = np.zeros((24, 40), dtype=np.uint8)
    alpha[:, 10:30] = 255
    trimap = alpha.copy()
    trimap[:, 9:12] = 128
    trimap[:, 28:31] = 128
    rgb = np.full((24, 40, 3), 220, dtype=np.uint8)
    rgb[:, 10:30] = color
    Image.fromarray(rgb).save(root/'image.png')
    Image.fromarray(alpha).save(root/'base.png')
    Image.fromarray(trimap).save(root/'trimap.png')
    paths = dict(image=root/'image.png', mask=root/'base.png', trimap=root/'trimap.png')
    _, records = snapshot_inputs(paths)
    bind_inputs(root/'inputs.json', records, (40, 24))
    return paths, rgb


def command(root, output):
    return [sys.executable, str(SCRIPTS/'comfy_sam3_cutout.py'), '--image', str(root/'image.png'),
            '--mask', str(root/'base.png'), '--trimap', str(root/'trimap.png'), '--matting', 'pymatting',
            '--input-manifest', str(root/'inputs.json'), '--output', str(output), '--no-encoding-cache']


class SamJobTests(unittest.TestCase):
    def test_binding_rejects_same_size_swaps_and_retains_snapshot_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths, _ = fixture(root/'a', (80, 130, 180))
            blobs, records = snapshot_inputs(paths)
            before = dict(records['image'])
            verify_binding(root/'a/inputs.json', records, (40, 24))
            for role in ('mask', 'trimap', 'image'):
                original = paths[role].read_bytes()
                with Image.open(paths[role]) as opened:
                    pixels = np.asarray(opened).copy()
                pixels[0, 0] = 255 if role == 'trimap' else 1
                Image.fromarray(pixels).save(paths[role])
                _, changed = snapshot_inputs(paths)
                with self.assertRaisesRegex(ValueError, f'mismatch: {role}'):
                    verify_binding(root/'a/inputs.json', changed, (40, 24))
                rejected = subprocess.run(command(root/'a', root/'rejected'), capture_output=True, text=True, timeout=20)
                self.assertEqual(rejected.returncode, 2, rejected.stdout)
                self.assertIn(f'mismatch: {role}', rejected.stderr)
                self.assertFalse((root/'rejected').exists())
                paths[role].write_bytes(original)
            self.assertEqual(hashlib.sha256(blobs['image']).hexdigest(), before['sha256'])
            with self.assertRaises(FileExistsError):
                bind_inputs(root/'a/inputs.json', records, (40, 24))
            foreign = root/'foreign'
            foreign.mkdir()
            (foreign/'mask.png').write_bytes(blobs['mask'])
            write_json(foreign/'result.json', dict(source_sha256='another-image'))
            with self.assertRaisesRegex(ValueError, 'different source'):
                snapshot_inputs(dict(paths, mask=foreign/'mask.png'))

    @unittest.skipUnless(os.name == 'nt', 'Windows GPU queue')
    def test_fifo_timeout_and_crashed_owner_recovery_with_real_processes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shared_root = queue_root()
            with patch.dict(os.environ, {'LOCALAPPDATA': str(root/'private-client-cache')}):
                self.assertEqual(queue_root(), shared_root)
            self.assertTrue(shared_root.is_relative_to(Path.home()/'.linn-modder'))
            self.assertEqual(shared_root.resolve(), shared_root)
            # A real Windows reader denying delete sharing must not break job-state publication.
            receipt = root/'reader.json'
            write_json(receipt, {'state': 'old'})
            blocked = Event()
            errors = []
            real_replace = os.replace

            def observed_replace(*args):
                try:
                    return real_replace(*args)
                except PermissionError:
                    blocked.set()
                    raise

            def publish():
                try:
                    write_json(receipt, {'state': 'new'})
                except Exception as exc:
                    errors.append(exc)

            with patch('sam3_job.os.replace', side_effect=observed_replace):
                with receipt.open('rb') as reader:
                    writer = Thread(target=publish)
                    writer.start()
                    self.assertTrue(blocked.wait(2), 'Expected native Windows rename sharing conflict')
                    self.assertEqual(json.loads(reader.read()), {'state': 'old'})
                writer.join(5)
                self.assertFalse(writer.is_alive())
            self.assertEqual(errors, [])
            self.assertEqual(json.loads(receipt.read_text()), {'state': 'new'})
            processes = {}

            def start(name, timeout=15):
                processes[name] = subprocess.Popen([sys.executable, '-c', WORKER, str(SCRIPTS), str(root), name, str(timeout)],
                                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                return processes[name]

            def release(name):
                (root/(name+'.release')).touch()
                _, error = processes[name].communicate(timeout=10)
                self.assertEqual(processes[name].returncode, 0, error)

            try:
                start('A')
                wait_for(lambda: state(root, 'A') == 'running')
                start('B')
                wait_for(lambda: state(root, 'B') == 'waiting')
                start('C')
                wait_for(lambda: state(root, 'C') == 'waiting')
                timed = start('timeout', .25)
                timed.communicate(timeout=10)
                self.assertEqual(timed.returncode, 3)
                tickets = json.loads((root/'queue.json').read_text())['tickets']
                self.assertEqual([t['id'] for t in tickets], ['A', 'B', 'C'])
                release('A')
                wait_for(lambda: state(root, 'B') == 'running')
                self.assertEqual(state(root, 'C'), 'waiting')
                release('B')
                wait_for(lambda: state(root, 'C') == 'running')
                processes['C'].terminate()  # Only this test-owned exact child, while it owns the mutex.
                processes['C'].communicate(timeout=10)
                start('D')
                wait_for(lambda: state(root, 'D') == 'running')
                release('D')
                self.assertEqual(json.loads((root/'queue.json').read_text())['tickets'], [])
            finally:
                for process in processes.values():
                    if process.poll() is None:
                        process.terminate()
                    process.communicate(timeout=10)

    @unittest.skipUnless(importlib.util.find_spec('pymatting'), 'Existing PyMatting required')
    def test_parallel_cpu_jobs_bypass_gpu_and_output_collision_preserves_winner(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, rgb_a = fixture(root/'a', (30, 90, 180))
            _, rgb_b = fixture(root/'b', (160, 60, 25))
            # Exercise the actual runner while making any GPU admission call fail immediately.
            wrapper = ('import sys,runpy;sys.path.insert(0,sys.argv[1]);import sam3_job;'
                       'sam3_job.gpu_turn=lambda *a,**k:(_ for _ in ()).throw(AssertionError("CPU entered GPU queue"));'
                       'script=sys.argv[2];sys.argv=sys.argv[2:];runpy.run_path(script,run_name="__main__")')
            processes = []
            env = dict(os.environ, CUDA_VISIBLE_DEVICES='-1')
            try:
                for name in ('a', 'b'):
                    cmd = command(root/name, root/(name+'-out'))
                    processes.append(subprocess.Popen([sys.executable, '-c', wrapper, str(SCRIPTS), *cmd[1:]],
                                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env))
                for process, name, rgb in zip(processes, ('a', 'b'), (rgb_a, rgb_b)):
                    output, error = process.communicate(timeout=60)
                    self.assertEqual(process.returncode, 0, error)
                    report = json.loads(output)
                    self.assertEqual(report['gpu_queue']['status'], 'not_required')
                    self.assertEqual(report['encoding_cache']['model_loads'], 0)
                    with Image.open(root/(name+'-out')/'cutout.png') as saved:
                        np.testing.assert_array_equal(np.asarray(saved)[..., :3], rgb)
                    self.assertEqual(report['source_sha256'], hashlib.sha256((root/name/'image.png').read_bytes()).hexdigest())
                collision = [subprocess.Popen(command(root/name, root/'shared'), stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE, text=True, env=env) for name in ('a', 'b')]
                processes.extend(collision)
                results = [p.communicate(timeout=60) for p in collision]
                self.assertEqual(sorted(p.returncode for p in collision), [0, 2])
                winner = next(i for i, p in enumerate(collision) if p.returncode == 0)
                report = json.loads(results[winner][0])
                with Image.open(root/'shared/cutout.png') as saved:
                    np.testing.assert_array_equal(np.asarray(saved)[..., :3], (rgb_a, rgb_b)[winner])
                self.assertEqual(json.loads((root/'shared/job.json').read_text())['job_id'], report['job_id'])
                self.assertFalse((root/'shared/error.json').exists())
            finally:
                for process in processes:
                    if process.poll() is None:
                        process.terminate()
                    process.communicate(timeout=10)


if __name__ == '__main__':
    unittest.main()
