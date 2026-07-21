import math
import numpy as np
import mss
import cv2
import random
sct = mss.mss()
def get_backward_line(cue_pos, angle_rad, length):
    x, y = cue_pos
    dx = -math.cos(angle_rad)
    dy = -math.sin(angle_rad)
    end_x = x + dx * length
    end_y = y + dy * length
    return ((x, y), (end_x, end_y))
def random_rad_angle():
    return random.uniform(-math.pi, math.pi)
def normalize_angle(a):
    return (a + math.pi) % (2 * math.pi) - math.pi
def angle_from_vertical(ball, pocket):
    dx = pocket[0] - ball[0]
    dy = pocket[1] - ball[1]
    angle = math.degrees(math.atan2(dx, dy))
    return abs(angle)
def parallel_to_y(ball, pocket):
    dx = pocket[0] - ball[0]
    dy = pocket[1] - ball[1]
    length = math.hypot(dx, dy)
    if length == 0:
        return 0
    else:
        return abs(dy) / length
def prolong_line(origin, end, prolong_dist):
    """\n    Prolongs a line segment from origin through end by an additional distance.\n\n    Args:\n        origin (tuple): (x, y) coordinates of the start point.\n        end (tuple): (x, y) coordinates of the current end point.\n        prolong_dist (float): The distance to add to the line\'s length.\n\n    Returns:\n        tuple: The new (x, y) coordinates of the updated end point.\n    """
    x1, y1 = origin
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1
    current_length = math.sqrt(dx ** 2 + dy ** 2)
    if current_length == 0:
        return end
    else:
        new_length = current_length + prolong_dist
        scale = new_length / current_length
        new_x = x1 + dx * scale
        new_y = y1 + dy * scale
        return (new_x, new_y)
def calculate_distance(pt1, pt2):
    x1, y1 = pt1
    x2, y2 = pt2
    dx = x2 - x1
    dy = y2 - y1
    distance = math.sqrt(dx ** 2 + dy ** 2)
    return distance
def circle_pixel_area(radius_: int) -> int:
    """\n    Returns the number of pixels inside a circle of a given radius.\n    Formula: area = π × r²\n    """
    return int(math.pi * radius_ ** 2)
def detect_perpendicular_lines(roi):
    def filter_perpendicular(lines, angle_thresh=10):
        filtered = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = abs(np.degrees(np.arctan2(y2 - y1, x2 - x1)))
            if angle < angle_thresh or abs(angle - 90) < angle_thresh:
                filtered.append(((x1, y1), (x2, y2)))
        return filtered
    with mss.mss() as sct:
        monitor = {'top': roi[0], 'left': roi[1], 'width': roi[2], 'height': roi[3]}
        screenshot = np.array(sct.grab(monitor))
        frame = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=10, maxLineGap=100)
        if lines is not None:
            return filter_perpendicular(lines)
        else:
            return []
def get_perpendicular_line(cue_pos, aim_angle, distance_behind=10, line_length=10):
    base_x = cue_pos[0] + math.cos(aim_angle + math.pi) * distance_behind
    base_y = cue_pos[1] + math.sin(aim_angle + math.pi) * distance_behind
    half_len = line_length / 2
    perp_angle = aim_angle + math.pi / 2
    dx = math.cos(perp_angle) * half_len
    dy = math.sin(perp_angle) * half_len
    point1 = (base_x + dx, base_y + dy)
    point2 = (base_x - dx, base_y - dy)
    return (point1, point2)
def get_aim_angle(cue_pos, target_pos):
    dx = target_pos[0] - cue_pos[0]
    dy = target_pos[1] - cue_pos[1]
    angle_rad = math.atan2(dy, dx)
    return angle_rad
def dist2(a, b):
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return dx * dx + dy * dy
def split_path_by_anchors(path, anchors, eps=2.0):
    """\n    Split path whenever it reaches a collision/final point.\n    eps = matching tolerance (pixels)\n    """
    segments = []
    current = [path[0]]
    anchor_i = 0
    for pt in path[1:]:
        current.append(pt)
        if anchor_i < len(anchors) and dist2(pt, anchors[anchor_i]) < eps * eps:
                segments.append(current)
                current = [pt]
                anchor_i += 1
    if len(current) > 1:
        segments.append(current)
    return segments
def update_angle(current_angle, change_amount):
    new_angle = current_angle + change_amount
    return (new_angle + math.pi) % (2 * math.pi) - math.pi
def simplify_path(points, tolerance=1.5):
    """\n    Remove intermediate points that lie on nearly straight lines.\n\n    tolerance:\n        how much curve is allowed (pixels).\n        bigger = fewer lines.\n    """
    if len(points) <= 2:
        return points
    else:
        simplified = [points[0]]
        for i in range(1, len(points) - 1):
            ax, ay = simplified[(-1)]
            bx, by = points[i]
            cx, cy = points[i + 1]
            abx, aby = (bx - ax, by - ay)
            bcx, bcy = (cx - bx, cy - by)
            cross = abs(abx * bcy - aby * bcx)
            length = math.hypot(abx, aby)
            deviation = cross / (length + 1e-06)
            if deviation > tolerance:
                simplified.append((bx, by))
        simplified.append(points[(-1)])
        return simplified
def red_blue_gradient(t):
    t = max(0, min(1, t))
    r = int(255 * t)
    g = 0
    b = int(255 * (1 - t))
    return (r, g, b)