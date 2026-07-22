# Ibrahim Baig Ruler

Ibrahim Baig Ruler is an advanced predictive helper and overlay bot for **8 Ball Pool**. It works by capturing the screen, automatically detecting the table geometry and pool balls, running deep learning models for classification, and simulating high-fidelity physical trajectories of pool shots in real-time.

---

## 🚀 Key Features

- **Transparent Screen Overlay:** Interactive click-through UI drawn directly on top of the game screen using `tkinter` and `customtkinter`.
- **Automatic Table & Cushion Calibration:** Instantly detects the pool table boundaries and rail cushion coordinates using pocket-based color checks (Hough Circles) and edge-based alignment (Hough Lines).
- **AI-Powered Ball Detection & Classification:**
  - **Hough Circle Candidates:** Identifies potential ball circles on the table surface.
  - **ONNX Localization:** Infers precise sub-pixel ball centers and radii using `model_ball/best.onnx`.
  - **ONNX Classification:** Identifies ball types (`solid`, `stripe`, `black`, `cue`) using a 25x25 masked crop processed by `model_ball/best_classifier.onnx`.
- **Geometric Path-Finding Engine:** Computes shot angles for four distinct classes:
  - _Direct Shots:_ Direct path from cue ball to target to pocket.
  - _Cue Cushion (Kick) Shots:_ Cue ball bounces off one or more cushions before hitting the target.
  - _Ball Cushion (Bank) Shots:_ Target ball is bounced off a cushion into the pocket.
  - _Combination Shots:_ Cue ball hits a first ball, which collides with a second target ball to pot it.
- **High-Speed Physics Simulation:** Simulates multi-ball collisions, cushion reflections, and pocketing results using a compiled native C++ physics core (`simulate_core.pyd`).
- **Heuristic Shot Evaluator:** Scores simulated outcomes using heuristics to recommend the best shot. Metrics include line-of-sight visibility, pocket openness, cue ball placement grid coverage, wall-clumping penalties, and target ball spacing.
- **Global Inputs & Mouse Wheel Controls:** Supports scroll-wheel modifications to tune shot angle and power on the fly (with modifier keys), as well as global keyboard hotkeys that register even when the overlay window is out of focus.
- **Platform Compatibility Settings:** Toggleable modes for **PC Web** and **Phone / Emulator** versions to accommodate different table scales, force curves, and HSV color metrics.

---

## 🛠️ Installation & Setup

### Requirements

- **Operating System:** Windows x64
- **Python Version:** **Python 3.9.x (64-bit)**
  > [!IMPORTANT]
  > You must use Python 3.9.0 - 3.9.13 (64-bit). The precompiled native extensions (`.pyd` files) are locked to the Python 3.9 ABI and will fail to import on other versions.

### Setup Instructions

1.  Clone or open this folder in your terminal.
2.  Create a virtual environment using Python 3.9:
    ```powershell
    py -3.9 -m venv .venv
    ```
3.  Upgrade pip and install dependencies:
    ```powershell
    python -m pip install --upgrade pip
    .venv\Scripts\python.exe -m pip install -r requirements.txt
    ```
4.  Run the application:
    ```powershell
    .venv\Scripts\python.exe main.py
    ```

vulture . --exclude .venv,**pycache**,.ruff_cache
