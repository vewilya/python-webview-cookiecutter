# python-webview-cookiecutter

A [cookiecutter](https://cookiecutter.readthedocs.io) template for spinning up a Python DSP prototyping environment, fast and convenient.

Parameters are exposed to a simple, clean webview UI automatically. DSP logic lives in a single file. No boilerplate to write, no UI to wire up — just start building.

---

## Requirements

- [uv](https://docs.astral.sh/uv/)
- [cookiecutter](https://cookiecutter.readthedocs.io) — `uv tool install cookiecutter`
- macOS or Linux

## Usage

```bash
cookiecutter gh:vewilya/python-webview-cookiecutter
cd your-project-slug
uv sync
uv run main.py
```

## What you get

- `main.py` — audio stream setup + webview launch, with optional `--record` and `--setup` flags
- `processor.py` — define your parameters and DSP logic here, nothing else needed
- `ui/index.html` — UI generated automatically from your parameter definitions
- `config.json` — saved device config, auto-prompted on first run
- `recordings/` — timestamped 24-bit WAV output via `--record`
- `.zed/tasks.json` — ready-to-run tasks for Zed editor

## Adding parameters

Open `processor.py` and edit `PARAMS`. The webview builds itself from this list at runtime:

```python
PARAMS = [
    ("input_gain",  "float", 0.0, -24.0, 24.0),
    ("feedback",    "float", 0.0,   0.0,  1.0),
    ("bypass",      "bool",  False, None, None),
]
```

Then implement your algorithm in `process()` — and that's it.
