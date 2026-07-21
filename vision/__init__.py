# Vision package initialization
import os
import sys

_VISION_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_VISION_DIR)

for _path in [_PROJECT_ROOT, _VISION_DIR]:
    if _path not in sys.path:
        sys.path.insert(0, _path)
