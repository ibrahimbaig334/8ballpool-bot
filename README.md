# 8BP Ruler - Reconstructed 8-Ball Pool Bot

8BP Ruler is an advanced predictive helper and overlay bot for **8 Ball Pool**. It works by capturing the screen, automatically detecting the table geometry and pool balls, running deep learning models for classification, and simulating high-fidelity physical trajectories of pool shots in real-time.

This repository is a reconstructed, editable Python codebase recovered from a compiled PyInstaller build.

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

## 📁 Project Architecture & Components

The application is structured into modular Python files coordinating with precompiled binary extensions:

| File                                                              | Description                                                                                                                                                   |
| :---------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **[main.py](file:///d:/Codes/Ruler/main.py)**                     | The main entry point. Sets up a single-instance mutex lock, handles startup splash screen transitions, and boots the CustomTkinter event loops.               |
| **[tk_window.py](file:///d:/Codes/Ruler/tk_window.py)**           | Manages the transparent overlay window, settings panel, login bypass GUI, keybind rebinder, pynput global listeners, and drawing primitives (circles, lines). |
| **[math_logic.py](file:///d:/Codes/Ruler/math_logic.py)**         | The central logic manager. Handles table auto-detection, ball scanning pipelines, color segmentation filters, shot searching loops, and canvas draws.         |
| **[find_paths.py](file:///d:/Codes/Ruler/find_paths.py)**         | Evaluates table geometry to calculate raw aim angles and collision coordinates for direct, cushion, and combination shots.                                    |
| **[math2.py](file:///d:/Codes/Ruler/math2.py)**                   | Standard 2D vector/geometry functions, line prolongation, perpendicular line filters, path simplification, and angle normalization routines.                  |
| **[evaluate_shots.py](file:///d:/Codes/Ruler/evaluate_shots.py)** | Scoring engine that ranks shot quality based on tactical metrics (pocket accessibility, cue positioning, blocking walls, layout openness).                    |
| **[model_use.py](file:///d:/Codes/Ruler/model_use.py)**           | ONNX Runtime wrapper. Pre-processes screen grabs (circular masking, resize, color normalization) and runs inference sessions.                                 |
| **[simulation_use.py](file:///d:/Codes/Ruler/simulation_use.py)** | Coordinates screen coordinates mapping with the simulated coordinate system (254 x 127 table units) and feeds data to the simulator.                          |
| **[splash_screen.py](file:///d:/Codes/Ruler/splash_screen.py)**   | Controls the subprocess for the launcher splash loader (active if environmental variables dictate).                                                           |
| **[keyauthx.py](file:///d:/Codes/Ruler/keyauthx.py)**             | Contains KeyAuth licensing checks (currently bypassed in the reconstructed GUI logic).                                                                        |

### Native Precompiled Extensions (Windows x64)

Because these files are compiled binaries, they must remain in the project root:

- **`simulate_core.cp39-win_amd64.pyd`**: The high-performance C++ physics engine compiled with `pybind11`.
- **`81d243bd2c585b0f4821__mypyc.cp39-win_amd64.pyd`**: Optimized performance modules compiled with `mypyc`.

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

---

## ⌨️ Controls & Keybinds

Keybinds are registered globally using `pynput`, so they trigger even when the game is active. They can be remapped inside the **⌨ Keybinds** window and are saved locally to `save_data_rulerv2_1`.

### Default Keymap

|        Key        | Action                 | Type  | Description                                                                                             |
| :---------------: | :--------------------- | :---: | :------------------------------------------------------------------------------------------------------ |
|      **`t`**      | Auto Detect Table      | Press | Calibrates the table borders by matching pockets and cushion rails.                                     |
|      **`g`**      | Move Table             | Hold  | Manually drags the table boundary box origin to the cursor position.                                    |
|      **`h`**      | Resize Table           | Hold  | Manually resizes the table boundary box by stretching it to the cursor.                                 |
|      **`x`**      | Hide/Show Table Area   | Press | Toggles visual drawing of the table boundary rectangle.                                                 |
|      **`k`**      | Detect All Balls       | Press | Scans the screen within table bounds to detect and classify all balls.                                  |
|      **`l`**      | Detect Ball on Mouse   | Press | Detects and classifies a single ball directly under the cursor.                                         |
|      **`m`**      | Move Ball near Mouse   | Hold  | Snaps the closest ball to the cursor position for manual adjustment.                                    |
|      **`j`**      | Delete Ball near Mouse | Press | Removes the ball closest to the cursor.                                                                 |
|      **`d`**      | Delete All Balls       | Press | Clears all detected balls from the overlay.                                                             |
|      **`c`**      | Direction to Mouse     | Hold  | Points the aim indicator line towards the cursor position.                                              |
| **`e`** / **`r`** | Scroll Direction       | Hold  | Nudges the target aim angle slowly to the right (`e`) or left (`r`).                                    |
| **`1`** / **`2`** | Scroll Power           | Hold  | Nudges the shot power down (`1`) or up (`2`).                                                           |
| **`3`** – **`9`** | Fixed Power Levels     | Press | Sets shot power directly: `3` (25%), `4` (37%), `5` (50%), `6` (62%), `7` (75%), `8` (88%), `9` (100%). |
|      **`o`**      | Find Shot (Solid)      | Press | Computes and selects the best scoring shot pointing at a Solid ball.                                    |
|      **`i`**      | Find Shot (Stripe)     | Press | Computes and selects the best scoring shot pointing at a Stripe ball.                                   |
|  **`Ctrl + B`**   | Lock/Unlock Keys       | Press | Locks/unlocks hotkey listeners to prevent triggers during chat typing.                                  |

### Mouse Scroll Controls

When the mouse scroll hook is enabled (🔓):

- **Scroll Wheel:** Adjusts the aim direction angle.
- **Shift + Scroll Wheel:** Adjusts the simulated shot power.
- _Scroll sensitivity can be tuned in the settings panel._

---

## ⚙️ Local Configuration (`save_data_rulerv2_1`)

At runtime, local adjustments (table size, hotkeys, styling properties) are stored in `save_data_rulerv2_1`.

- **💾 Save:** Writes current dimensions, colors, power configurations, and customized hotkeys.
- **↩ Revert:** Restores the UI to the last saved state.

---

## 📝 Decompilation & Reverse Engineering Notes

- This project was reconstructed using PyLingual.
- Known issues in decompiled logical blocks (loops, variable assignments, and matrix transformations) have been manually repaired and verified.
- **Authentication Bypass:** The network licensing validation via `keyauthx.py` is bypassed in the interface setup (`check_key` function in `tk_window.py`). Clicking the **Submit** button in the login screen immediately logs the user in with forced mock security credentials.
