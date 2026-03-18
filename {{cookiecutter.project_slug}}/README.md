# {{cookiecutter.project_name}}
*{{cookiecutter.project_subtitle}}*

A minimal Python DSP prototyping environment with a live audio stream and a webview UI. Define your parameters and DSP logic in `processor.py` — everything else is wired up for you.

---

## Setup

Install dependencies with `uv`:

```bash
uv sync
```

---

## Audio Routing

This prototype streams live audio through your system using `sounddevice`. On macOS, you'll need a virtual audio device to route audio from a source (e.g. Apple Music, a DAW) into the processor.

**Recommended: BlackHole 2ch**

1. Download and install [BlackHole 2ch](https://existential.audio/blackhole/)
2. Open **Audio MIDI Setup** (found in `/Applications/Utilities/`)
3. Create a **Multi-Output Device**:
   - Click `+` → *Create Multi-Output Device*
   - Check both **BlackHole 2ch** and your regular output (e.g. MacBook Pro Speakers or your audio interface)
   - Set this Multi-Output Device as your system output in **System Settings → Sound**
4. Audio now plays through both your speakers and BlackHole simultaneously

When prompted at launch, select:
- **Input:** BlackHole 2ch
- **Output:** Your audio interface or built-in output

---

## Running

```bash
uv run dsp
```

At launch you will be prompted to:
1. Select an **input device** (e.g. BlackHole 2ch)
2. Select the number of **input channels**
3. Select an **output device** (e.g. your interface or built-in output)
4. Select the number of **output channels**

The webview UI opens automatically once the stream is running.

---

## Adding Parameters

Open `processor.py` and edit the `PARAMS` list. The UI generates itself from this list at runtime — no HTML changes needed.

```python
PARAMS = [
    ("input_gain",  "float", 0.0,  -24.0, 24.0),
    ("output_gain", "float", 0.0,  -24.0, 24.0),
    ("feedback",    "float", 0.0,    0.0,  1.0),
    ("bypass",      "bool",  False, None,  None),
    ("mode",        "enum",  "clean", None, None, ["clean", "warm", "dirty"]),
]
```

| Type | Control | Extra fields |
|---|---|---|
| `float` | Slider | `min`, `max` |
| `int` | Slider (integer steps) | `min`, `max` |
| `bool` | Toggle | — |
| `enum` | Dropdown | list of choices as 6th element |

---

## DSP Logic

Implement your algorithm in the `process()` function in `processor.py`:

```python
def process(indata: np.ndarray, outdata: np.ndarray) -> None:
    # indata / outdata shape: (block_size, n_channels), float32
    ...
```

Read parameter values from the `state` dict:

```python
gain = 10.0 ** (state["input_gain"] / 20.0)
```

`state` is updated in real time from the UI — no restart needed.

---

## Recording

To capture the processed output to a WAV file, launch with the `--record` flag:

```bash
uv run main.py --record
```

Recording runs alongside the stream — the webview UI stays open as normal. Stop with Ctrl+C and the file is saved automatically to `recordings/` as a timestamped 24-bit WAV:

```
recordings/2024-03-18_14-32-01.wav
```


---

## Project Structure

```
{{cookiecutter.project_slug}}/
├── main.py          # audio stream + webview setup
├── processor.py     # your DSP lives here
├── pyproject.toml
└── ui/
    └── index.html   # auto-generated UI — no edits needed
```
