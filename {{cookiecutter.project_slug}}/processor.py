import numpy as np

# --- Parameter definitions ---
# Add your parameters here. The UI is generated automatically from this list.
#
# Format: (name, type, default, min, max)          for float / int
#         (name, "bool", default, None, None)       for toggle
#         (name, "enum", default, None, None, [...]) for dropdown
#
# Examples:
#   ("input_gain",  "float", 0.0,  -24.0, 24.0)
#   ("output_gain", "float", 0.0,  -24.0, 24.0)
#   ("feedback",    "float", 0.0,    0.0,  1.0)
#   ("bypass",      "bool",  False,  None, None)
#   ("mode",        "enum",  "clean", None, None, ["clean", "warm", "dirty"])

PARAMS = [
    ("input_gain",  "float", 0.0,  -24.0, 24.0),
    ("output_gain", "float", 0.0,  -24.0, 24.0),
    ("bypass",      "bool",  False, None,  None),
]

# Live state — mutated by the webview API
state: dict = {p[0]: p[2] for p in PARAMS}


def process(indata: np.ndarray, outdata: np.ndarray) -> None:
    """
    Core DSP callback. indata/outdata shape: (block_size, n_channels), float32.
    Edit this function to implement your algorithm.
    """
    if state["bypass"]:
        outdata[:] = indata
        return

    in_gain  = 10.0 ** (state["input_gain"]  / 20.0)
    out_gain = 10.0 ** (state["output_gain"] / 20.0)
    outdata[:] = indata * in_gain * out_gain
