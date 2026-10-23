"""Input identity receipts and Windows FIFO admission for local SAM GPU jobs."""
from contextlib import contextmanager
import ctypes
from ctypes import wintypes
import hashlib
import json
import os
from pathlib import Path
import time
import uuid


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def write_json(path, value, *, exclusive=False):
    raw = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    path.parent.mkdir(parents=True, exist_ok=True)
    if exclusive:
        with path.open('xb') as stream:
            stream.write(raw)
        return
    temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    try:
        with temporary.open('xb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        deadline = time.monotonic() + 2
        while True:
            try:
                os.replace(temporary, path)
                break
            except OSError as exc:
                # A status reader on Windows can briefly deny rename/delete sharing.
                # Keep the old complete JSON visible; never truncate it as a fallback.
                if os.name != 'nt' or getattr(exc, 'winerror', None) not in (5, 32, 33) or time.monotonic() >= deadline:
                    raise
                time.sleep(.02)
    finally:
        temporary.unlink(missing_ok=True)


def snapshot_inputs(paths):
    """Hash and decode the same bytes, even if files change while the GPU is busy."""
    blobs = {role: path.read_bytes() for role, path in paths.items() if path is not None}
    records = {role: dict(path=str(paths[role]), sha256=sha256(raw), bytes=len(raw))
               for role, raw in blobs.items()}
    source_hash = records['image']['sha256']
    for role in ('mask', 'trimap'):
        if role not in blobs:
            continue
        path = paths[role]
        receipt_path = path.parent / 'result.json'
        if receipt_path.is_file():
            receipt = json.loads(receipt_path.read_text(encoding='utf-8-sig'))
            known = path.name in ('mask.png', 'segmentation-mask.png', 'raw-mask.png', 'trimap.png')
            artifact_hash = receipt.get('artifacts', {}).get(path.name)
            if (known or artifact_hash) and 'source_sha256' in receipt:
                if receipt['source_sha256'] != source_hash:
                    raise ValueError(f'{role} receipt belongs to a different source image: {path}')
                if artifact_hash and artifact_hash != records[role]['sha256']:
                    raise ValueError(f'{role} changed since its result receipt: {path}; preserve the old file')
    return blobs, records


def bind_inputs(path, records, size):
    value = dict(schema_version=1, kind='sam3-input-binding', binding_id=uuid.uuid4().hex,
                 inputs=records, size=list(size), coordinates='exif_transposed_source_pixels',
                 semantic_review='caller_responsibility')
    write_json(path, value, exclusive=True)
    return value


def verify_binding(path, records, size):
    value = json.loads(path.read_text(encoding='utf-8-sig'))
    if (value.get('schema_version') != 1 or value.get('kind') != 'sam3-input-binding'
            or not value.get('binding_id') or value.get('size') != list(size)
            or value.get('coordinates') != 'exif_transposed_source_pixels'
            or set(value.get('inputs', {})) != set(records)):
        raise ValueError('Input binding schema, roles or canvas do not match this task')
    for role, record in records.items():
        if value['inputs'][role].get('sha256') != record['sha256']:
            raise ValueError(f'Input binding mismatch: {role}; use the original files, do not rebind to bypass')
    return value['binding_id']


def _kernel():
    if os.name != 'nt':
        raise RuntimeError('SAM GPU admission currently requires Windows; CPU --mask matting is independent')
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.CreateMutexW.argtypes = [ctypes.c_void_p, wintypes.BOOL, wintypes.LPCWSTR]
    kernel.CreateMutexW.restype = wintypes.HANDLE
    kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    kernel.WaitForSingleObject.restype = wintypes.DWORD
    kernel.ReleaseMutex.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.GetProcessTimes.argtypes = [wintypes.HANDLE] + [ctypes.POINTER(wintypes.FILETIME)] * 4
    kernel.ProcessIdToSessionId.argtypes = [wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)]
    return kernel


@contextmanager
def _mutex(name, timeout):
    kernel = _kernel()
    handle = kernel.CreateMutexW(None, False, name)
    if not handle:
        raise ctypes.WinError(ctypes.get_last_error())
    acquired = False
    try:
        result = kernel.WaitForSingleObject(handle, min(0xFFFFFFFE, max(0, int(timeout * 1000))))
        if result == 258:
            raise TimeoutError('SAM GPU queue wait expired')
        if result not in (0, 128):  # WAIT_ABANDONED also grants ownership.
            raise ctypes.WinError(ctypes.get_last_error())
        acquired = True
        yield
    finally:
        if acquired:
            kernel.ReleaseMutex(handle)
        kernel.CloseHandle(handle)


def _process_birth(pid):
    kernel = _kernel()
    handle = kernel.OpenProcess(0x1000 | 0x100000, False, pid)
    if not handle:
        error = ctypes.get_last_error()
        if error == 87:
            return None
        raise ctypes.WinError(error)
    try:
        result = kernel.WaitForSingleObject(handle, 0)
        if result == 0:
            return None
        if result != 258:
            raise ctypes.WinError(ctypes.get_last_error())
        times = [wintypes.FILETIME() for _ in range(4)]
        if not kernel.GetProcessTimes(handle, *(ctypes.byref(t) for t in times)):
            raise ctypes.WinError(ctypes.get_last_error())
        return (times[0].dwHighDateTime << 32) | times[0].dwLowDateTime
    finally:
        kernel.CloseHandle(handle)


def _alive(ticket):
    try:
        birth = _process_birth(ticket['pid'])
        return birth is not None and birth == ticket['birth']
    except OSError:
        return True  # Access denied does not prove a process is dead.


def queue_root():
    session = wintypes.DWORD()
    if not _kernel().ProcessIdToSessionId(os.getpid(), ctypes.byref(session)):
        raise ctypes.WinError(ctypes.get_last_error())
    # MSIX can virtualize AppData even when addressed via an absolute profile path.
    # Stay outside AppData so packaged and ordinary clients see the same journal.
    return Path.home() / '.linn-modder' / 'sam3-queue' / f'session-{session.value}'


@contextmanager
def gpu_turn(job_id, output, timeout=900, *, root=None, on_state=None):
    """One queue across installed/source runners, before loading torch or weights.

    Windows mutexes are not FIFO; the atomic ticket journal defines admission order.
    A live slow job is never evicted by age. No external process is terminated.
    """
    root = (root or queue_root()).resolve()
    name = 'Local\\LinnModderSAM3.' + sha256(os.path.normcase(str(root)).encode())[:24]
    path = root / 'queue.json'
    started = time.monotonic()
    deadline = started + timeout
    ticket = dict(id=job_id, pid=os.getpid(), birth=_process_birth(os.getpid()), output=str(output))
    registered = False

    def update(*, register=False, remove=False):
        with _mutex(name + '.Queue', 10 if remove else max(0, deadline - time.monotonic())):
            state = json.loads(path.read_text(encoding='utf-8')) if path.exists() else dict(next_sequence=1, tickets=[])
            before = json.dumps(state, sort_keys=True)
            # Malformed journals fail closed; do not silently erase unknown owners.
            state['tickets'] = [t for t in state['tickets'] if _alive(t) and not (remove and t['id'] == job_id)]
            if register:
                ticket['sequence'] = state['next_sequence']
                state['next_sequence'] += 1
                state['tickets'].append(ticket)
            if before != json.dumps(state, sort_keys=True):
                write_json(path, state)
            return state['tickets']

    try:
        waiting = update(register=True)
        registered = True
        info = dict(status='waiting', sequence=ticket['sequence'], queue=str(path))
        if on_state:
            on_state(info)
        while not waiting or waiting[0]['id'] != job_id:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError('SAM GPU queue wait expired; inputs are preserved; retry with a new output directory')
            time.sleep(min(0.2, remaining))
            waiting = update()
        with _mutex(name + '.GPU', max(0, deadline - time.monotonic())):
            info.update(status='running', wait_seconds=round(time.monotonic() - started, 3))
            if on_state:
                on_state(info)
            yield info
    finally:
        if registered:
            update(remove=True)
