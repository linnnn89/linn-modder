"""Task-local cache for ComfyUI's native cached_trunk interface; no core edits."""
from collections import OrderedDict
import hashlib
import inspect
import json
import os
from pathlib import Path
import uuid


def model_identity(comfy_root, checkpoint, dtype, torch_version, device):
    checkpoint = Path(checkpoint).resolve()
    stat = checkpoint.stat()
    code = hashlib.sha256()
    for relative in ('comfy/ldm/sam3/sam.py', 'comfy/ldm/sam3/detector.py',
                     'comfy/ldm/sam3/tracker.py', 'comfy/ops.py',
                     'comfy/model_base.py', 'comfy_extras/nodes_sam3.py'):
        code.update((Path(comfy_root) / relative).read_bytes())
    return dict(schema=1, checkpoint=str(checkpoint), size=stat.st_size,
                mtime_ns=stat.st_mtime_ns, comfy_code_sha256=code.hexdigest(),
                compute_dtype=str(dtype), torch=torch_version, device=device)


class ImageEncodingCache:
    """Reuse only image trunk tensors. Prompt, decoder and mask state stay native.

    The adapter owns a model instance in one serial CLI process. It is removed on
    exit; separate agents never share mutable Python model/prompt state. Optional
    disk entries are safetensors, keyed by actual preprocessed pixels and model
    identity, and atomically published so concurrent writers cannot truncate them.
    """

    def __init__(self, backbone, identity, directory=None, enabled=True):
        self.backbone = backbone
        self.identity = json.dumps(identity, sort_keys=True).encode()
        self.directory = Path(directory) if directory is not None else None
        self.enabled = enabled
        self.memory = OrderedDict()
        self.stats = dict(enabled=enabled, trunk_encodes=0, memory_hits=0,
                          disk_hits=0, invalid_disk_entries=0)

    def __enter__(self):
        if self.enabled and 'cached_trunk' not in inspect.signature(self.backbone.forward).parameters:
            raise RuntimeError('Native backbone lacks cached_trunk; use --no-encoding-cache '
                               'with a compatible native node or review this ComfyUI version')
        self.original = self.backbone.forward
        self.had_instance_forward = 'forward' in vars(self.backbone)
        self.signature = inspect.signature(self.original)
        self.backbone.forward = self._forward
        return self

    def __exit__(self, *exc):
        if self.had_instance_forward:
            self.backbone.forward = self.original
        else:
            del self.backbone.forward
        self.memory.clear()

    def _forward(self, *args, **kwargs):
        import torch
        bound = self.signature.bind(*args, **kwargs)
        images = bound.arguments['images']
        if bound.arguments.get('cached_trunk') is not None:
            return self.original(*args, **kwargs)
        if not self.enabled:
            self.stats['trunk_encodes'] += 1
            return self.original(*args, **kwargs)
        if torch.is_grad_enabled():
            raise RuntimeError('Image encoding cache requires torch.inference_mode()')
        # Hash contents, not data_ptr: nodes recreate tensors and may reuse storage.
        pixels = images.detach().contiguous().cpu().view(torch.uint8).numpy()
        digest = hashlib.sha256(b'sam3-trunk-layout-v2\0' + self.identity)
        digest.update(str((tuple(images.shape), str(images.dtype))).encode())
        digest.update(pixels.tobytes())
        key = digest.hexdigest()
        trunk = self.memory.pop(key, None)
        if trunk is not None:
            self.stats['memory_hits'] += 1
        elif self.directory is not None:
            entry = self.directory / (key + '.safetensors')
            if entry.is_file():
                from safetensors import safe_open, SafetensorError
                try:
                    with safe_open(str(entry), framework='pt', device='cpu') as handle:
                        metadata = handle.metadata() or {}
                        layout = metadata.get('layout')
                        if metadata.get('key') != key or layout not in ('contiguous', 'channels_last') or list(handle.keys()) != ['trunk']:
                            raise ValueError('Unexpected cache metadata')
                        trunk = handle.get_tensor('trunk')
                    expected = (images.shape[0], self.backbone.trunk.embed_dim,
                                images.shape[2] // self.backbone.trunk.patch_size,
                                images.shape[3] // self.backbone.trunk.patch_size)
                    if tuple(trunk.shape) != expected or trunk.dtype != images.dtype or not torch.isfinite(trunk).all():
                        raise ValueError('Invalid cached tensor')
                    # Native trunk returns a permuted NHWC tensor. Changing its
                    # layout can select different FP16 convolution kernels and
                    # move a few mask-boundary pixels despite identical values.
                    if layout == 'channels_last':
                        trunk = trunk.contiguous(memory_format=torch.channels_last)
                    self.stats['disk_hits'] += 1
                except (OSError, ValueError, RuntimeError, SafetensorError):
                    trunk = None
                    self.stats['invalid_disk_entries'] += 1
        if trunk is None:
            trunk = self.backbone.trunk(images)
            self.stats['trunk_encodes'] += 1
            if self.directory is not None:
                from safetensors.torch import save_file
                self.directory.mkdir(parents=True, exist_ok=True)
                entry = self.directory / (key + '.safetensors')
                temporary = self.directory / (key + '.' + uuid.uuid4().hex + '.tmp')
                if trunk.is_contiguous(memory_format=torch.channels_last):
                    layout = 'channels_last'
                elif trunk.is_contiguous():
                    layout = 'contiguous'
                else:
                    raise RuntimeError('Unsupported trunk layout; use in-memory cache without --cache-dir')
                try:
                    save_file({'trunk': trunk.detach().cpu().contiguous()}, str(temporary), metadata={'key': key, 'layout': layout})
                    os.replace(temporary, entry)
                finally:
                    if temporary.exists():
                        temporary.unlink()
        trunk = trunk.to(device=images.device, dtype=images.dtype)
        self.memory[key] = trunk
        # Whole image plus one text-refinement crop; do not grow with every object.
        while len(self.memory) > 2:
            self.memory.popitem(last=False)
        bound.arguments['cached_trunk'] = trunk
        return self.original(*bound.args, **bound.kwargs)
