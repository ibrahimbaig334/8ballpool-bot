global table_height
global prediction_angle
global table_top
global ball_colors
global cue_ball
global need_update_draws
global balls
global table_left
global ball_radius
global predictions
global power_cue
global table_width
import random
import model_use
from simulation_use import simulate_shot
import pyautogui
import cv2
import mss
import numpy as np
from math2 import *
import time
import find_paths
import evaluate_shots
sct = mss.mss()
table_left = 200
table_top = 150
table_width = 900
table_height = 500
lock_table_geo = False
circle_thickness = 2
line_thickness = 2
transparency = 0.9
cue_length_scaler = 1
cue_start_scaler = 1
mouse_scroll_mode = 'on'
mouse_scroll_enabled = False
mouse_scroll_sensitivity_power = 0.2
mouse_scroll_sensitivity_direction = 0.2
cue_force_green = 0
cue_force_purple = 0
game_version = 0
ball_colors = None
ball_colors_rgb = {'cue': (100, 100, 100), 'black': (0, 0, 0), 'red': (255, 0, 0), 'orange': (255, 165, 0), 'purple': (128, 0, 128), 'yellow': (255, 255, 0), 'blue': (0, 0, 255), 'brown': (139, 69, 19), 'green': (0, 128, 0)}
power_cue = 0.5
max_wall_hits = 100
ball_radius = 10
cue_ball = None
balls = []
prediction_angle = 0
predictions = None
power_indicator_start = 1000
power_indicator_end = 1000
indicate_power = False
indirect_black = False
indirect_all   = False
def update_radius():
    global ball_radius
    ball_radius = table_width * 0.0149625
def on_move_table():
    global table_top
    global table_left
    global need_update_draws
    if lock_table_geo:
        return None
    else:
        table_left, table_top = pyautogui.position()
        need_update_draws = True
def on_resize_table():
    global table_height
    global table_width
    global need_update_draws
    if lock_table_geo:
        return None
    else:
        x, y = pyautogui.position()
        new_w = max(50, x - table_left)
        new_h = max(50, y - table_top)
        table_width = new_w
        table_height = new_h
        update_radius()
        need_update_draws = True
def update_ball_colors():
    global ball_colors
    if game_version == 0:
        ball_colors = {
            'cue': {'lower': (17, 7, 173), 'upper': (26, 37, 255), 'min_pixels': table_width * 70 / 664},
            'black': {'lower': (0, 0, 0), 'upper': (0, 0, 120), 'min_pixels': table_width * 58 / 664},
            'red': {'lower': (176, 13, 167), 'upper': (179, 255, 255), 'min_pixels': table_width * 38 / 664},
            'orange': {'lower': (11, 148, 193), 'upper': (12, 248, 248), 'min_pixels': table_width * 30 / 664},
            'purple': {'lower': (133, 42, 140), 'upper': (134, 174, 235), 'min_pixels': table_width * 35 / 664},
            'yellow': {'lower': (20, 129, 152), 'upper': (21, 255, 255), 'min_pixels': table_width * 38 / 664},
            'blue': {'lower': (107, 55, 148), 'upper': (109, 196, 246), 'min_pixels': table_width * 38 / 664},
            'brown': {'lower': (5, 87, 99), 'upper': (7, 163, 147), 'min_pixels': table_width * 15 / 664},
            'green': {'lower': (58, 2, 83), 'upper': (66, 221, 255), 'min_pixels': table_width * 38 / 664},
        }
    else:
        ball_colors = {
            'cue': {'lower': (17, 7, 173), 'upper': (26, 37, 255), 'min_pixels': table_width * 70 / 664},
            'black': {'lower': (0, 16, 0), 'upper': (169, 255, 46), 'min_pixels': table_width * 100 / 664},
            'red': {'lower': (164, 75, 120), 'upper': (179, 255, 255), 'min_pixels': table_width * 38 / 664},
            'orange': {'lower': (8, 90, 90), 'upper': (16, 255, 255), 'min_pixels': table_width * 30 / 664},
            'purple': {'lower': (127, 44, 63), 'upper': (162, 255, 232), 'min_pixels': table_width * 35 / 664},
            'yellow': {'lower': (16, 80, 118), 'upper': (29, 255, 255), 'min_pixels': table_width * 38 / 664},
            'blue': {'lower': (107, 43, 106), 'upper': (132, 187, 255), 'min_pixels': table_width * 38 / 664},
            'brown': {'lower': (0, 92, 35), 'upper': (13, 255, 144), 'min_pixels': table_width * 15 / 664},
            'green': {'lower': (50, 69, 86), 'upper': (68, 222, 226), 'min_pixels': table_width * 38 / 664},
        }
def ball_inside_table(ball_table):
    if ball_table[0] < -ball_radius or ball_table[1] < -ball_radius:
        return False
    else:
        if ball_table[0] > table_width + ball_radius or ball_table[1] > table_height + ball_radius:
            return False
        else:
            return True
def detect_ball_on_mouse():
    global need_update_draws
    from tk_window import delete_all_drawings
    delete_all_drawings()
    detect_ball(pyautogui.position())
    need_update_draws = True
def detect_ball(position_, radius_condition=False):
    global cue_ball
    global balls
    x, y = position_
    detected_ball = model_use.detect_and_classify(x, y, 100)
    if radius_condition:
        if detected_ball[3] == 'none':
            return None
        else:
            if detected_ball[2] > ball_radius * 1.1 or detected_ball[2] < ball_radius * 0.9:
                return None
    detected_ball_screen = (x + detected_ball[0], y + detected_ball[1])
    detected_ball_table = (detected_ball_screen[0] - table_left, detected_ball_screen[1] - table_top)
    if not ball_inside_table(detected_ball_table):
        return None
    else:
        ball_color = get_ball_color(detected_ball_table)
        old_balls = balls
        if ball_color == 'cue':
            cue_ball = (detected_ball_table, detected_ball[2])
            balls = []
        else:
            type_ = 'stripe'
            if ball_color == 'black':
                type_ = 'black'
            else:
                if detected_ball[3] != 'stripe':
                    type_ = 'solid'
            balls = [[detected_ball_table[0], detected_ball_table[1], ball_color, detected_ball[2], type_]]
        for ball in old_balls:
            dist_to_new_ball = calculate_distance([ball[0], ball[1]], [detected_ball_table[0], detected_ball_table[1]])
            if dist_to_new_ball > ball_radius * 1.5:
                balls.append(ball)
def move_ball_near_mouse():
    global need_update_draws
    global cue_ball
    x, y = pyautogui.position()
    x -= table_left
    y -= table_top
    if x < -ball_radius:
        x = -ball_radius
    if x > table_width + ball_radius:
        x = table_width + ball_radius
    if y < -ball_radius:
        y = -ball_radius
    if y > table_height + ball_radius:
        y = table_height + ball_radius
    nearest_index = (-2)
    for i in range(len(balls)):
        if i == 0:
            nearest_index = 0
        else:
            if calculate_distance([balls[i][0], balls[i][1]], [x, y]) < calculate_distance([balls[nearest_index][0], balls[nearest_index][1]], [x, y]):
                nearest_index = i
    if cue_ball is not None:
        if nearest_index == (-2):
            nearest_index = (-1)
        else:
            if calculate_distance(cue_ball[0], [x, y]) < calculate_distance([balls[nearest_index][0], balls[nearest_index][1]], [x, y]):
                nearest_index = (-1)
    if nearest_index == (-1):
        cue_ball = ([x, y], cue_ball[1])
    else:
        if nearest_index != (-2):
            balls[nearest_index] = (x, y, balls[nearest_index][2], balls[nearest_index][3], balls[nearest_index][4])
    need_update_draws = True
def delete_ball_near_mouse():
    global need_update_draws
    global cue_ball
    global balls
    x, y = pyautogui.position()
    x -= table_left
    y -= table_top
    if x < -ball_radius:
        x = -ball_radius
    if x > table_width + ball_radius:
        x = table_width + ball_radius
    if y < -ball_radius:
        y = -ball_radius
    if y > table_height + ball_radius:
        y = table_height + ball_radius
    nearest_index = (-2)
    for i in range(len(balls)):
        if i == 0:
            nearest_index = 0
        else:
            if calculate_distance([balls[i][0], balls[i][1]], [x, y]) < calculate_distance([balls[nearest_index][0], balls[nearest_index][1]], [x, y]):
                nearest_index = i
    if cue_ball is not None:
        if nearest_index == (-2):
            nearest_index = (-1)
        else:
            if calculate_distance(cue_ball[0], [x, y]) < calculate_distance([balls[nearest_index][0], balls[nearest_index][1]], [x, y]):
                nearest_index = (-1)
    if nearest_index == (-1):
        cue_ball = None
    else:
        if nearest_index != (-2):
            old_balls = balls
            balls = []
            for i in range(len(old_balls)):
                if i != nearest_index:
                    balls.append(old_balls[i])
    need_update_draws = True
def get_ball_color(ball_pos):
    ball_color_ = 'black'
    most_px = 0
    roi_x = {'top': table_top + int(ball_pos[1] - ball_radius), 'left': table_left + int(ball_pos[0] - ball_radius), 'width': int(ball_radius * 2), 'height': int(ball_radius * 2)}
    crop_img = np.array(sct.grab(roi_x))
    hsv = cv2.cvtColor(crop_img, cv2.COLOR_BGR2HSV)
    for ball, color_vals in ball_colors.items():
        lower = np.array(color_vals['lower'])
        upper = np.array(color_vals['upper'])
        mask = cv2.inRange(hsv, lower, upper)
        h, w = mask.shape[:2]
        cx, cy = (w // 2, h // 2)
        circle_mask = np.zeros((h, w), dtype=np.uint8)
        cv2.circle(circle_mask, (cx, cy), int(ball_radius), 255, (-1))
        mask = cv2.bitwise_and(mask, circle_mask)
        num_pixels = cv2.countNonZero(mask) / color_vals['min_pixels']
        if num_pixels > most_px:
            most_px = num_pixels
            ball_color_ = ball
    return ball_color_
def detect_table():
    global table_height
    global table_top
    global need_update_draws
    global table_left
    global table_width
    if lock_table_geo:
        return None
    else:
        from tk_window import delete_all_drawings
        delete_all_drawings()
        w, h, l, t = (0, 0, 0, 0)
        if game_version == 0:
            pocket_red_shade = {'lower': (0, 235, 37), 'upper': (179, 253, 82)}
            pocket_black_shade = {'lower': (0, 0, 0), 'upper': (179, 255, 25)}
        else:
            pocket_red_shade_iphone = {'lower': (0, 234, 30), 'upper': (179, 255, 65)}
            pocket_black_shade_iphone = {'lower': (0, 0, 0), 'upper': (179, 255, 21)}
            pocket_red_shade_android = {'lower': (0, 226, 35), 'upper': (179, 255, 82)}
            pocket_black_shade_android = {'lower': (0, 0, 0), 'upper': (179, 255, 25)}
            pocket_red_shade = {'lower': (0, 226, 30), 'upper': (179, 255, 82)}
            pocket_black_shade = {'lower': (0, 0, 0), 'upper': (179, 255, 25)}
        monitor = sct.monitors[1]
        width = monitor['width']
        height = monitor['height']
        roi = {'top': 0, 'left': 0, 'width': width, 'height': height}
        img = np.array(sct.grab(roi))
        img2 = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 1)
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 30, param1=300, param2=34, minRadius=5, maxRadius=100)
        detected_pockets = []
        if circles is not None:
            circles = np.round(circles[0, :]).astype(int)
            for x, y, r in circles:
                h, w = img.shape[:2]
                x1 = max(x - r, 0)
                y1 = max(y - r, 0)
                x2 = min(x + r, w)
                y2 = min(y + r, h)
                crop_img = img[y1:y2, x1:x2]
                if crop_img.size > 0:
                    hsv = cv2.cvtColor(crop_img, cv2.COLOR_BGR2HSV)
                    min_pixels = circle_pixel_area(r) * 0.25
                    lower_red = np.array(pocket_red_shade['lower'])
                    upper_red = np.array(pocket_red_shade['upper'])
                    mask_red = cv2.inRange(hsv, lower_red, upper_red)
                    num_pixels_red = cv2.countNonZero(mask_red)
                    lower_black = np.array(pocket_black_shade['lower'])
                    upper_black = np.array(pocket_black_shade['upper'])
                    mask_black = cv2.inRange(hsv, lower_black, upper_black)
                    num_pixels_black = cv2.countNonZero(mask_black)
                    if num_pixels_black >= min_pixels and num_pixels_red >= min_pixels:
                            detected_pockets.append((x, y, r))
                            cv2.circle(img2, (x, y), 1, (0, 255, 0), 3)
                            cv2.circle(img2, (x, y), r, (255, 0, 0), 2)
        if detected_pockets:
            top_left = min(detected_pockets, key=lambda c: c[1] + c[0])
            top_right = min(detected_pockets, key=lambda c: c[1] - c[0])
            bottom_left = max(detected_pockets, key=lambda c: c[1] - c[0])
            bottom_right = max(detected_pockets, key=lambda c: c[1] + c[0])
            if len(detected_pockets) >= 4:
                avg_r = top_left[2] + top_right[2] + bottom_left[2] + bottom_right[2]
                avg_r /= 4
                l = (top_left[0] + bottom_left[0]) / 2
                t = (top_left[1] + top_right[1]) / 2
                w = (top_right[0] + bottom_right[0]) / 2 - l
                h = (bottom_left[1] + bottom_right[1]) / 2 - t
                roi_t = (t, l + avg_r, w - avg_r * 2, avg_r)
                roi_l = (t + avg_r, l, avg_r, h - avg_r * 2)
                roi_r = (t + avg_r, l + w - avg_r, avg_r, h - avg_r * 2)
                roi_b = (t + h - avg_r, l + avg_r, w - avg_r * 2, avg_r)
                roi_t = tuple(map(int, roi_t))
                roi_l = tuple(map(int, roi_l))
                roi_r = tuple(map(int, roi_r))
                roi_b = tuple(map(int, roi_b))
                top_lines = detect_perpendicular_lines(roi_t)
                if len(top_lines) > 0:
                    top_y = (-1)
                    for line_ in top_lines:
                        if line_[0][1] > top_y:
                            top_y = line_[0][1]
                        if line_[1][1] > top_y:
                            top_y = line_[1][1]
                    top_y += roi_t[0]
                    left_lines = detect_perpendicular_lines(roi_l)
                    if len(left_lines) > 0:
                        left_x = (-1)
                        for line_ in left_lines:
                            if line_[0][0] > left_x:
                                left_x = line_[0][0]
                            if line_[1][0] > left_x:
                                left_x = line_[1][0]
                        left_x += roi_l[1]
                        right_lines = detect_perpendicular_lines(roi_r)
                        if len(right_lines) > 0:
                            right_x = 1000000
                            for line_ in right_lines:
                                if line_[0][0] < right_x:
                                    right_x = line_[0][0]
                                if line_[1][0] < right_x:
                                    right_x = line_[1][0]
                            right_x += roi_r[1]
                            bottom_lines = detect_perpendicular_lines(roi_b)
                            if len(bottom_lines) > 0:
                                bottom_y = 1000000
                                for line_ in bottom_lines:
                                    if line_[0][1] < bottom_y:
                                        bottom_y = line_[0][1]
                                    if line_[1][1] < bottom_y:
                                        bottom_y = line_[1][1]
                                bottom_y += roi_b[0]
                                t = top_y - 1
                                l = left_x - 1
                                w = right_x - left_x + 2
                                h = bottom_y - top_y + 2
                                table_width, table_height, table_left, table_top = (int(w), int(h), int(l), int(t))
                                update_radius()
                                need_update_draws = True
def draw_power_indicator(indicator_start, indicator_end, power_, line_length, color_start, color_power, draw_line):
    """
    Draws:
    - line at indicator_start
    - line at indicator_end
    - moving line between them based on power_ (0-1)

    All lines are parallel and centered on the positions.
    """
    x1, y1 = indicator_start
    x2, y2 = indicator_end
    power_ = max(0.0, min(1.0, power_))
    dx = x2 - x1
    dy = y2 - y1
    d = math.hypot(dx, dy)
    if d == 0:
        return None
    else:
        dx /= d
        dy /= d
        px = -dy
        py = dx
        half_len = line_length / 2
        def make_line(cx, cy):
            sx = cx - px * half_len
            sy = cy - py * half_len
            ex = cx + px * half_len
            ey = cy + py * half_len
            return ((sx, sy), (ex, ey))
        s0, e0 = make_line(x1, y1)
        s1, e1 = make_line(x2, y2)
        mx = x1 + (x2 - x1) * power_
        my = y1 + (y2 - y1) * power_
        sm, em = make_line(mx, my)
        draw_line(s0, e0, color_start)
        draw_line(s1, e1, color_start)
        draw_line(sm, em, color_power)
def draw_predictions(draw_circle, draw_line):
    from simulation_use import POCKETS_SCREEN
    behind1 = 1
    cue_length = 1
    if game_version == 0:
        cue_length = ball_radius * 10.5
        behind1 = ball_radius * 1.7
    else:
        cue_length = ball_radius * 15.5
        behind1 = ball_radius * 1.75
    behind1 *= cue_start_scaler
    cue_length *= cue_length_scaler
    stick_on_0 = get_perpendicular_line(cue_ball[0], prediction_angle, behind1, ball_radius * 2)
    draw_line(stick_on_0[0], stick_on_0[1], ball_colors_rgb['green'])
    stick_on_power = get_perpendicular_line(cue_ball[0], prediction_angle, behind1 + cue_length * predictions[4], ball_radius * 2)
    draw_line(stick_on_power[0], stick_on_power[1], ball_colors_rgb['red'])
    stick_on_100 = get_perpendicular_line(cue_ball[0], prediction_angle, behind1 + cue_length, ball_radius * 2)
    draw_line(stick_on_100[0], stick_on_100[1], ball_colors_rgb['green'])
    if indicate_power:
        power_indicator_start_canvas = (power_indicator_start[0] - table_left, power_indicator_start[1] - table_top)
        power_indicator_end_canvas = (power_indicator_end[0] - table_left, power_indicator_end[1] - table_top)
        draw_power_indicator(power_indicator_start_canvas, power_indicator_end_canvas, predictions[4], ball_radius * 2, ball_colors_rgb['green'], ball_colors_rgb['red'], draw_line)
    target_ball_id = (-10)
    if not predictions[3]:
        target_ball_id = predictions[2]
    else:
        backward_start, backward_end = get_backward_line(cue_ball[0], prediction_angle, ball_radius * 20)
        draw_line(backward_start, backward_end, ball_colors_rgb['cue'])
    for ball_data in predictions[0]:
        ball_color = ball_colors_rgb['cue']
        id_ = ball_data['id']
        if id_ == (-1):
            ball_color = ball_colors_rgb['black']
        else:
            if (-1) < id_ < len(balls):
                    ball_color = ball_colors_rgb[balls[id_][2]]
        for p_i in range(1, len(ball_data['path'])):
            line_end = ball_data['path'][p_i]
            if p_i == 1 and id_ == target_ball_id:
                    line_end = prolong_line(ball_data['path'][p_i - 1], line_end, ball_radius * 10)
            draw_circle(ball_data['path'][p_i], ball_radius, ball_color)
            draw_line(ball_data['path'][p_i - 1], line_end, ball_color)
    for pocketed in predictions[1]:
        ball_color = ball_colors_rgb['cue']
        id_ = pocketed['id']
        if id_ == (-1):
            ball_color = ball_colors_rgb['black']
        else:
            if (-1) < id_ < len(balls):
                    ball_color = ball_colors_rgb[balls[id_][2]]
        pocket_id = pocketed['pocket']
        draw_circle(POCKETS_SCREEN[pocket_id], ball_radius * 2, ball_color)
def get_cue_force():
    cue_force = cue_force_green + cue_force_purple
    if game_version == 0:
        web_f = [520, 576, 630, 683, 705, 722, 746, 767, 787, 805, 827]
        if 0 <= cue_force < len(web_f):
                return web_f[cue_force]
        return 670 + 13 * cue_force + 0.3 * cue_force ** 2
    else:
        phone_f = [670, 681, 699, 715, 730, 750, 760, 775, 790, 815, 831, 850, 869]
        if 0 <= cue_force < len(phone_f):
                return phone_f[cue_force]
        return 670 + 13 * cue_force + 0.3 * cue_force ** 2
def detect_balls():
    global need_update_draws
    from tk_window import delete_all_drawings
    delete_all_drawings()
    delete_all_balls()
    roi = {'top': table_top, 'left': table_left, 'width': table_width, 'height': table_height}
    img = np.array(sct.grab(roi))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    tile_px = int(ball_radius * 2)
    tiles_x = max(2, table_width // tile_px)
    tiles_y = max(2, table_height // tile_px)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(tiles_x, tiles_y))
    gray_contrast = clahe.apply(gray)
    gray_blur = cv2.GaussianBlur(gray_contrast, (3, 3), 0)
    all_circles = []
    all_circles += extract_circles(get_circles(gray))
    all_circles += extract_circles(get_circles(gray_blur))
    all_circles += extract_circles(get_circles(gray_contrast))
    merged_circles = merge_close_circles(all_circles, int(ball_radius) + 1)
    contact_circle = detect_contact_circle(img)
    merged_circles = remove_near_contact(merged_circles, contact_circle, int(ball_radius) + 1)
    for x, y, r in merged_circles:
        detect_ball((table_left + int(x), table_top + int(y)), radius_condition=True)
    need_update_draws = True
def remove_near_contact(merged_circles, contact_circle, min_dist):
    if contact_circle is None:
        return merged_circles
    else:
        cx, cy = contact_circle
        filtered = []
        for x, y, r in merged_circles:
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            if d >= min_dist:
                filtered.append((x, y, r))
        return filtered
def detect_contact_circle(img):
    img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    color_range = {'lower': (0, 0, 240), 'upper': (172, 10, 255)}
    lower = np.array(color_range['lower'])
    upper = np.array(color_range['upper'])
    mask = cv2.inRange(hsv, lower, upper)
    blurred_mask = cv2.GaussianBlur(mask, (3, 3), 0)
    circles = cv2.HoughCircles(blurred_mask, cv2.HOUGH_GRADIENT, 2, 1, param1=135, param2=40, minRadius=int(ball_radius * 0.8), maxRadius=int(ball_radius * 1.5))
    if circles is not None:
        circles = np.round(circles[0, :]).astype(int)
        for x, y, r in circles:
            return (x, y)
def merge_close_circles(circles, merge_dist):
    clusters = []
    for c in circles:
        x, y, r = c
        placed = False
        for cluster in clusters:
            cx, cy, cr, members = cluster
            d = math.hypot(x - cx, y - cy)
            if d < merge_dist:
                members.append(c)
                xs = [m[0] for m in members]
                ys = [m[1] for m in members]
                rs = [m[2] for m in members]
                cluster[0] = np.mean(xs)
                cluster[1] = np.mean(ys)
                cluster[2] = np.mean(rs)
                placed = True
                break
        if not placed:
            clusters.append([x, y, r, [c]])
    return [(c[0], c[1], c[2]) for c in clusters]
def extract_circles(circles):
    if circles is None:
        return []
    else:
        circles = np.squeeze(circles, axis=0)
        return [(float(x), float(y), float(r)) for x, y, r in circles]
def get_circles(img):
    circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, dp=1.0, minDist=ball_radius * 1.5, param1=int(np.clip(80 + ball_radius * 2, 80, 200)), param2=int(np.clip(ball_radius * 1.2, 15, 60)), minRadius=int(ball_radius - 0.95), maxRadius=int(ball_radius + 1.05))
    return circles
def calc_predictions():
    global predictions
    if cue_ball is not None:
        balls_data, pocketed, first_hit_id, cue_hit_wall_first = simulate_shot(cue_ball[0], (1000, 1000), balls, [], prediction_angle, power_cue, get_cue_force(), table_width)
        predictions = (balls_data, pocketed, first_hit_id, cue_hit_wall_first, power_cue)
    else:
        predictions = None
def direction_to_mouse():
    global need_update_draws
    global prediction_angle
    if cue_ball is None:
        return None
    else:
        x, y = pyautogui.position()
        mouse_pos_on_canvas = (x - table_left, y - table_top)
        prediction_angle = get_aim_angle(cue_ball[0], mouse_pos_on_canvas)
        need_update_draws = True
need_update_draws = False
def get_pockets():
    from simulation_use import POCKETS_SCREEN
    corner_pockets = [(ball_radius, ball_radius), (table_width - ball_radius, ball_radius), (table_width - ball_radius, table_height - ball_radius), (ball_radius, table_height - ball_radius)]
    mid_pockets = [POCKETS_SCREEN[1], POCKETS_SCREEN[4]]
    return (corner_pockets, mid_pockets)
def update_draws(draw_circle_fn, draw_line_fn):
    from tk_window import delete_all_drawings_no_updt, _draw_table_rect
    delete_all_drawings_no_updt()
    _draw_table_rect()
    calc_predictions()
    if cue_ball is not None:
        draw_circle_fn(cue_ball[0], ball_radius, ball_colors_rgb['cue'])
    ball_colors_rgb2 = {'stripe': (0, 128, 0), 'black': (0, 0, 0), 'solid': (255, 0, 0)}
    for ball in balls:
        draw_circle_fn([ball[0], ball[1]], ball_radius, ball_colors_rgb2[ball[4]])
    if predictions is not None and cue_ball is not None:
            draw_predictions(draw_circle_fn, draw_line_fn)
def delete_all_draw():
    from tk_window import delete_all_drawings_no_updt
    delete_all_drawings_no_updt()
def update_canvas():
    from tk_window import update_canvas_
    update_canvas_()
def draw_search(balls_data, pocketed, POCKETS_SCREEN):
    from tk_window import delete_all_drawings_no_updt, update_canvas_, draw_circle, draw_line
    delete_all_drawings_no_updt()
    cue_pos = (0, 0)
    for ball_data in balls_data:
        ball_color = ball_colors_rgb['cue']
        id_ = ball_data['id']
        if id_ == (-2):
            cue_pos = ball_data['final_pos']
        else:
            if id_ == (-1):
                ball_color = ball_colors_rgb['black']
            else:
                if (-1) < id_ < len(balls):
                        ball_color = ball_colors_rgb[balls[id_][2]]
        for p_i in range(1, len(ball_data['path'])):
            line_end = ball_data['path'][p_i]
            draw_circle(ball_data['path'][p_i], ball_radius, ball_color)
            draw_line(ball_data['path'][p_i - 1], line_end, ball_color)
    for pocketed_ in pocketed:
        ball_color = ball_colors_rgb['cue']
        id_ = pocketed_['id']
        if id_ == (-1):
            ball_color = ball_colors_rgb['black']
        else:
            if (-1) < id_ < len(balls):
                    ball_color = ball_colors_rgb[balls[id_][2]]
        pocket_id = pocketed_['pocket']
        draw_circle(POCKETS_SCREEN[pocket_id], ball_radius * 2, ball_color)
    update_canvas_()
    return cue_pos
def delete_all_balls():
    global need_update_draws
    global cue_ball
    global balls
    cue_ball = None
    balls = []
    need_update_draws = True
def score_single(angle_, power_, cue_ball_, black_ball_, team_balls_, opp_balls_, cue_cushion_mode=False):
    from simulation_use import POCKETS_SCREEN
    balls_data, pocketed, first_hit_id, cue_hit_wall_first = simulate_shot(cue_ball_, black_ball_, team_balls_, opp_balls_, angle_, power_, get_cue_force(), table_width)
    draw_search(balls_data, pocketed, POCKETS_SCREEN)
    if cue_cushion_mode and cue_hit_wall_first:
        # For a deliberate cue-cushion shot the cue hits the wall before the
        # team ball – skip the "hit team ball first" foul check and only
        # require that a team ball was actually pocketed without a scratch.
        return evaluate_shots.evaluate_result_cushion(balls_data, pocketed, len(team_balls_))
    return evaluate_shots.evaluate_result(balls_data, pocketed, first_hit_id, len(team_balls_))
def find_shot_stripe():
    find_shot_x('stripe')
def find_shot_solid():
    find_shot_x('solid')
def find_shot_black():
    find_shot_x('black')
def _best_from_angles(angles, cue_ball_, black_, team_balls_, opp_balls_, cue_cushion_mode=False):
    """
    Score every candidate aim angle and return the (angle, power, score)
    triple with the highest robust score strictly above 0 (i.e. a shot that
    genuinely pocketed a team ball without a foul).  Returns None when no
    angle succeeds so the caller can fall through to the next priority tier.
    cue_cushion_mode=True is forwarded to the evaluator so that cue-wall-first
    shots are not rejected by the hit_team_first foul check.
    """
    best = None
    for angle in angles:
        result = angle_score_best_power(angle, cue_ball_, black_, team_balls_, opp_balls_, cue_cushion_mode=cue_cushion_mode)
        if result[0] is None:
            continue
        if result[2] > 0 and (best is None or result[2] > best[2]):
            best = result
    return best
def find_shot_x(ball_type_x):
    """
    Priority cascade:
      1. Direct shots          (skipped when indirect mode is active)
      2. Combination shots     (skipped when indirect mode is active)
      3. Ball-cushion shots    – 1 to 4 cushions
      4. Cue-cushion shots     – 1 to 4 cushions
    indirect_all  → skip 1 & 2 for every ball type.
    indirect_black → skip 1 & 2 only when the target type resolves to 'black'.
    """
    global need_update_draws, power_cue, prediction_angle
    if cue_ball is None:
        return None
    evaluate_shots.TABLE_X_MIN    = 0
    evaluate_shots.TABLE_X_MAX    = table_width
    evaluate_shots.TABLE_Y_MIN    = 0
    evaluate_shots.TABLE_Y_MAX    = table_height
    evaluate_shots.ball_radius_ev = ball_radius
    # ── Categorise balls on the table ────────────────────────────────────────
    ball_type  = 'black'
    team_balls = []
    opp_balls  = []
    black      = (1000, 1000)
    for ball in balls:
        if ball_type_x == 'black' and ball[4] == 'black':
            black = (ball[0], ball[1])
        elif ball[4] == ball_type_x:
            ball_type = ball_type_x
            team_balls.append((ball[0], ball[1]))
        elif ball[4] == 'black':
            black = (ball[0], ball[1])
        elif ball[4]:
            opp_balls.append((ball[0], ball[1]))
    # Bug-3 fix: if none of the requested ball type were detected, bail out.
    # Without this guard the code falls through and searches for 8-ball shots,
    # which score positively and overwrite prediction_angle with a losing move.
    if ball_type != ball_type_x and ball_type != 'black':
        return None
    if ball_type == 'black' and black == (1000, 1000):
        return None
    corner_pockets, mid_pockets = get_pockets()
    # ── Determine whether to allow direct / combination shots ─────────────────
    _is_black_shot  = (ball_type == 'black')
    _skip_direct    = indirect_all or (indirect_black and _is_black_shot)
    best_shot = None
    # ── Priority 1: Direct shots ──────────────────────────────────────────────
    if not _skip_direct:
        dp = find_paths.direct_paths(
            cue_ball[0], balls, ball_type, mid_pockets, corner_pockets, ball_radius)
        if dp:
            best_shot = _best_from_angles(
                [p[0] for p in dp], cue_ball[0], black, team_balls, opp_balls)
    # ── Priority 2: Combination shots ─────────────────────────────────────────
    if best_shot is None and not _skip_direct:
        cp = find_paths.combination_paths(
            cue_ball[0], balls, ball_type, mid_pockets, corner_pockets, ball_radius)
        if cp:
            best_shot = _best_from_angles(
                [p[0] for p in cp], cue_ball[0], black, team_balls, opp_balls)
    # ── Priority 3: Ball-cushion (bank) shots – 1 to 2 cushions ──────────────
    if best_shot is None:
        for n_cush in range(1, 3):
            bcp = find_paths.ball_cushion_paths_n(
                cue_ball[0], balls, ball_type, mid_pockets, corner_pockets,
                table_width, table_height, ball_radius, n_cush)
            if bcp:
                result = _best_from_angles(
                    [p[0] for p in bcp], cue_ball[0], black, team_balls, opp_balls)
                if result is not None:
                    best_shot = result
                    break
    # ── Priority 4: Cue-cushion (kick) shots – 1 to 2 cushions ───────────────
    if best_shot is None:
        for n_cush in range(1, 3):
            ccp = find_paths.cue_cushion_paths_n(
                cue_ball[0], balls, ball_type, mid_pockets, corner_pockets,
                table_width, table_height, ball_radius, n_cush)
            if ccp:
                result = _best_from_angles(
                    [p[0] for p in ccp], cue_ball[0], black, team_balls, opp_balls,
                    cue_cushion_mode=True)
                if result is not None:
                    best_shot = result
                    break
    # ── Apply the best shot found ─────────────────────────────────────────────
    if best_shot is not None:
        prediction_angle  = best_shot[0]
        power_cue         = best_shot[1]
        need_update_draws = True
        from tk_window import _refresh_sliders
        _refresh_sliders()
def angle_score_best_power(angle_, cue_ball_, black_, team_balls_, opp_balls_, cue_cushion_mode=False):
    """
    Sweep 21 power levels (0.00 – 1.00) and find the one with the best
    neighbourhood-robust score.  Returns (angle, power, score) only when the
    best score is strictly > 0, meaning at least one power plateau resulted in
    a legitimately pocketed team ball without any foul.  If every power level
    produced an invalid simulation (-9999: scratch, wrong first ball, nothing
    pocketed), returns (None, None, -999999) so callers can safely skip it.
    cue_cushion_mode=True relaxes the "hit team ball first" constraint so that
    cue-cushion (kick) shots are evaluated correctly.
    """
    action = [(-0.5001966165614263), (-0.27094216647114566)]
    powers = np.arange(0.0, 1.01, 0.05)
    neighborhood_size = int((action[0] + 1) * 4)
    power_scores = []
    for power in powers:
        score_ = score_single(angle_, power, cue_ball_, black_, team_balls_, opp_balls_, cue_cushion_mode=cue_cushion_mode)
        power_scores.append(score_)
    best_local = (None, None, (-999999))
    for i, power in enumerate(powers):
        if i - neighborhood_size < 0 or i + neighborhood_size + 1 > len(power_scores):
            continue
        lo = max(0, i - neighborhood_size)
        hi = min(len(power_scores), i + neighborhood_size + 1)
        neighborhood = power_scores[lo:hi]
        m = np.mean(neighborhood)
        s = np.std(neighborhood) if len(neighborhood) > 1 else 0
        robust_score = m - (action[1] + 1) * 5 * s
        if robust_score > best_local[2]:
            best_local = (angle_, power, robust_score)
    # Only return a result when the shot is genuinely valid (score > 0).
    # This prevents 5%-power / cue-scratch angles from being used.
    if best_local[2] <= 0:
        return (None, None, (-999999))
    return best_local
def update(draw_circle_fn, draw_line_fn):
    global need_update_draws
    if need_update_draws:
        update_draws(draw_circle_fn, draw_line_fn)
        need_update_draws = False