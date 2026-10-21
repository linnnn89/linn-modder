"""Coordinate transforms for aspect-preserving SAM input and original-size output."""
from PIL import ImageOps


def pad_to_square(source):
    side = max(source.size)
    dx, dy = side - source.width, side - source.height
    padding = (dx // 2, dy // 2, dx - dx // 2, dy - dy // 2)
    return ImageOps.expand(source, border=padding, fill='white'), padding


def box_to_padded(box, padding):
    x1, y1, x2, y2 = box
    left, top, _, _ = padding
    return dict(x=x1 + left, y=y1 + top, width=x2 - x1, height=y2 - y1)


def mask_to_source(mask, size, padding):
    width, height = size
    left, top, right, bottom = padding
    if tuple(mask.shape[-2:]) != (height + top + bottom, width + left + right):
        raise ValueError('SAM mask size does not match padded input')
    return mask[..., top:top + height, left:left + width]


def boxes_to_source(frames, size, padding):
    width, height = size
    left, top, _, _ = padding
    restored = []
    for frame in frames:
        boxes = []
        for box in frame:
            x1, y1 = box['x'] - left, box['y'] - top
            x2, y2 = x1 + box['width'], y1 + box['height']
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(width, x2), min(height, y2)
            if x2 > x1 and y2 > y1:
                boxes.append({**box, 'x': x1, 'y': y1, 'width': x2 - x1, 'height': y2 - y1})
        restored.append(boxes)
    return restored
