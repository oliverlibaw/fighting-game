import os
import io
from PIL import Image, ImageDraw
from app import app
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
# Also override the reference imported into the app module (app imported generate_action at import time)
app.generate_action = fake_generate_action

# Diagnostics: show which function objects are bound
print('sprite_engine.generate_action ->', sprite_engine.generate_action)
print('app.generate_action ->', app.generate_action)
print('app globals contains generate_action?', 'generate_action' in app.__dict__)
print('app.__dict__["generate_action"] ->', app.__dict__.get('generate_action'))
print('are they same object?', app.generate_action is sprite_engine.generate_action)

# Remove previous output dir if exists
out_frames_dir = os.path.join(result_root, 'punch')
if os.path.exists(out_frames_dir):
    for f in os.listdir(out_frames_dir):
        os.remove(os.path.join(out_frames_dir, f))

# Replace the Flask view with a test-safe handler that uses our fake_generate_action
from flask import request, redirect, render_template
from werkzeug.utils import secure_filename

def fake_process():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filename = secure_filename(file.filename)
        upload_path = os.path.join(upload_dir, filename)
        file.save(upload_path)

        action_type = 'punch'
        strip_path = fake_generate_action(upload_path, action_type)

        if strip_path:
            output_dir = os.path.join(result_root, action_type)
            frames = image_processor.process_sprite_strip(strip_path, output_dir)
            frames = [os.path.join('results', os.path.basename(output_dir), os.path.basename(f)) for f in frames]
            return render_template('results.html', frames=frames)
        else:
            return "Error generating sprite sheet."

# Override the registered view function
app.view_functions['process'] = fake_process

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
