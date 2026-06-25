# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: 'splash_screen.py'
# Bytecode version: 3.9.0beta5 (3425)
# Source timestamp: 1970-01-01 00:00:00 UTC (0)

global _proc
import subprocess
import sys
import os
import time
_proc = None
_enabled = os.environ.get('RULER_ENABLE_SPLASH') == '1'


def _get_splash_cmd():
    if hasattr(sys, '_MEIPASS'):
        splash_exe = os.path.join(sys._MEIPASS, '_splash.exe')
        return [splash_exe] if os.path.exists(splash_exe) else None

    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'splash_process.py')
    return [sys.executable, script] if os.path.exists(script) else None


def start():
    global _proc
    if not _enabled:
        return
    cmd = _get_splash_cmd()
    if not cmd:
        return
    try:
        _proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
        time.sleep(0.35)
    except Exception:
        _proc = None


def update(percent: int, message: str):
    if _proc and _proc.poll() is None:
            try:
                _proc.stdin.write(f'progress:{percent}:{message}\n'.encode())
                _proc.stdin.flush()
            except Exception:
                pass


def close():
    if _proc and _proc.poll() is None:
            try:
                _proc.stdin.write(b'close\n')
                _proc.stdin.flush()
                _proc.wait(timeout=5)
            except Exception:
                _proc.kill()
