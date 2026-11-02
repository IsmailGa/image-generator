from io import BytesIO
from PIL import Image

from app.generator import render_image

def test_render_size_and_determinism():
    a = render_image(32, 20, seed=7, kind="gradient")
    b = render_image(32, 20, seed=7, kind="gradient")
    assert a == b
    assert Image.open(BytesIO(a)).size == (32, 20)

def test_gradient_differs_from_noise():
    assert render_image(16, 16, 1, "gradient") != render_image(16, 16, 1, "noise")