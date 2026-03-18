import argparse
import json
import threading
from datetime import datetime
from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf
import webview

import processor as dsp

RECORDINGS_DIR = Path(__file__).parent / "recordings"
CONFIG_PATH    = Path(__file__).parent / "config.json"


def load_config() -> dict:
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text())
    return {"input_device": None, "input_channels": None,
            "output_device": None, "output_channels": None}


def save_config(cfg: dict) -> None:
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2))

# ── Device setup ──────────────────────────────────────────────────────────────

def list_devices() -> None:
    print("\nAvailable audio devices:")
    for i, d in enumerate(sd.query_devices()):
        tag = []
        if d["max_input_channels"] > 0:  tag.append("in")
        if d["max_output_channels"] > 0: tag.append("out")
        print(f"  [{i:2d}] {d['name']}  ({', '.join(tag)})")
    print()

def ask_device(label: str, kind: str) -> int:
    while True:
        raw = input(f"{label} device index: ").strip()
        try:
            idx = int(raw)
            d = sd.query_devices(idx)
            key = f"max_{kind}_channels"
            if d[key] < 1:
                print(f"  Device {idx} has no {kind} channels — pick another.")
                continue
            return idx
        except (ValueError, sd.PortAudioError):
            print("  Invalid index, try again.")

def ask_channels(device_idx: int, kind: str) -> int:
    d = sd.query_devices(device_idx)
    max_ch = d[f"max_{kind}_channels"]
    while True:
        raw = input(f"  Number of {kind} channels [1–{max_ch}]: ").strip()
        try:
            n = int(raw)
            if 1 <= n <= max_ch:
                return n
        except ValueError:
            pass
        print(f"  Enter a number between 1 and {max_ch}.")

# ── Audio callback ─────────────────────────────────────────────────────────────

def make_callback(n_in: int, n_out: int, record: bool):
    buf: list[np.ndarray] = []

    def callback(indata, outdata, frames, time, status):
        if status:
            print(f"[sd] {status}")
        tmp = np.zeros((frames, n_out), dtype=np.float32)
        ch = min(n_in, n_out)
        tmp[:, :ch] = indata[:, :ch]
        dsp.process(tmp, outdata)
        if record:
            buf.append(outdata.copy())

    return callback, buf

# ── Webview API ────────────────────────────────────────────────────────────────

class Api:
    def get_params(self) -> str:
        return json.dumps(dsp.PARAMS, default=str)

    def get_state(self) -> str:
        return json.dumps(dsp.state)

    def set_param(self, name: str, value) -> None:
        if name not in dsp.state:
            return
        # Find type info
        spec = next((p for p in dsp.PARAMS if p[0] == name), None)
        if spec is None:
            return
        kind = spec[1]
        if kind == "float": dsp.state[name] = float(value)
        elif kind == "int":  dsp.state[name] = int(value)
        elif kind == "bool": dsp.state[name] = bool(value)
        elif kind == "enum": dsp.state[name] = str(value)

# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", action="store_true", help="Record processed output to recordings/")
    parser.add_argument("--setup",  action="store_true", help="Force device setup and save to config.json")
    args = parser.parse_args()

    sr  = {{cookiecutter.sample_rate}}
    bs  = {{cookiecutter.block_size}}
    cfg = load_config()

    needs_setup = args.setup or any(v is None for v in cfg.values())

    if needs_setup:
        list_devices()
        cfg["input_device"]    = ask_device("Input",  "input")
        cfg["input_channels"]  = ask_channels(cfg["input_device"],  "input")
        cfg["output_device"]   = ask_device("Output", "output")
        cfg["output_channels"] = ask_channels(cfg["output_device"], "output")
        save_config(cfg)
        print("Device config saved to config.json")
    else:
        d = sd.query_devices(cfg["input_device"])
        print(f"\nUsing saved config — input: {d['name']} ({cfg['input_channels']}ch)")
        d = sd.query_devices(cfg["output_device"])
        print(f"                    output: {d['name']} ({cfg['output_channels']}ch)")
        print("Run with --setup to change devices.\n")

    in_idx, n_in   = cfg["input_device"],  cfg["input_channels"]
    out_idx, n_out = cfg["output_device"], cfg["output_channels"]

    callback, buf = make_callback(n_in, n_out, args.record)

    stream = sd.Stream(
        samplerate=sr,
        blocksize=bs,
        device=(in_idx, out_idx),
        channels=(n_in, n_out),
        dtype="float32",
        callback=callback,
    )

    html = (Path(__file__).parent / "ui" / "index.html").read_text()

    def start_stream():
        stream.start()
        msg = f"Streaming — SR {sr} Hz, block {bs}  |  {n_in}in → {n_out}out"
        if args.record:
            msg += "  |  recording... (close the webview window to stop and save)"
        print(f"\n{msg}")

    threading.Thread(target=start_stream, daemon=True).start()

    webview.create_window(
        "{{cookiecutter.project_name}}",
        html=html,
        js_api=Api(),
        width=480,
        height=520,
        resizable=True,
    )
    def save_recording():
        if args.record and buf:
            RECORDINGS_DIR.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            out_path  = RECORDINGS_DIR / f"{timestamp}.wav"
            audio     = np.concatenate(buf, axis=0)
            sf.write(out_path, audio, sr, subtype="PCM_24")
            print(f"Saved → {out_path}")

    try:
        webview.start()
    except KeyboardInterrupt:
        pass
    finally:
        stream.stop()
        save_recording()

if __name__ == "__main__":
    main()
