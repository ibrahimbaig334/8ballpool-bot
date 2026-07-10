global slider_power
global button_table_geo_lock
global _lock_btn_ref
global slider_scroll_sens_power_var
global _cue_ind_toggle_btn
global key_tr
global slider_cue_length
global can_open_keybinds
global slider_cue_start
global show_table_bounds
global slider_ct
global slider_tr
global tr
global button_show_table
global slider_tr_var
global keys_locked
global button_scroll_lock
global cue_settings_window
global _active_line_count
global ct
global slider_scroll_sens_direction
global slider_cue_start_var
global game_version_var
global slider_ct_var
global _cue_start_coord_var
global key_save
global lt
global _active_circle_count
global button_cue_settings
global buttons_win_opened
global slider_scroll_sens_power
global slider_cue_length_var
global slider_lt_var
global _kb_listener
global _kb_paused
global slider_lt
global _shift_down
global slider_power_var
global _cue_ind_btn_var
global _cue_end_coord_var
global slider_scroll_sens_direction_var
import math
import queue
import threading
import tkinter as tk
import math_logic as ml
import pyautogui
import json
import os
import customtkinter as ctk
import ctypes
from tkinter import messagebox
import sys
from math2 import *
show_table_bounds = False
keys_locked = False
app_ready = False
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        return os.path.join(os.path.abspath('.'), relative_path)
ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('dark-blue')
BG = '#0f1117'
BG2 = '#1a1d27'
BG3 = '#22263a'
ACCENT = '#5865f2'
ACCENT2 = '#7289da'
SUCCESS = '#3ba55c'
DANGER = '#ed4245'
WARNING = '#faa61a'
TEXT = '#e3e5e8'
TEXT2 = '#a3a6aa'
BORDER = '#2f3347'
save_data_name = 'save_data_rulerv2_1'
buttons_win_opened = False
can_open_keybinds = True
ct = 2
lt = 2
tr = 9
TABLE_TAG = 'table_rect'
slider_power = slider_ct = slider_lt = slider_tr = None
slider_power_var = slider_ct_var = slider_lt_var = slider_tr_var = None
slider_scroll_sens_power = None
slider_scroll_sens_power_var = None
slider_scroll_sens_direction = None
slider_scroll_sens_direction_var = None
button_show_table = None
button_scroll_lock = None
button_table_geo_lock = None
game_version_var = None
_bar_green_btns = []
_bar_purple_btns = []
_scroll_mode_var = None
button_cue_settings = None
slider_cue_length = None
slider_cue_length_var = None
slider_cue_start = None
slider_cue_start_var = None
cue_settings_window = None
_cue_ind_btn_var = None
_cue_ind_toggle_btn = None
_cue_start_coord_var = None
_cue_end_coord_var = None
indirect_black_var = None
indirect_all_var = None
checkbox_indirect_black = None
checkbox_indirect_all = None
KEYBINDS = {
    'auto detect table': ('t', True, 'ml.detect_table'),
    'move window/table': ('g', False, 'ml.on_move_table'),
    'modify window/table size': ('h', False, 'ml.on_resize_table'),
    'hide/show table bounds': ('x', True, 'toggle_table_bounds'),
    'detect all balls': ('k', True, 'ml.detect_balls'),
    'detect ball near mouse': ('l', True, 'ml.detect_ball_on_mouse'),
    'move ball near mouse': ('m', False, 'ml.move_ball_near_mouse'),
    'delete ball near mouse': ('j', True, 'ml.delete_ball_near_mouse'),
    'delete all balls': ('d', True, 'ml.delete_all_balls'),
    'direction to mouse': ('c', False, 'ml.direction_to_mouse'),
    'direction scroll left': ('r', False, '_adj_direction_angle_left'),
    'direction scroll right': ('e', False, '_adj_direction_angle_right'),
    'power down': ('1', False, '_adj_power_down'),
    'power up': ('2', False, '_adj_power_up'),
    'power 25%': ('3', True, '_set_power_25'),
    'power 37%': ('4', True, '_set_power_37'),
    'power 50%': ('5', True, '_set_power_50'),
    'power 62%': ('6', True, '_set_power_62'),
    'power 75%': ('7', True, '_set_power_75'),
    'power 88%': ('8', True, '_set_power_88'),
    'power 100%': ('9', True, '_set_power_100'),
    'find shot stripe': ('i', True, 'ml.find_shot_stripe'),
    'find shot solid': ('o', True, 'ml.find_shot_solid'),
    'auto aim': ('a', True, 'auto_aim'),
    'auto shoot': ('s', True, 'auto_shoot'),
}
def _set_power(value):
    ml.power_cue = max(0.0, min(1.0, value))
    if slider_power is not None:
        slider_power.set(ml.power_cue)
        slider_power_var.set(f'{ml.power_cue:.2f}')
    ml.need_update_draws = True
def _adj_power(delta):
    _set_power(ml.power_cue + delta)
def _adj_direction_angle(delta):
    ml.prediction_angle = update_angle(ml.prediction_angle, delta)
    ml.need_update_draws = True
def _set_power_25():
    _set_power(0.25)
def _set_power_37():
    _set_power(0.37)
def _set_power_50():
    _set_power(0.5)
def _set_power_62():
    _set_power(0.62)
def _set_power_75():
    _set_power(0.75)
def _set_power_88():
    _set_power(0.88)
def _set_power_100():
    _set_power(1.0)
power_sens_scaler = 0.01
direction_sens_scaler = 0.002
def _adj_power_down():
    _adj_power(-ml.mouse_scroll_sensitivity_power * power_sens_scaler / 4)
def _adj_power_up():
    _adj_power(ml.mouse_scroll_sensitivity_power * power_sens_scaler / 4)
def _adj_direction_angle_left():
    _adj_direction_angle(ml.mouse_scroll_sensitivity_direction * direction_sens_scaler / 4)
def _adj_direction_angle_right():
    _adj_direction_angle(-ml.mouse_scroll_sensitivity_direction * direction_sens_scaler / 4)
def set_scroll_off():
    """Disable mouse scroll."""
    ml.mouse_scroll_mode = 'off'
    _sync_scroll_lock_btn()
def set_scroll_on():
    """Enable mouse scroll."""
    ml.mouse_scroll_mode = 'on'
    _sync_scroll_lock_btn()
def set_scroll_power():
    """Compatibility alias: enable mouse scroll."""
    set_scroll_on()
def set_scroll_direction():
    """Compatibility alias: enable mouse scroll."""
    set_scroll_on()
_shift_down = False
def _sync_scroll_lock_btn():
    if button_scroll_lock is None:
        return None
    else:
        if str(ml.mouse_scroll_mode).lower()!= 'on':
            button_scroll_lock.configure(text='🔒', fg_color=DANGER, hover_color='#b03032', text_color='white')
        else:
            button_scroll_lock.configure(text='🔓', fg_color=BG3, hover_color=BORDER, text_color=TEXT2)
def _start_scroll_listener():
    from pynput import keyboard as pynput_keyboard
    from pynput import mouse as pynput_mouse
    def on_press(key):
        global _shift_down
        try:
            if key in [pynput_keyboard.Key.shift, pynput_keyboard.Key.shift_l, pynput_keyboard.Key.shift_r]:
                _shift_down = True
        except Exception:
            pass
    def on_release(key):
        global _shift_down
        try:
            if key in [pynput_keyboard.Key.shift, pynput_keyboard.Key.shift_l, pynput_keyboard.Key.shift_r]:
                _shift_down = False
        except Exception:
            pass
    def on_scroll(x, y, dx, dy):
        if not app_ready:
            return None
        else:
            if keys_locked or str(ml.mouse_scroll_mode).lower()!= 'on':
                return None
            else:
                if _shift_down:
                    canvas.after(0, lambda: _adj_power(dy * ml.mouse_scroll_sensitivity_power * power_sens_scaler))
                else:
                    canvas.after(0, lambda: _adj_direction_angle(dy * ml.mouse_scroll_sensitivity_direction * direction_sens_scaler))
    kb_listener = pynput_keyboard.Listener(on_press=on_press, on_release=on_release)
    kb_listener.daemon = True
    kb_listener.start()
    mouse_listener = pynput_mouse.Listener(on_scroll=on_scroll)
    mouse_listener.daemon = True
    mouse_listener.start()
_start_scroll_listener()
default_keybinds = {a: v[0] for a, v in KEYBINDS.items()}
keybinds = dict(default_keybinds)
key_behavior = {a: v[1] for a, v in KEYBINDS.items()}
_kb_queue = queue.SimpleQueue()
_kb_paused = False
_kb_hook = None
_kb_listener = None
_kb_held_keys = set()
_kb_toggled_down = set()
def _key_name_from_pynput(key):
    try:
        if hasattr(key, 'char') and key.char is not None:
            return key.char.lower()
        name = getattr(key, 'name', None)
        if name:
            name = name.lower()
            numpad_map = {'kp_0': '0', 'kp_1': '1', 'kp_2': '2', 'kp_3': '3', 'kp_4': '4', 'kp_5': '5', 'kp_6': '6', 'kp_7': '7', 'kp_8': '8', 'kp_9': '9', 'kp_enter': 'enter', 'kp_decimal': '.'}
            return numpad_map.get(name, name)
        vk = getattr(key, 'vk', None)
        if vk is not None:
            vk_map = {96: '0', 97: '1', 98: '2', 99: '3', 100: '4', 101: '5', 102: '6', 103: '7', 104: '8', 105: '9'}
            if vk in vk_map:
                return vk_map[vk]
    except Exception:
        pass
    return None
def _start_keyboard_listener():
    """\n    Global keyboard listener that works without window focus.\n      - toggle keys → fire once per press\n      - hold keys → fire while held\n    """
    global _kb_listener
    from pynput import keyboard as pynput_keyboard
    import time
    def on_press(key):
        global _shift_down
        try:
            _vk = getattr(key, 'vk', None)
            if _vk == 66 and ('ctrl_l' in _kb_held_keys or 'ctrl_r' in _kb_held_keys or 'ctrl' in _kb_held_keys):
                _kb_queue.put('__toggle_lock__')
                return
        except Exception:
            pass
        key_name = _key_name_from_pynput(key)
        if not key_name:
            return None
        else:
            _kb_held_keys.add(key_name)
            if key_name in ['shift', 'shift_l', 'shift_r']:
                _shift_down = True
            if _kb_paused or keys_locked:
                return None
            else:
                for action, bound_key in keybinds.items():
                    if key_name!= bound_key:
                        continue
                    else:
                        if key_behavior.get(action, False) and key_name not in _kb_toggled_down:
                                _kb_toggled_down.add(key_name)
                                _kb_queue.put(bound_key.lower())
                        break
    def on_release(key):
        global _shift_down
        key_name = _key_name_from_pynput(key)
        if not key_name:
            return None
        else:
            _kb_held_keys.discard(key_name)
            _kb_toggled_down.discard(key_name)
            if key_name in ['shift', 'shift_l', 'shift_r']:
                _shift_down = False
    def _listener_loop():
        while True:
            if not _kb_paused and not keys_locked:
                for action, bound_key in keybinds.items():
                    if not key_behavior.get(action, False) and bound_key.lower() in _kb_held_keys:
                        _kb_queue.put(bound_key.lower())
            time.sleep(0.03)
    _kb_listener = pynput_keyboard.Listener(on_press=on_press, on_release=on_release)
    _kb_listener.daemon = True
    _kb_listener.start()
    t = threading.Thread(target=_listener_loop, daemon=True)
    t.start()
def _poll_kb_queue():
    """Drain the keyboard queue and dispatch actions. Runs on the main thread."""
    try:
        while True:
            key = _kb_queue.get_nowait()
            _dispatch_keybind(key)
    except queue.Empty:
        pass
    if buttons_win_opened:
        canvas.after(30, _poll_kb_queue)
def _abs(rx, ry):
    return (int(round(ml.table_left + rx)), int(round(ml.table_top + ry)))
_circle_pool = []
_line_pool = []
_active_circle_count = 0
_active_line_count = 0
def draw_line(pt1, pt2, color=(255, 255, 255), dots=False):
    global _active_line_count
    rgb = f'#{int(color[0]):02x}{int(color[1]):02x}{int(color[2]):02x}'
    ax1, ay1 = _abs(pt1[0], pt1[1])
    ax2, ay2 = _abs(pt2[0], pt2[1])
    if dots:
        dx, dy = (ax2 - ax1, ay2 - ay1)
        length = math.hypot(dx, dy)
        steps = max(1, int(length / 20))
        for i in range(steps + 1):
            x = ax1 + dx * i / steps
            y = ay1 + dy * i / steps
            draw_circle((x - ml.table_left, y - ml.table_top), 1, color)
    else:
        if _active_line_count < len(_line_pool):
            line_id = _line_pool[_active_line_count]
            canvas.coords(line_id, ax1, ay1, ax2, ay2)
            canvas.itemconfig(line_id, fill=rgb, width=int(round(lt)), state='normal')
        else:
            line_id = canvas.create_line(ax1, ay1, ax2, ay2, fill=rgb, width=int(round(lt)))
            _line_pool.append(line_id)
        _active_line_count += 1
def draw_circle(center, radius, color=(255, 255, 255)):
    global _active_circle_count
    rgb = f'#{int(color[0]):02x}{int(color[1]):02x}{int(color[2]):02x}'
    ax, ay = _abs(center[0], center[1])
    r = int(round(radius))
    if _active_circle_count < len(_circle_pool):
        circle_id = _circle_pool[_active_circle_count]
        canvas.coords(circle_id, ax - r, ay - r, ax + r, ay + r)
        canvas.itemconfig(circle_id, outline=rgb, width=int(round(ct)), state='normal')
    else:
        circle_id = canvas.create_oval(ax - r, ay - r, ax + r, ay + r, outline=rgb, width=int(round(ct)))
        _circle_pool.append(circle_id)
    _active_circle_count += 1
def draw_pixel(x, y, color=(255, 255, 255)):
    rgb = f'#{int(color[0]):02x}{int(color[1]):02x}{int(color[2]):02x}'
    ax, ay = _abs(x, y)
    canvas.create_rectangle(ax, ay, ax + 1, ay + 1, outline=rgb, fill=rgb, tags='temp_drawing')
def draw_filled_circle(center, radius, color=(255, 255, 255)):
    rgb = f'#{int(color[0]):02x}{int(color[1]):02x}{int(color[2]):02x}'
    ax, ay = _abs(center[0], center[1])
    r = int(round(radius))
    canvas.create_oval(ax - r, ay - r, ax + r, ay + r, outline=rgb, width=2, fill=rgb, tags='temp_drawing')
def _draw_table_rect():
    if show_table_bounds:
        x0 = int(round(ml.table_left))
        y0 = int(round(ml.table_top))
        x1 = int(round(ml.table_left + ml.table_width))
        y1 = int(round(ml.table_top + ml.table_height))
        canvas.create_rectangle(x0, y0, x1, y1, outline='white', width=2, tags=TABLE_TAG)
def delete_all_drawings():
    delete_all_drawings_no_updt()
    canvas.update_idletasks()
def delete_all_drawings_no_updt():
    global _active_line_count
    global _active_circle_count
    _active_circle_count = 0
    _active_line_count = 0
    for item_id in _circle_pool:
        canvas.itemconfig(item_id, state='hidden')
    for item_id in _line_pool:
        canvas.itemconfig(item_id, state='hidden')
    canvas.delete('temp_drawing')
    canvas.delete(TABLE_TAG)
def update_canvas_():
    canvas.update_idletasks()
def toggle_table_bounds():
    global show_table_bounds
    show_table_bounds = not show_table_bounds
    _refresh_show_table_btn()
    delete_all_drawings()
def _refresh_show_table_btn():
    if button_show_table is None:
        return None
    else:
        on = not show_table_bounds
def _sync_show_table_btn():
    """Called after ml.update() so the button reflects the real flag."""
    if button_show_table is None:
        return None
    else:
        if show_table_bounds:
            button_show_table.configure(text='Show table area  ●', fg_color=SUCCESS, hover_color='#2d8a4e')
        else:
            button_show_table.configure(text='Show table area  ○', fg_color=BG3, hover_color=BORDER)
def _sync_table_geo_lock_btn():
    if button_table_geo_lock is None:
        return None
    else:
        if ml.lock_table_geo:
            button_table_geo_lock.configure(text='🔒', fg_color=DANGER, hover_color='#b03032', text_color='white')
        else:
            button_table_geo_lock.configure(text='🔓', fg_color=BG3, hover_color=BORDER, text_color=TEXT2)
def update_window():
    """Main render loop."""
    if show_table_bounds and not canvas.find_withtag(TABLE_TAG):
        _draw_table_rect()
    ml.update(draw_circle, draw_line)
    _sync_show_table_btn()
    canvas.after(80, update_window)

def _keep_overlay_topmost():
    try:
        window.wm_attributes('-topmost', True)
    finally:
        canvas.after(1000, _keep_overlay_topmost)
def _current_data():
    return {
        'table_left': ml.table_left,
        'table_top': ml.table_top,
        'table_width': ml.table_width,
        'table_height': ml.table_height,
        'ct': ct,
        'lt': lt,
        'tr': tr,
        'power_cue': ml.power_cue,
        'show_table_bounds': show_table_bounds,
        'lock_table_geo': ml.lock_table_geo,
        'game_version': ml.game_version,
        'keybinds': keybinds,
        'transparency': key_tr,
        'cue_force_green': ml.cue_force_green,
        'cue_force_purple': ml.cue_force_purple,
        'mouse_scroll_mode': ml.mouse_scroll_mode,
        'mouse_scroll_sensitivity_power': ml.mouse_scroll_sensitivity_power,
        'mouse_scroll_sensitivity_direction': ml.mouse_scroll_sensitivity_direction,
        'save': key_save,
        'cue_length_scaler': ml.cue_length_scaler,
        'cue_start_scaler': ml.cue_start_scaler,
        'power_indicator_start': getattr(ml, 'power_indicator_start', [0.0, 0.0]),
        'power_indicator_end': getattr(ml, 'power_indicator_end', [0.0, 0.0]),
        'indicate_power': getattr(ml, 'indicate_power', False),
        'indirect_black': ml.indirect_black,
        'indirect_all': ml.indirect_all,
    }
def save_():
    with open(save_data_name, 'w') as f:
        json.dump(_current_data(), f)
    print('data saved')
def reset():
    global lt
    global ct
    global tr
    if not os.path.exists(save_data_name):
        return None
    else:
        with open(save_data_name) as f:
            data = json.load(f)
    ml.table_left = data.get('table_left', ml.table_left)
    ml.table_top = data.get('table_top', ml.table_top)
    ml.table_width = data.get('table_width', ml.table_width)
    ml.table_height = data.get('table_height', ml.table_height)
    ml.update_radius()
    ct = data.get('ct', ct)
    lt = data.get('lt', lt)
    tr = data.get('tr', tr)
    ml.power_cue = data.get('power_cue', ml.power_cue)
    ml.cue_force_green = data.get('cue_force_green', ml.cue_force_green)
    ml.cue_force_purple = data.get('cue_force_purple', ml.cue_force_purple)
    ml.show_table_bounds = data.get('show_table_bounds', True)
    ml.lock_table_geo = data.get('lock_table_geo', False)
    ml.game_version = data.get('game_version', 0)
    ml.mouse_scroll_mode = 'on' if str(data.get('mouse_scroll_mode', 'off')).lower()!= 'off' else 'off'
    ml.mouse_scroll_sensitivity_power = data.get('mouse_scroll_sensitivity_power', data.get('mouse_scroll_sensitivity', 0.2))
    ml.mouse_scroll_sensitivity_direction = data.get('mouse_scroll_sensitivity_direction', data.get('mouse_scroll_sensitivity', 0.2))
    ml.cue_length_scaler = data.get('cue_length_scaler', ml.cue_length_scaler)
    ml.cue_start_scaler = data.get('cue_start_scaler', ml.cue_start_scaler)
    ml.power_indicator_start = data.get('power_indicator_start', getattr(ml, 'power_indicator_start', [0.0, 0.0]))
    ml.power_indicator_end = data.get('power_indicator_end', getattr(ml, 'power_indicator_end', [0.0, 0.0]))
    ml.indicate_power = data.get('indicate_power', getattr(ml, 'indicate_power', False))
    ml.indirect_black = data.get('indirect_black', False)
    ml.indirect_all = data.get('indirect_all', False)
    if 'keybinds' in data:
        filtered = {k: v for k, v in data['keybinds'].items() if k in KEYBINDS}
        keybinds.update(filtered)
    window.wm_attributes('-alpha', tr * 0.1)
    _refresh_sliders()
    _sync_show_table_btn()
    print('reverted to saved data')
    refresh_cue_sliders()
def refresh_cue_sliders():
    if cue_settings_window is not None and cue_settings_window.winfo_exists():
            if slider_cue_length is not None:
                slider_cue_length.set(ml.cue_length_scaler)
            if slider_cue_length_var is not None:
                slider_cue_length_var.set(f'{ml.cue_length_scaler:.3f}')
            if slider_cue_start is not None:
                slider_cue_start.set(ml.cue_start_scaler)
            if slider_cue_start_var is not None:
                slider_cue_start_var.set(f'{ml.cue_start_scaler:.3f}')
            _on = getattr(ml, 'indicate_power', False)
            if _cue_ind_btn_var is not None:
                _cue_ind_btn_var.set('● ON' if _on else '○ OFF')
            if _cue_ind_toggle_btn is not None:
                try:
                    _cue_ind_toggle_btn.configure(fg_color=SUCCESS if _on else BG3, hover_color='#2d8a4e' if _on else BORDER)
                except Exception:
                    pass
            if _cue_start_coord_var is not None:
                s = getattr(ml, 'power_indicator_start', [0.0, 0.0])
                try:
                    _cue_start_coord_var.set(f'{float(s[0]):.1f},  {float(s[1]):.1f}')
                except Exception:
                    _cue_start_coord_var.set('—')
            if _cue_end_coord_var is not None:
                e = getattr(ml, 'power_indicator_end', [0.0, 0.0])
                try:
                    _cue_end_coord_var.set(f'{float(e[0]):.1f},  {float(e[1]):.1f}')
                except Exception:
                    _cue_end_coord_var.set('—')
def _refresh_sliders():
    try:
        if slider_power is not None:
            slider_power.set(ml.power_cue)
            slider_power_var.set(f'{ml.power_cue:.2f}')
        if slider_ct is not None:
            slider_ct.set(ct)
            slider_ct_var.set(str(int(ct)))
        if slider_lt is not None:
            slider_lt.set(lt)
            slider_lt_var.set(str(int(lt)))
        if slider_tr is not None:
            slider_tr.set(tr)
            slider_tr_var.set(str(int(tr)))
        if slider_scroll_sens_power is not None:
            slider_scroll_sens_power.set(ml.mouse_scroll_sensitivity_power)
            slider_scroll_sens_power_var.set(f'{ml.mouse_scroll_sensitivity_power:.2f}')
        if slider_scroll_sens_direction is not None:
            slider_scroll_sens_direction.set(ml.mouse_scroll_sensitivity_direction)
            slider_scroll_sens_direction_var.set(f'{ml.mouse_scroll_sensitivity_direction:.2f}')
    except Exception:
        pass
    if game_version_var is not None:
        game_version_var.set(ml.game_version)
    if indirect_black_var is not None:
        indirect_black_var.set(ml.indirect_black)
    if indirect_all_var is not None:
        indirect_all_var.set(ml.indirect_all)
    _sync_scroll_lock_btn()
    _sync_scroll_lock_btn()
    _sync_table_geo_lock_btn()
    _refresh_force_bars()
    ml.need_update_draws = True
def _refresh_force_bars():
    """Repaint both bar rows to match current ml values."""
    for i, btn in enumerate(_bar_green_btns):
        active = i + 1 <= ml.cue_force_green
        btn.configure(fg_color='#3ba55c' if active else '#22263a', hover_color='#2d8a4e' if active else '#2f3347')
    for i, btn in enumerate(_bar_purple_btns):
        active = i + 1 <= ml.cue_force_purple
        btn.configure(fg_color='#9b59b6' if active else '#22263a', hover_color='#7d3c98' if active else '#2f3347')
def _autosave_keybinds():
    try:
        if os.path.exists(save_data_name):
            with open(save_data_name) as f:
                data = json.load(f)
        else:
            data = _current_data()
        data['keybinds'] = keybinds
        with open(save_data_name, 'w') as f:
            json.dump(data, f)
        print('keybinds auto-saved')
    except Exception as e:
        print('keybind autosave failed:', e)
def _dispatch_keybind(key):
    """Map a key name to its action and execute it. Runs on the main thread."""
    if key == '__toggle_lock__':
        _toggle_lock_from_keybind()
        return None
    else:
        for action, bound_key in keybinds.items():
            if key == bound_key:
                _run_action(action)
                break
def _toggle_lock_from_keybind():
    """Called from Ctrl+B — invokes the same toggle_lock that lock_btn uses."""
    global keys_locked
    keys_locked = not keys_locked
    try:
        if keys_locked:
            _lock_btn_ref.configure(text='🔒', fg_color=DANGER, hover_color='#b03032', text_color='white')
        else:
            _lock_btn_ref.configure(text='🔓', fg_color=BG3, hover_color=BORDER, text_color=TEXT2)
    except Exception:
        pass
_lock_btn_ref = None
def _run_action(action):
    """Resolve the handler name from KEYBINDS and call it."""
    if action!= 'powers path':
        ml.powers_hover = False
    handler_name = KEYBINDS[action][2]
    if handler_name.startswith('ml.'):
        if _shift_down and handler_name[3:] in ['find_shot_stripe', 'find_shot_solid']:
            ml.find_shot_black()
        else:
            fn = getattr(ml, handler_name[3:])
            fn()
    else:
        globals()[handler_name]()

def auto_aim():
    if ml.cue_ball is None:
        print("Auto-aim: No cue ball detected.")
        return
    
    # Calculate screen coordinates of the cue ball
    cue_x = ml.table_left + ml.cue_ball[0][0]
    cue_y = ml.table_top + ml.cue_ball[0][1]
    angle = ml.prediction_angle
    
    target_x = None
    target_y = None
    
    # Try to find the exact midpoint of the predicted line segment
    if ml.predictions is not None and len(ml.predictions) > 0:
        balls_data = ml.predictions[0]
        for b_data in balls_data:
            if b_data.get('id') == -2:  # Cue ball ID
                path = b_data.get('path', [])
                if len(path) >= 2:
                    p0 = path[0]
                    p1 = path[1]
                    target_x = ml.table_left + p0[0] + (p1[0] - p0[0]) / 2.0
                    target_y = ml.table_top + p0[1] + (p1[1] - p0[1]) / 2.0
                    break
                    
    # Fallback to a fixed distance along the prediction angle if path is not available
    if target_x is None or target_y is None:
        dist = 120.0
        target_x = cue_x + math.cos(angle) * dist
        target_y = cue_y + math.sin(angle) * dist
        
    # Clamp to screen boundary to be safe
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    target_x = max(10, min(screen_width - 10, target_x))
    target_y = max(10, min(screen_height - 10, target_y))
    
    print(f"Auto-aim: Tapping at center of predicted line: ({target_x:.1f}, {target_y:.1f})")
    
    # Perform the click
    import time
    from pynput.mouse import Button, Controller
    mouse = Controller()
    
    # Save current position
    orig_pos = mouse.position
    
    # Move to target position
    mouse.position = (int(target_x), int(target_y))
    time.sleep(0.1)
    
    # Press and release
    mouse.press(Button.left)
    time.sleep(0.1)
    mouse.release(Button.left)
    time.sleep(0.1)
    
    # Restore original position
    mouse.position = orig_pos

def auto_shoot():
    start_coord = getattr(ml, 'power_indicator_start', [0.0, 0.0])
    end_coord = getattr(ml, 'power_indicator_end', [0.0, 0.0])
    
    if not isinstance(start_coord, (list, tuple)) or len(start_coord) < 2 or not isinstance(end_coord, (list, tuple)) or len(end_coord) < 2 or start_coord == [0.0, 0.0] or end_coord == [0.0, 0.0]:
        print("Auto-shoot: Power indicator not calibrated.")
        return
        
    # Calculate target coordinate along the power bar
    power = ml.power_cue
    target_x = start_coord[0] + (end_coord[0] - start_coord[0]) * power
    target_y = start_coord[1] + (end_coord[1] - start_coord[1]) * power
    
    print(f"Auto-shoot: Dragging from ({start_coord[0]:.1f}, {start_coord[1]:.1f}) to ({target_x:.1f}, {target_y:.1f}) for power {power:.2f}")
    
    import time
    from pynput.mouse import Button, Controller
    mouse = Controller()
    
    # Save current position
    orig_pos = mouse.position
    
    # Move to start of power indicator
    mouse.position = (int(start_coord[0]), int(start_coord[1]))
    time.sleep(0.2)
    
    # Press
    mouse.press(Button.left)
    time.sleep(0.2)
    
    # Drag in steps
    steps = 25
    for i in range(1, steps + 1):
        t = i / steps
        curr_x = start_coord[0] + (target_x - start_coord[0]) * t
        curr_y = start_coord[1] + (target_y - start_coord[1]) * t
        mouse.position = (int(curr_x), int(curr_y))
        time.sleep(0.01)
        
    # Hold for 0.5 seconds to ensure pixel accuracy and game registration
    time.sleep(0.5)
    
    # Release to shoot
    mouse.release(Button.left)
    time.sleep(0.1)
    
    # Restore original position
    mouse.position = orig_pos

def close_():
    os._exit(1)
def callback():
    os._exit(1)
key_save = 'Bypass_Active'
key_tr = 0.112
def create_keys_window():
    global can_open_keybinds
    if not can_open_keybinds:
        return None
    else:
        can_open_keybinds = False
        kw = ctk.CTkToplevel()
        kw.title('Keybinds')
        kw.after(201, lambda: kw.iconbitmap(resource_path('s.ico')))
        kw.attributes('-topmost', True)
        kw.resizable(False, False)
        kw.configure(fg_color=BG)
        listening_for = [None]
        row_widgets = {}
        def _on_ready():
            kw.unbind('<Map>')
            kw.after(100, _on_ready2)
            kw.deiconify()
        def _on_ready2():
            kw.attributes('-topmost', True)
            kw.lift()
            kw.focus_force()
        hdr = ctk.CTkFrame(kw, fg_color=BG, corner_radius=0)
        hdr.pack(fill='x', padx=16, pady=(8, 0))
        ctk.CTkLabel(hdr, text='ACTION', font=ctk.CTkFont('Segoe UI', 10, 'bold'), text_color=TEXT2, width=220, anchor='w').pack(side='left')
        ctk.CTkLabel(hdr, text='KEY', font=ctk.CTkFont('Segoe UI', 10, 'bold'), text_color=TEXT2, width=80, anchor='center').pack(side='left', padx=4)
        scroll = ctk.CTkScrollableFrame(kw, fg_color=BG, scrollbar_button_color=BG3, scrollbar_button_hover_color=BORDER, width=430, height=520)
        scroll.pack(fill='both', expand=True, padx=12, pady=4)
        def refresh_rows():
            for action, (klbl, _) in row_widgets.items():
                klbl.configure(text=f'  {keybinds[action].upper()}  ')
        def start_listening(action, btn):
            global _kb_paused
            if listening_for[0] is not None:
                _, old = row_widgets[listening_for[0]]
                old.configure(text='Change', fg_color=BG3, hover_color=BORDER, text_color=TEXT2)
            listening_for[0] = action
            _kb_paused = True
            btn.configure(text='● press', fg_color=WARNING, hover_color=WARNING, text_color=BG)
            status_var.set(f'Listening  ›  {action}   (Esc = cancel)')
            kw.focus_set()
        def _stop_listening(btn):
            global _kb_paused
            listening_for[0] = None
            _kb_paused = False
        def on_key(event):
            nonlocal listening_for
            action = listening_for[0]
            if action is None:
                return None
            key_name = event.keysym.lower()
            _, active_btn = row_widgets[action]
            if key_name == 'escape':
                active_btn.configure(text='Change', fg_color=BG3, hover_color=BORDER, text_color=TEXT2)
                _stop_listening(active_btn)
                refresh_rows()
                status_var.set('Cancelled.')
                return None
            conflict = [a for a, k in keybinds.items() if k == key_name and a != action]
            if conflict:
                status_var.set(f"Warning: '{key_name.upper()}' already used by '{conflict[0]}'")
                active_btn.configure(text='Change', fg_color=DANGER, hover_color=DANGER, text_color='white')
                kw.after(1500, lambda b=active_btn: b.configure(fg_color=BG3, hover_color=BORDER, text_color=TEXT2))
                _stop_listening(active_btn)
                refresh_rows()
                return None
            keybinds[action] = key_name
            active_btn.configure(text='Change', fg_color=BG3, hover_color=BORDER, text_color=TEXT2)
            _stop_listening(active_btn)
            refresh_rows()
            status_var.set(f"Saved: '{action}' -> '{key_name.upper()}'")
            _autosave_keybinds()
        kw.bind('<KeyPress>', on_key)
        for i, action in enumerate(keybinds):
            row_bg = BG2 if i % 2 == 0 else BG
            row = ctk.CTkFrame(scroll, fg_color=row_bg, corner_radius=6, height=38)
            row.pack(fill='x', pady=2)
            row.pack_propagate(False)
            ctk.CTkLabel(row, text=action, font=ctk.CTkFont('Segoe UI', 12), text_color=TEXT, anchor='w', width=220).pack(side='left', padx=(12, 4), pady=6)
            key_lbl = ctk.CTkLabel(row, text=f'  {keybinds[action].upper()}  ', font=ctk.CTkFont('Consolas', 12, 'bold'), text_color=ACCENT2, fg_color=BG3, corner_radius=6, width=70)
            key_lbl.pack(side='left', padx=6, pady=6)
            btn = ctk.CTkButton(row, text='Change', width=72, height=26, font=ctk.CTkFont('Segoe UI', 11), fg_color=BG3, hover_color=BORDER, text_color=TEXT2, corner_radius=6)
            btn.configure(command=lambda a=action, b=btn: start_listening(a, b))
            btn.pack(side='right', padx=(4, 10), pady=6)
            row_widgets[action] = (key_lbl, btn)
        bottom = ctk.CTkFrame(kw, fg_color=BG2, corner_radius=0, height=52)
        bottom.pack(fill='x', side='bottom')
        bottom.pack_propagate(False)
        status_var = ctk.StringVar(value='Click \'Change\', then press any key.   Esc = cancel.')
        ctk.CTkLabel(bottom, textvariable=status_var, font=ctk.CTkFont('Segoe UI', 10), text_color=TEXT2, wraplength=290, anchor='w').pack(side='left', padx=14)
        def reset_keybinds():
            keybinds.update(default_keybinds)
            refresh_rows()
            status_var.set('Reset to defaults.')
            _autosave_keybinds()
        ctk.CTkButton(bottom, text='Reset defaults', width=110, height=30, font=ctk.CTkFont('Segoe UI', 11), fg_color=DANGER, hover_color='#b03032', text_color='white', corner_radius=6, command=reset_keybinds).pack(side='right', padx=12, pady=10)
        def on_close():
            global _kb_paused
            global can_open_keybinds
            can_open_keybinds = True
            _kb_paused = False
            kw.destroy()
        kw.protocol('WM_DELETE_WINDOW', on_close)
        kw.update()
        kw.update_idletasks()
        kw.after_idle(_on_ready)
def open_cue_settings_window():
    global slider_cue_start_var
    global _cue_ind_toggle_btn
    global _cue_start_coord_var
    global slider_cue_length
    global _cue_ind_btn_var
    global _cue_end_coord_var
    global cue_settings_window
    global slider_cue_length_var
    global slider_cue_start
    if cue_settings_window is not None and cue_settings_window.winfo_exists():
        cue_settings_window.lift()
        cue_settings_window.focus_force()
        return None
    else:
        cue_settings_window = ctk.CTkToplevel()
        cue_settings_window.title('Cue Settings')
        cue_settings_window.geometry('520x410')
        cue_settings_window.wm_attributes('-topmost', True)
        cue_settings_window.resizable(False, False)
        cue_settings_window.configure(fg_color=BG)
        frame = ctk.CTkFrame(cue_settings_window, fg_color=BG2)
        frame.pack(fill='both', expand=True, padx=15, pady=15)
        lbl1 = ctk.CTkLabel(frame, text='Cue Length Scaler', text_color=TEXT)
        lbl1.pack(anchor='w', pady=(5, 0))
        slider_cue_length_var = tk.StringVar(value=f'{ml.cue_length_scaler:.3f}')
        val_lbl1 = ctk.CTkLabel(frame, textvariable=slider_cue_length_var, width=60)
        val_lbl1.pack(anchor='e')
        def update_length(v):
            ml.cue_length_scaler = float(v)
            slider_cue_length_var.set(f'{ml.cue_length_scaler:.3f}')
            ml.need_update_draws = True
        slider_cue_length = ctk.CTkSlider(frame, from_=0, to=3, number_of_steps=3000, command=update_length)
        slider_cue_length.set(ml.cue_length_scaler)
        slider_cue_length.pack(fill='x', padx=5, pady=(0, 10))
        lbl2 = ctk.CTkLabel(frame, text='Cue Start Scaler', text_color=TEXT)
        lbl2.pack(anchor='w', pady=(5, 0))
        slider_cue_start_var = tk.StringVar(value=f'{ml.cue_start_scaler:.3f}')
        val_lbl2 = ctk.CTkLabel(frame, textvariable=slider_cue_start_var, width=60)
        val_lbl2.pack(anchor='e')
        def update_start(v):
            ml.cue_start_scaler = float(v)
            slider_cue_start_var.set(f'{ml.cue_start_scaler:.3f}')
            ml.need_update_draws = True
        slider_cue_start = ctk.CTkSlider(frame, from_=0, to=3, number_of_steps=3000, command=update_start)
        slider_cue_start.set(ml.cue_start_scaler)
        slider_cue_start.pack(fill='x', padx=5, pady=(0, 4))
        ctk.CTkFrame(frame, fg_color=BORDER, height=1).pack(fill='x', padx=5, pady=(10, 6))
        ind_row = ctk.CTkFrame(frame, fg_color='transparent')
        ind_row.pack(fill='x', padx=5, pady=(0, 6))
        ctk.CTkLabel(ind_row, text='Power Indicator', text_color=TEXT, font=ctk.CTkFont('Segoe UI', 13, 'bold')).pack(side='left')
        _ind_enabled = getattr(ml, 'indicate_power', False)
        _cue_ind_btn_var = tk.StringVar(value='● ON' if _ind_enabled else '○ OFF')
        def _toggle_indicate():
            ml.indicate_power = not getattr(ml, 'indicate_power', False)
            _cue_ind_btn_var.set('● ON' if ml.indicate_power else '○ OFF')
            _cue_ind_toggle_btn.configure(fg_color=SUCCESS if ml.indicate_power else BG3, hover_color='#2d8a4e' if ml.indicate_power else BORDER)
            ml.need_update_draws = True
        _cue_ind_toggle_btn = ctk.CTkButton(ind_row, textvariable=_cue_ind_btn_var, width=72, height=28, corner_radius=6, fg_color=SUCCESS if _ind_enabled else BG3, hover_color='#2d8a4e' if _ind_enabled else BORDER, text_color='white', font=ctk.CTkFont('Segoe UI', 12), command=_toggle_indicate)
        _cue_ind_toggle_btn.pack(side='right')
        def _fmt_pos(val):
            """Format an [x, y] pair, or \'—\' if not set."""
            try:
                return f'{float(val[0]):.1f},  {float(val[1]):.1f}'
            except (TypeError, ValueError, IndexError):
                return '—'
        def _start_crosshair_pick(which, coord_var, btn):
            """\n        Hide the settings window, show a fullscreen crosshair on the overlay.\n        On click → store [x, y], restore everything.  Esc = cancel.\n        \'which\' is \'start\' or \'end\'.\n        """
            cue_settings_window.withdraw()
            mouse_listener = [None]
            key_listener = [None]
            cancelled = [False]
            ch_items = []
            def _draw_crosshair(x, y):
                for item in ch_items:
                    canvas.delete(item)
                ch_items.clear()
                color = '#00e5ff'
                gap = 14
                arm = 30
                ch_items.append(canvas.create_line(x - arm - gap, y, x - gap, y, fill=color, width=2, tags='__crosshair__'))
                ch_items.append(canvas.create_line(x + gap, y, x + arm + gap, y, fill=color, width=2, tags='__crosshair__'))
                ch_items.append(canvas.create_line(x, y - arm - gap, x, y - gap, fill=color, width=2, tags='__crosshair__'))
                ch_items.append(canvas.create_line(x, y + gap, x, y + arm + gap, fill=color, width=2, tags='__crosshair__'))
                ch_items.append(canvas.create_oval(x - 3, y - 3, x + 3, y + 3, outline=color, fill=color, tags='__crosshair__'))
                label = f"Click to set  {('Start' if which == 'start' else 'End')}  position  ({int(x)}, {int(y)})  |  Esc = cancel"
                ch_items.append(canvas.create_text(x, y - arm - gap - 18, text=label, fill=color, font=('Segoe UI', 11), tags='__crosshair__'))
                canvas.update_idletasks()
            from pynput import mouse as _pm, keyboard as _pk
            def _on_move(mx, my):
                canvas.after(0, lambda: _draw_crosshair(mx, my))
            def _on_click(mx, my, button, pressed):
                if not pressed:
                    return None
                else:
                    from pynput.mouse import Button
                    if button == Button.left:
                        _finish(mx, my)
                    return False
            def _on_key(key):
                try:
                    from pynput.keyboard import Key
                    if key == Key.esc:
                        cancelled[0] = True
                        _finish(None, None)
                        return False
                except Exception:
                    pass
            def _finish(mx, my):
                try:
                    if mouse_listener[0] is not None:
                        mouse_listener[0].stop()
                except Exception:
                    pass
                try:
                    if key_listener[0] is not None:
                        key_listener[0].stop()
                except Exception:
                    pass
                canvas.delete('__crosshair__')
                ch_items.clear()
                if not cancelled[0] and mx is not None:
                        pos = [float(mx), float(my)]
                        if which == 'start':
                            ml.power_indicator_start = pos
                        else:
                            ml.power_indicator_end = pos
                        coord_var.set(_fmt_pos(pos))
                        ml.need_update_draws = True
                if cue_settings_window is not None and cue_settings_window.winfo_exists():
                        cue_settings_window.deiconify()
                        cue_settings_window.lift()
                        cue_settings_window.focus_force()
            mouse_listener[0] = _pm.Listener(on_move=_on_move, on_click=_on_click)
            mouse_listener[0].daemon = True
            mouse_listener[0].start()
            key_listener[0] = _pk.Listener(on_press=_on_key)
            key_listener[0].daemon = True
            key_listener[0].start()
        ctk.CTkFrame(frame, fg_color=BORDER, height=1).pack(fill='x', padx=5, pady=(0, 6))
        start_row = ctk.CTkFrame(frame, fg_color='transparent')
        start_row.pack(fill='x', padx=5, pady=(0, 4))
        ctk.CTkLabel(start_row, text='Indicator Start', text_color=TEXT, font=ctk.CTkFont('Segoe UI', 12)).pack(side='left')
        _cue_start_coord_var = tk.StringVar(value=_fmt_pos(getattr(ml, 'power_indicator_start', None)))
        ctk.CTkLabel(start_row, textvariable=_cue_start_coord_var, text_color=ACCENT2, font=ctk.CTkFont('Consolas', 12), width=120, anchor='e').pack(side='left', padx=8)
        _pick_start_btn = ctk.CTkButton(start_row, text='✛  Pick', width=80, height=28, corner_radius=6, fg_color=BG3, hover_color=BORDER, text_color=TEXT, font=ctk.CTkFont('Segoe UI', 12))
        _pick_start_btn.configure(command=lambda: _start_crosshair_pick('start', _cue_start_coord_var, _pick_start_btn))
        _pick_start_btn.pack(side='right')
        end_row = ctk.CTkFrame(frame, fg_color='transparent')
        end_row.pack(fill='x', padx=5, pady=(0, 4))
        ctk.CTkLabel(end_row, text='Indicator End', text_color=TEXT, font=ctk.CTkFont('Segoe UI', 12)).pack(side='left')
        _cue_end_coord_var = tk.StringVar(value=_fmt_pos(getattr(ml, 'power_indicator_end', None)))
        ctk.CTkLabel(end_row, textvariable=_cue_end_coord_var, text_color=ACCENT2, font=ctk.CTkFont('Consolas', 12), width=120, anchor='e').pack(side='left', padx=8)
        _pick_end_btn = ctk.CTkButton(end_row, text='✛  Pick', width=80, height=28, corner_radius=6, fg_color=BG3, hover_color=BORDER, text_color=TEXT, font=ctk.CTkFont('Segoe UI', 12))
        _pick_end_btn.configure(command=lambda: _start_crosshair_pick('end', _cue_end_coord_var, _pick_end_btn))
        _pick_end_btn.pack(side='right')
        def on_close():
            global cue_settings_window
            cue_settings_window.destroy()
            cue_settings_window = None
        cue_settings_window.protocol('WM_DELETE_WINDOW', on_close)
def create_buttons_window():
    global slider_ct
    global slider_lt_var
    global slider_power
    global button_table_geo_lock
    global slider_lt
    global slider_tr
    global slider_scroll_sens_power_var
    global game_version_var
    global _lock_btn_ref
    global button_show_table
    global slider_ct_var
    global slider_tr_var
    global slider_power_var
    global button_scroll_lock
    global button_cue_settings
    global slider_scroll_sens_power
    global slider_scroll_sens_direction_var
    global slider_scroll_sens_direction
    global indirect_black_var
    global indirect_all_var
    global checkbox_indirect_black
    global checkbox_indirect_all
    bw = ctk.CTkToplevel()
    bw.title('Settings')
    bw.after(201, lambda: bw.iconbitmap(resource_path('s.ico')))
    bw.attributes('-topmost', 1)
    bw.resizable(False, False)
    bw.configure(fg_color=BG)
    content = ctk.CTkFrame(bw, fg_color=BG, corner_radius=0)
    content.pack(fill='both', expand=True, padx=20, pady=15)
    def section_lbl(text):
        ctk.CTkLabel(content, text=text, font=ctk.CTkFont('Segoe UI', 10, 'bold'), text_color=TEXT2).pack(anchor='w', pady=(8, 1))
    def divider():
        ctk.CTkFrame(content, fg_color=BORDER, height=1, corner_radius=0).pack(fill='x', pady=2)
    def slider_row(label, from_, to, init, cmd, is_float=False):
        r = ctk.CTkFrame(content, fg_color='transparent')
        r.pack(fill='x', pady=3)
        ctk.CTkLabel(r, text=label, width=100, anchor='w', font=ctk.CTkFont('Segoe UI', 11), text_color=TEXT2).pack(side='left')
        if is_float:
            val_v = ctk.StringVar(value=f'{float(init):.2f}')
            def _cmd(v, vv=val_v, c=cmd):
                vv.set(f'{float(v):.2f}')
                c(v)
        else:
            val_v = ctk.StringVar(value=str(int(init)))
            def _cmd(v, vv=val_v, c=cmd):
                vv.set(str(int(float(v))))
                c(v)
        ctk.CTkLabel(r, textvariable=val_v, width=36, font=ctk.CTkFont('Consolas', 11, 'bold'), text_color=ACCENT2).pack(side='right')
        sl = ctk.CTkSlider(r, from_=from_, to=to, command=_cmd, progress_color=ACCENT, button_color=ACCENT2, button_hover_color=ACCENT, fg_color=BG3, height=14)
        sl.set(init)
        sl.pack(side='left', fill='x', expand=True, padx=6)
        return (sl, val_v)
    save_row = ctk.CTkFrame(content, fg_color='transparent')
    save_row.pack(pady=(2, 0))
    ctk.CTkButton(save_row, text='💾  Save', width=170, height=34, fg_color=WARNING, hover_color='#c47f10', font=ctk.CTkFont('Segoe UI', 12, 'bold'), text_color=BG, corner_radius=8, command=save_).pack(side='left', padx=(0, 10))
    ctk.CTkButton(save_row, text='↩  Revert', width=170, height=34, fg_color=BG3, hover_color=BORDER, font=ctk.CTkFont('Segoe UI', 12), text_color=TEXT, corner_radius=8, command=reset).pack(side='left')
    divider()
    section_lbl('DISPLAY')
    table_row = ctk.CTkFrame(content, fg_color='transparent')
    table_row.pack(fill='x', pady=2)
    button_show_table = ctk.CTkButton(table_row, text='Show table area  ●' if show_table_bounds else 'Show table area  ○', height=32, corner_radius=8, fg_color=SUCCESS if show_table_bounds else BG3, hover_color='#2d8a4e' if show_table_bounds else BORDER, font=ctk.CTkFont('Segoe UI', 12), text_color='white', command=toggle_table_bounds)
    button_show_table.pack(side='left', fill='x', expand=True)
    button_table_geo_lock = ctk.CTkButton(table_row, text='🔒' if ml.lock_table_geo else '🔓', width=34, height=32, corner_radius=8, fg_color=DANGER if ml.lock_table_geo else BG3, hover_color='#b03032' if ml.lock_table_geo else BORDER, font=ctk.CTkFont('Segoe UI', 16), text_color='white' if ml.lock_table_geo else TEXT2)
    def toggle_table_geo_lock():
        ml.lock_table_geo = not ml.lock_table_geo
        _sync_table_geo_lock_btn()
    button_table_geo_lock.configure(command=toggle_table_geo_lock)
    button_table_geo_lock.pack(side='right', padx=(6, 0))
    divider()
    section_lbl('PHYSICS')
    def on_power(v):
        ml.power_cue = round(float(v), 4)
        if slider_power_var:
            slider_power_var.set(f'{ml.power_cue:.2f}')
        ml.need_update_draws = True
    slider_power, slider_power_var = slider_row('Power cue', 0.0, 1.0, ml.power_cue, on_power, is_float=True)
    def _make_bar_row(label, count, color_on, color_on_hover, get_val, set_val, bar_list):
        nonlocal content
        bar_list.clear()
        r = ctk.CTkFrame(content, fg_color='transparent')
        r.pack(fill='x', pady=(4, 1))
        ctk.CTkLabel(r, text=label, width=100, anchor='w', font=ctk.CTkFont('Segoe UI', 11), text_color=TEXT2).pack(side='left')
        bar_frame = ctk.CTkFrame(r, fg_color='transparent')
        bar_frame.pack(side='left', padx=4)
        def _click(idx):
            new_val = idx if get_val()!= idx else idx - 1
            set_val(max(0, new_val))
            _refresh_force_bars()
            ml.need_update_draws = True
        for i in range(count):
            active = i + 1 <= get_val()
            btn = ctk.CTkButton(bar_frame, text='', width=18, height=22, corner_radius=3, fg_color=color_on if active else BG3, hover_color=color_on_hover if active else BORDER, border_width=0, command=lambda idx=i + 1: _click(idx))
            btn.grid(row=0, column=i, padx=2)
            bar_list.append(btn)
    _make_bar_row('Cue force (green)', 10, '#3ba55c', '#2d8a4e', lambda: ml.cue_force_green, lambda v: setattr(ml, 'cue_force_green', v), _bar_green_btns)
    _make_bar_row('Cue force (purple)', 5, '#9b59b6', '#7d3c98', lambda: ml.cue_force_purple, lambda v: setattr(ml, 'cue_force_purple', v), _bar_purple_btns)
    divider()
    section_lbl('THICKNESS  &  TRANSPARENCY')
    def on_ct(v):
        global ct
        ct = int(v)
    def on_lt(v):
        global lt
        lt = int(v)
    def on_tr(v):
        global tr
        tr = int(v)
        window.wm_attributes('-alpha', tr * 0.1)
    slider_ct, slider_ct_var = slider_row('Circles', 1, 10, ct, on_ct)
    slider_lt, slider_lt_var = slider_row('Lines', 1, 10, lt, on_lt)
    slider_tr, slider_tr_var = slider_row('Opacity', 1, 10, tr, on_tr)
    divider()
    section_lbl('MOUSE SCROLL')
    scroll_mode_row = ctk.CTkFrame(content, fg_color='transparent')
    scroll_mode_row.pack(fill='x', pady=(3, 2))
    ctk.CTkLabel(scroll_mode_row, text='Enabled', width=100, anchor='w', font=ctk.CTkFont('Segoe UI', 11), text_color=TEXT2).pack(side='left')
    button_scroll_lock = ctk.CTkButton(scroll_mode_row, text='🔓', width=34, height=34, corner_radius=8, fg_color=BG3, hover_color=BORDER, font=ctk.CTkFont('Segoe UI', 16), text_color=TEXT2)
    def toggle_scroll_lock():
        ml.mouse_scroll_mode = 'off' if str(ml.mouse_scroll_mode).lower() == 'on' else 'on'
        _sync_scroll_lock_btn()
    button_scroll_lock.configure(command=toggle_scroll_lock)
    button_scroll_lock.pack(side='right', padx=(6, 0))
    _sync_scroll_lock_btn()
    def on_scroll_sens_direction(v):
        ml.mouse_scroll_sensitivity_direction = round(float(v), 3)
        if slider_scroll_sens_direction_var:
            slider_scroll_sens_direction_var.set(f'{ml.mouse_scroll_sensitivity_direction:.2f}')
    def on_scroll_sens_power(v):
        ml.mouse_scroll_sensitivity_power = round(float(v), 3)
        if slider_scroll_sens_power_var:
            slider_scroll_sens_power_var.set(f'{ml.mouse_scroll_sensitivity_power:.2f}')
    slider_scroll_sens_direction, slider_scroll_sens_direction_var = slider_row('Direction sens', 0.05, 1.0, ml.mouse_scroll_sensitivity_direction, on_scroll_sens_direction, is_float=True)
    slider_scroll_sens_power, slider_scroll_sens_power_var = slider_row('Power sens', 0.05, 1.0, ml.mouse_scroll_sensitivity_power, on_scroll_sens_power, is_float=True)
    divider()
    section_lbl('VERSION')
    game_version_var = ctk.IntVar(value=ml.game_version)
    def _on_version_change(*_):
        ml.game_version = game_version_var.get()
        ml.update_ball_colors()
        ml.need_update_draws = True
    game_version_var.trace_add('write', _on_version_change)
    vr = ctk.CTkFrame(content, fg_color='transparent')
    vr.pack(fill='x', pady=2)
    for idx, lbl in enumerate(['Web', 'Phone / Emulator']):
        ctk.CTkRadioButton(vr, text=lbl, variable=game_version_var, value=idx, radiobutton_width=16, radiobutton_height=16, fg_color=ACCENT, hover_color=ACCENT2, font=ctk.CTkFont('Segoe UI', 12), text_color=TEXT).pack(side='left', padx=(0, 18))
    divider()
    section_lbl('INDIRECT SHOTS')
    indirect_black_var = tk.BooleanVar(value=ml.indirect_black)
    def _on_indirect_black_change(*_):
        ml.indirect_black = indirect_black_var.get()
        ml.need_update_draws = True
    indirect_black_var.trace_add('write', _on_indirect_black_change)
    indirect_all_var = tk.BooleanVar(value=ml.indirect_all)
    def _on_indirect_all_change(*_):
        ml.indirect_all = indirect_all_var.get()
        ml.need_update_draws = True
    indirect_all_var.trace_add('write', _on_indirect_all_change)
    ind_frame = ctk.CTkFrame(content, fg_color='transparent')
    ind_frame.pack(fill='x', pady=2)
    checkbox_indirect_black = ctk.CTkCheckBox(ind_frame, text='Black Ball Indirect', variable=indirect_black_var, checkbox_width=16, checkbox_height=16, fg_color=ACCENT, hover_color=ACCENT2, font=ctk.CTkFont('Segoe UI', 12), text_color=TEXT)
    checkbox_indirect_black.pack(side='left', padx=(0, 18))
    checkbox_indirect_all = ctk.CTkCheckBox(ind_frame, text='All Balls Indirect', variable=indirect_all_var, checkbox_width=16, checkbox_height=16, fg_color=ACCENT, hover_color=ACCENT2, font=ctk.CTkFont('Segoe UI', 12), text_color=TEXT)
    checkbox_indirect_all.pack(side='left')
    divider()
    kb_row = ctk.CTkFrame(content, fg_color='transparent')
    kb_row.pack(fill='x', pady=(4, 4))
    lock_btn = ctk.CTkButton(kb_row, text='🔓', width=34, height=34, corner_radius=8, fg_color=BG3, hover_color=BORDER, font=ctk.CTkFont('Segoe UI', 16), text_color=TEXT2)
    def toggle_lock():
        global keys_locked
        keys_locked = not keys_locked
        if keys_locked:
            lock_btn.configure(text='🔒', fg_color=DANGER, hover_color='#b03032', text_color='white')
        else:
            lock_btn.configure(text='🔓', fg_color=BG3, hover_color=BORDER, text_color=TEXT2)
    lock_btn.configure(command=toggle_lock)
    lock_btn.pack(side='right', padx=(6, 0))
    _lock_btn_ref = lock_btn
    button_cue_settings = ctk.CTkButton(kb_row, text='C', width=button_scroll_lock.cget('width'), height=button_scroll_lock.cget('height'), fg_color=BG3, hover_color=BORDER, text_color=TEXT, command=open_cue_settings_window)
    button_cue_settings.pack(side='left', padx=(0, 6))
    ctk.CTkButton(kb_row, text='⌨   Keybinds', height=34, corner_radius=8, fg_color=BG3, hover_color=BORDER, font=ctk.CTkFont('Segoe UI', 12), text_color=TEXT, command=create_keys_window).pack(side='left', fill='x', expand=True)
    bw.protocol('WM_DELETE_WINDOW', callback)
if __name__ == '__main__':
    pass
else:

    _default_data = {'table_left': 200, 'table_top': 150, 'table_width': 900, 'table_height': 500, 'ct': 2, 'lt': 2, 'tr': 10, 'power_cue': 0.5, 'show_table_bounds': True, 'lock_table_geo': False, 'game_version': 0, 'transparency': 0.286, 'save': '', 'cue_force_green': 5, 'cue_force_purple': 3, 'keybinds': default_keybinds, 'mouse_scroll_mode': 'on', 'mouse_scroll_sensitivity_power': 0.4, 'mouse_scroll_sensitivity_direction': 0.2, 'cue_length_scaler': 1, 'cue_start_scaler': 1, 'power_indicator_start': [0.0, 0.0], 'power_indicator_end': [0.0, 0.0], 'indicate_power': False, 'indirect_black': False, 'indirect_all': False}
    if not os.path.exists(save_data_name):
        with open(save_data_name, 'w') as f:
            json.dump(_default_data, f)
        print('save data not found, creating one…')
    else:
        print('save data found')
    with open(save_data_name) as f:
        data = json.load(f)
    print('save data loaded:', data)
    import splash_screen
    splash_screen.update(82, 'Applying settings...')
    ct = data.get('ct', 2)
    lt = data.get('lt', 2)
    tr = data.get('tr', 9)
    ml.table_left = data.get('table_left', 200)
    ml.table_top = data.get('table_top', 150)
    ml.table_width = data.get('table_width', 900)
    ml.table_height = data.get('table_height', 500)
    ml.update_radius()
    ml.power_cue = data.get('power_cue', 0.5)
    ml.cue_force_green = data.get('cue_force_green', ml.cue_force_green)
    ml.cue_force_purple = data.get('cue_force_purple', ml.cue_force_purple)
    ml.game_version = data.get('game_version', 0)
    ml.update_ball_colors()
    show_table_bounds = data.get('show_table_bounds', True)
    ml.lock_table_geo = data.get('lock_table_geo', False)
    ml.mouse_scroll_mode = 'on' if str(data.get('mouse_scroll_mode', 'on')).lower()!= 'off' else 'off'
    ml.mouse_scroll_sensitivity_power = data.get('mouse_scroll_sensitivity_power', data.get('mouse_scroll_sensitivity', 0.4))
    ml.mouse_scroll_sensitivity_direction = data.get('mouse_scroll_sensitivity_direction', data.get('mouse_scroll_sensitivity', 0.2))
    ml.cue_length_scaler = data.get('cue_length_scaler', 1)
    ml.cue_start_scaler = data.get('cue_start_scaler', 1)
    ml.power_indicator_start = data.get('power_indicator_start', [0.0, 0.0])
    ml.power_indicator_end = data.get('power_indicator_end', [0.0, 0.0])
    ml.indicate_power = data.get('indicate_power', False)
    ml.indirect_black = data.get('indirect_black', False)
    ml.indirect_all = data.get('indirect_all', False)
    if 'keybinds' in data:
        filtered = {k: v for k, v in data['keybinds'].items() if k in KEYBINDS}
        keybinds.update(filtered)
    import splash_screen
    splash_screen.update(85, 'Creating overlay window...')
    window = tk.Tk()
    window.tk.call('tk', 'scaling', 1.3)
    window.title('overlay')
    window.overrideredirect(True)
    window.wm_attributes('-topmost', True)
    window.wm_attributes('-transparentcolor', 'azure')
    window.wm_attributes('-alpha', tr * 0.1)
    _sw = window.winfo_screenwidth()
    _sh = window.winfo_screenheight()
    window.geometry(f'{_sw}x{_sh}+0+0')
    canvas = tk.Canvas(window, bg='azure', width=_sw, height=_sh, highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)
    def _apply_click_through():
        try:
            hwnd = ctypes.windll.user32.GetAncestor(canvas.winfo_id(), 2)
            GWL_EXSTYLE = (-20)
            WS_EX_LAYERED = 524288
            WS_EX_TRANSPARENT = 32
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_LAYERED | WS_EX_TRANSPARENT)
            print('click-through enabled')
        except Exception as e:
            print('click-through setup failed:', e)
    window.after(100, _apply_click_through)
    import splash_screen
    splash_screen.update(95, 'Launching app...')
    buttons_win_opened = True
    create_buttons_window()
    _start_keyboard_listener()
    canvas.after(250, update_window)
    canvas.after(250, _keep_overlay_topmost)
    canvas.after(80, _poll_kb_queue)
