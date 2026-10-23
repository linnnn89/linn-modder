"""Opt-in, trimap-constrained alpha estimation using an existing PyMatting install."""
import numpy as np
from PIL import Image


def read_mask(path, size, *, trimap=False):
    with Image.open(path) as image:
        if image.size != size or image.mode != 'L':
            raise ValueError(f'{path}: expected same-size grayscale L PNG, got {image.mode} {image.size}')
        pixels = np.asarray(image).copy()
    if trimap and not np.isin(pixels, [0, 128, 255]).all():
        raise ValueError('Trimap must contain exactly 0=background, 128=unknown, 255=opaque foreground')
    return pixels


def validate_trimap(trimap, roi=None):
    height, width = trimap.shape
    if roi is not None and not (0 <= roi[0] < roi[2] <= width and 0 <= roi[1] < roi[3] <= height):
        raise ValueError('--matting-roi must lie inside the source canvas')
    unknown = trimap == 128
    if roi is not None:
        region = np.zeros_like(unknown)
        region[roi[1]:roi[3], roi[0]:roi[2]] = True
        unknown &= region
    if unknown.any() and (not np.any(trimap == 0) or not np.any(trimap == 255)):
        raise ValueError('Trimap needs confirmed foreground and background; do not guess them from brightness')
    return unknown


def apply_matting(rgb, base_alpha, trimap, roi=None):
    """Only replace selected unknown pixels; leave all other alpha values intact."""
    from pymatting import estimate_alpha_cf
    unknown = validate_trimap(trimap, roi)
    if rgb.shape[:2] != base_alpha.shape or base_alpha.shape != trimap.shape:
        raise ValueError('Image, base alpha and trimap must share the same canvas')
    if not unknown.any():
        return base_alpha.copy(), dict(status='skipped_no_unknown', backend='pymatting_cf', changed_pixels=0)
    # Keep context for the matting Laplacian, never resize or tile arbitrarily.
    ys, xs = np.nonzero(unknown)
    h, w = trimap.shape
    x1, y1 = max(0, int(xs.min()) - 32), max(0, int(ys.min()) - 32)
    x2, y2 = min(w, int(xs.max()) + 33), min(h, int(ys.max()) + 33)
    crop_trimap = trimap[y1:y2, x1:x2]
    if not np.any(crop_trimap == 0) or not np.any(crop_trimap == 255):
        x1, y1, x2, y2 = 0, 0, w, h
        crop_trimap = trimap
    estimated = estimate_alpha_cf(
        rgb[y1:y2, x1:x2].astype(np.float64) / 255,
        crop_trimap.astype(np.float64) / 255,
        laplacian_kwargs={'epsilon': 1e-7}, cg_kwargs={'maxiter': 2000})
    if not np.isfinite(estimated).all():
        raise ValueError('Matting returned non-finite alpha; base candidate is preserved')
    candidate = np.rint(np.clip(estimated, 0, 1) * 255).astype(np.uint8)
    output = base_alpha.copy()
    selected = unknown[y1:y2, x1:x2]
    output[y1:y2, x1:x2][selected] = candidate[selected]
    if not np.array_equal(output[~unknown], base_alpha[~unknown]):
        raise AssertionError('Matting changed protected alpha')
    return output, dict(status='applied', backend='pymatting_cf',
                        solve_bbox=[x1, y1, x2, y2], roi=roi,
                        unknown_pixels=int(unknown.sum()),
                        changed_pixels=int(np.count_nonzero(output != base_alpha)),
                        protected_alpha_unchanged=True, rgb_policy='source_unchanged')
