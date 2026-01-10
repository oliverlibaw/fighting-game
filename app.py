
import os
from flask import Flask, request, render_template, url_for, redirect
from werkzeug.utils import secure_filename
import sprite_engine
from image_processor import process_sprite_strip


def create_app(test_config=None):
    """Factory to create and configure the Flask app."""
    app = Flask(__name__)

    # Default folders
    app.config.setdefault('UPLOAD_FOLDER', 'static/uploads')
    app.config.setdefault('RESULT_FOLDER', 'static/results')

    if test_config:
        app.config.update(test_config)

    # Ensure directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/process', methods=['POST'])
    def process():
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(upload_path)

            # Generate the "Punch" action sprite strip
            action_type = "punch"
            # Call the function from the module so tests can monkeypatch sprite_engine.generate_action
            strip_path = sprite_engine.generate_action(upload_path, action_type)

            if strip_path:
                # Process the sprite strip to get individual frames
                output_dir = os.path.join(app.config['RESULT_FOLDER'], action_type)
                frames = process_sprite_strip(strip_path, output_dir)
                
                # Get relative paths for display in the template
                frames = [os.path.join('results', os.path.basename(output_dir), os.path.basename(f)) for f in frames]
                
                return render_template('results.html', frames=frames)
            else:
                return "Error generating sprite sheet."

    return app


# Backwards-compatible single-app entry for simple runs
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
