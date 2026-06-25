# Ruler Reconstructed Source

This folder is the editable Python reconstruction of the original PyInstaller build.

## Python version

Use **Python 3.9 x64**. The native extension files in this project are named for CPython 3.9 on 64-bit Windows:

- `simulate_core.cp39-win_amd64.pyd`
- `81d243bd2c585b0f4821__mypyc.cp39-win_amd64.pyd`

Those files are not installed with `pip`. Keep them in the project root unless you rebuild the original native/C++ sources.

## Setup

Run these commands from this folder:

```powershell
py -3.9 -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

If `py -3.9` is not available, install Python 3.9 x64 first. A newer Python version will not load the included `.cp39-win_amd64.pyd` binaries.

## Required project files

These files are part of the recovered app and should stay in this tree:

- `main.py`
- `tk_window.py`
- `math_logic.py`
- `math2.py`
- `model_use.py`
- `simulation_use.py`
- `evaluate_shots.py`
- `find_paths.py`
- `keyauthx.py`
- `splash_screen.py`
- `s.ico`
- `model_ball\best.onnx`
- `model_ball\best_classifier.onnx`
- `simulate_core.cp39-win_amd64.pyd`
- `81d243bd2c585b0f4821__mypyc.cp39-win_amd64.pyd`

The app also creates `save_data_rulerv2_1` at runtime for local settings.

## Notes

`splash_screen.py` is intentionally safe in this source tree. It only launches a splash helper if `RULER_ENABLE_SPLASH=1` is set and a splash executable/script exists. This avoids startup errors when `_splash.exe` or `splash_process.py` are not present.

The recovered Python files still contain a few PyLingual header/diagnostic comments, but the known broken decompiler sections have been repaired enough for compilation. If runtime behavior looks wrong in a specific feature, compare that feature against the extracted bundle and repair that function directly.
