import ctypes
import os
import sys
import tkinter as tk
from tkinter import messagebox
import traceback

# Setup sys.path for structured package layout
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
for path in [
    PROJECT_ROOT,
    os.path.join(PROJECT_ROOT, 'core'),
    os.path.join(PROJECT_ROOT, 'core', 'binaries'),
    os.path.join(PROJECT_ROOT, 'ui'),
    os.path.join(PROJECT_ROOT, 'vision'),
]:
    if path not in sys.path:
        sys.path.insert(0, path)

from ui import splash_screen

class SingleInstanceChecker:
    def __init__(self):
        self.mutex_name = 'Ibrahim Baig Ruler'
        self.mutex = None
    def is_already_running(self):
        ERROR_ALREADY_EXISTS = 183
        self.mutex = ctypes.windll.kernel32.CreateMutexW(None, False, self.mutex_name)
        last_error = ctypes.windll.kernel32.GetLastError()
        return last_error == ERROR_ALREADY_EXISTS
    def release_lock(self):
        if self.mutex:
            try:
                ctypes.windll.kernel32.CloseHandle(self.mutex)
                self.mutex = None
            except:
                pass

instance_checker = SingleInstanceChecker()
if instance_checker.is_already_running():
    root_temp = tk.Tk()
    root_temp.withdraw()
    messagebox.showerror('Already Running', 'Ibrahim Baig Ruler is already running!\nPlease close the existing instance first.')
    root_temp.destroy()
    sys.exit(0)

def show_error(msg):
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror('Startup Error', msg)
    root.destroy()

try:
    try:
        splash_screen.start()
        splash_screen.update(5, 'Starting up...')
        splash_screen.update(20, 'Loading UI framework...')
        import customtkinter
        splash_screen.update(40, 'Loading AI model...')
        from vision import model_use
        splash_screen.update(70, 'Loading math engine...')
        from core import math_logic
        splash_screen.update(80, 'Loading interface...')
        from ui import tk_window
        splash_screen.close()
        tk_window.app_ready = True
        tk_window.window.mainloop()
    except Exception as e:
        try:
            splash_screen.close()
        except:
            pass
        error_text = traceback.format_exc()
        print(error_text)
        show_error(f'Application failed to start:\n\n{str(e)}')
finally:
    instance_checker.release_lock()