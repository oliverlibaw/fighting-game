# Fighting Game

Small Flask app for generating and processing fighting game sprites.

## Setup (macOS / recommended)

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Upgrade packaging tools and install pinned dependencies:

```bash
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt -c constraints.txt
pip check
```

3. Run the app locally:

```bash
python app.py
```

Notes:
- `constraints.txt` contains conservative pins to avoid common dependency conflicts on macOS. If you need a different set (e.g., for TensorFlow or label-studio), use a separate environment.
- If `rembg` fails to import, install `onnxruntime` in the environment: `pip install onnxruntime`.
