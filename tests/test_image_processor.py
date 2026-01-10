import os
import io
from PIL import Image, ImageDraw
import pytest
import image_processor


def make_strip(path, n=4, frame_w=64, frame_h=64):
    strip = Image.new('RGBA', (frame_w * n, frame_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(strip)
    colors = [(255, 0, 0, 255), (0, 255, 0, 255), (0, 0, 255, 255), (255, 255, 0, 255)]
    for i, c in enumerate(colors[:n]):
        box = (i * frame_w + 8, 8, i * frame_w + frame_w - 8, frame_h - 8)
        draw.rectangle(box, fill=c)
    strip.save(path)


def test_process_sprite_strip_creates_frames(tmp_path, monkeypatch):
    # Create a synthetic strip image
    strip_path = tmp_path / "strip.png"
    make_strip(str(strip_path), n=4, frame_w=64, frame_h=64)

    out_dir = tmp_path / "out"
    out_dir.mkdir()

    # Mock rembg.remove to just return the original image bytes
    def fake_remove(data_bytes):
        return data_bytes

    monkeypatch.setattr('image_processor.remove', fake_remove)

    frames = image_processor.process_sprite_strip(str(strip_path), str(out_dir))

    # Should produce 4 frames
    assert len(frames) == 4
    for f in frames:
        assert os.path.exists(f)
        img = Image.open(f)
        assert img.size == (256, 256)
