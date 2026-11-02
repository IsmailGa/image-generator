import random
from io import BytesIO
from app.schemas import Kind

from PIL import Image

def _noise(width: int, height: int, seed: int):
    rng = random.Random(seed)
    return [
        (rng.randrange(256), rng.randrange(256), rng.randrange(256))
        for _ in range(width * height)
    ]

def _gradient(width: int, height: int, seed: int):
    rng = random.Random(seed)
    c1 = [rng.randrange(256) for _ in range(3)]
    c2 = [rng.randrange(256) for _ in range(3)]
    span = max(width + height - 2, 1)
    pixels = []
    for i in range(width * height):
        y, x = divmod(i, width)
        t = (x + y) / span
        pixels.append(tuple(int(a + (b - a) * t) for a, b in zip(c1, c2)))
    return pixels


def render_image(width: int, height: int, seed: int, kind: str = "noise") -> bytes:
    pixels = _gradient(width, height, seed) if kind == "gradient" else _noise(width, height, seed)
    img = Image.new("RGB", (width, height))
    img.putdata(pixels)
    buf = BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()