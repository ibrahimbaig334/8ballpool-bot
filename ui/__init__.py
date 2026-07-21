# UI package initialization
import os
import sys

_UI_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_UI_DIR)

for _path in [_PROJECT_ROOT, _UI_DIR]:
    if _path not in sys.path:
        sys.path.insert(0, _path)
