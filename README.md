# telescope_sim

Minimal PyGame telescope simulation scaffold.

Setup
-----

1. Create and activate a virtual environment (recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python main.py
```

Files
-----

- `main.py` — application entry and main loop
- `ui.py` — small UI helper (FPS display)
- `starfield.py` — star generation and drawing
- `tracker.py` — target tracking logic
- `assets/` — place fonts/icons here

Notes
-----
This is a minimal starting point. Replace and expand the modules to add telescope-specific visuals and controls.
