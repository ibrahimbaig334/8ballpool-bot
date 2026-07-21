# Core package initialization
import os
import sys

# Ensure core and binaries directory are in sys.path
_CORE_DIR = os.path.dirname(os.path.abspath(__file__))
_BINARIES_DIR = os.path.join(_CORE_DIR, 'binaries')
_PROJECT_ROOT = os.path.dirname(_CORE_DIR)

for _path in [_PROJECT_ROOT, _CORE_DIR, _BINARIES_DIR]:
    if _path not in sys.path:
        sys.path.insert(0, _path)
