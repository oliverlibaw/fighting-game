import os
import io
from PIL import Image, ImageDraw
from app import create_app
app = create_app({'TESTING': True})
import sprite_engine
import image_processor

# Prepare directories
upload_dir = app.config['UPLOAD_FOLDER']
result_root = app.config['RESULT_FOLDER']
if os.path.exists(upload_dir):
    pass
else:
    os.makedirs(upload_dir, exist_ok=True)
if os.path.exists(result_root):
    pass
else:
    os.makedirs(result_root, exist_ok=True)

# Create synthetic input image
input_img_path = os.path.join(upload_dir, 'test_input.png')
img = Image.new('RGBA', (128, 128), (255, 0, 0, 255))
img.save(input_img_path)

# Monkeypatch generate_action

def fake_generate_action(image_path, action_type):
    frame_w, frame_h = 64, 64
    n = 4
    strip = Image.new('RGBA', (frame_w * n, frame_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(strip)
    colors = [(255, 0, 0, 255), (0, 255, 0, 255), (0, 0, 255, 255), (255, 255, 0, 255)]
    for i, c in enumerate(colors):
        box = (i * frame_w + 8, 8, i * frame_w + frame_w - 8, frame_h - 8)
        draw.rectangle(box, fill=c)
    out_dir = os.path.join(result_root)
    os.makedirs(out_dir, exist_ok=True)
    output_path = os.path.join(out_dir, f"{action_type}_strip.png")
    strip.save(output_path)
    return output_path

sprite_engine.generate_action = fake_generate_action
print('Patched sprite_engine.generate_action for test ->', sprite_engine.generate_action)

# Remove previous output dir if exists
out_frames_dir = os.path.join(result_root, 'punch')
if os.path.exists(out_frames_dir):
    for f in os.listdir(out_frames_dir):
        os.remove(os.path.join(out_frames_dir, f))


# Run POST to the endpoint
with app.test_client() as client:
    with open(input_img_path, 'rb') as f:
        data = {'file': (io.BytesIO(f.read()), 'test_input.png')}
        resp = client.post('/process', content_type='multipart/form-data', data=data)

print('Response status:', resp.status_code)
print('Response length:', len(resp.get_data()))

if os.path.exists(out_frames_dir):
    frames = sorted(os.listdir(out_frames_dir))
    print('Frames produced:', frames)
else:
    print('No frames directory produced at', out_frames_dir)

# Print small preview of results.html if present
try:
    text = resp.get_data(as_text=True)
    print('Response preview snippet:\n', text[:400])
except Exception as e:
    print('Could not decode response body:', e)
