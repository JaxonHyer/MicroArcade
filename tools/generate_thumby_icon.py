"""Generate a 38x38 RGB565 Windows BMP launcher icon for Thumby Color."""
import struct
import sys


def rgb(r, g, b):
    return ((r & 0xf8) << 8) | ((g & 0xfc) << 3) | (b >> 3)


def make_icon(path):
    w = h = 38
    pixels = bytearray()
    # Bottom-up BGR565-compatible RGB565 sprite rows.
    for y in range(h - 1, -1, -1):
        for x in range(w):
            border = x < 2 or x >= w-2 or y < 2 or y >= h-2
            cx, cy = x-19, y-19
            if border:
                c = rgb(255, 210, 70)
            elif cx*cx + cy*cy < 110:
                c = rgb(70, 220, 255)
            else:
                c = rgb(16, 28, 70)
            # 38x38 platformer glyph: an upward arrow / bound sprite.
            if 15 <= x <= 22 and 10 <= y <= 17:
                c = rgb(255, 255, 255)
            if 17 <= x <= 20 and 6 <= y <= 14:
                c = rgb(255, 95, 120)
            pixels += struct.pack('<H', c)

    row_size = w * 2
    image_size = row_size * h
    off = 66
    size = off + image_size
    header = struct.pack('<2sIHHI', b'BM', size, 0, 0, off)
    dib = struct.pack('<IiiHHIIIIII', 52, w, h, 1, 16, 3, image_size,
                      2835, 2835, 0, 0)
    masks = struct.pack('<III', 0xf800, 0x07e0, 0x001f)
    with open(path, 'wb') as f:
        f.write(header + dib + masks + pixels)


if __name__ == '__main__':
    make_icon(sys.argv[1] if len(sys.argv) > 1 else 'icon.bmp')
