# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: 'find_paths.py'
# Bytecode version: 3.9.0beta5 (3425)
# Source timestamp: 1970-01-01 00:00:00 UTC (0)

import math
from math2 import *
def distance_point_to_segment(px, py, x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        return math.hypot(px - x1, py - y1)
    else:
        t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
        t = max(0, min(1, t))
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy
        return math.hypot(px - closest_x, py - closest_y)
def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])
def path_blocked(x1, y1, x2, y2, balls, BALL_RADIUS, ignore_ball=None, ignore_ball2=None):
    for b in balls:
        bx, by = (b[0], b[1])
        if ignore_ball is not None and b == ignore_ball:
                continue
        if ignore_ball2 is not None and b == ignore_ball2:
                continue
        dist = distance_point_to_segment(bx, by, x1, y1, x2, y2)
        if dist < BALL_RADIUS * 2:
            return True
    return False
def compute_ghost_ball(ball, pocket, BALL_RADIUS):
    bx, by = ball
    px, py = pocket
    dx = px - bx
    dy = py - by
    length = math.hypot(dx, dy)
    if length == 0:
        return None
    else:
        dx /= length
        dy /= length
        gx = bx - dx * BALL_RADIUS * 2
        gy = by - dy * BALL_RADIUS * 2
        return (gx, gy)
def shot_angle_ok(cue, ghost, ball, max_angle_deg=75):
    cx, cy = cue
    gx, gy = ghost
    bx, by = ball
    v1 = (gx - cx, gy - cy)
    v2 = (bx - gx, by - gy)
    dot = v1[0] * v2[0] + v1[1] * v2[1]
    mag1 = math.hypot(*v1)
    mag2 = math.hypot(*v2)
    if mag1 == 0 or mag2 == 0:
        return False
    else:
        angle = math.degrees(math.acos(dot / (mag1 * mag2)))
        return angle < max_angle_deg
def direct_paths(cue_ball, balls, team_type, mid_pockets, corner_pockets, BALL_RADIUS):
    results = []
    all_pockets = [(p, 'mid') for p in mid_pockets] + [(p, 'corner') for p in corner_pockets]
    for ball in balls:
        if ball[4]!= team_type:
            continue
        else:
            bx, by = (ball[0], ball[1])
            for pocket, pocket_type in all_pockets:
                px, py = pocket
                ghost = compute_ghost_ball((bx, by), (px, py), BALL_RADIUS)
                if ghost is None:
                    continue
                else:
                    gx, gy = ghost
                    if path_blocked(cue_ball[0], cue_ball[1], gx, gy, balls, BALL_RADIUS, ignore_ball=ball):
                        continue
                    else:
                        if path_blocked(bx, by, px, py, balls, BALL_RADIUS, ignore_ball=ball):
                            continue
                        else:
                            if not shot_angle_ok((cue_ball[0], cue_ball[1]), ghost, (bx, by)):
                                continue
                            else:
                                if pocket_type == 'mid' and parallel_to_y((bx, by), (px, py)) < 0.9:
                                        continue
                                angle = math.atan2(gy - cue_ball[1], gx - cue_ball[0])
                                results.append((angle, ghost, (bx, by), (px, py)))
    return results
def mirror_point(p, wall, left, right, top, bottom):
    x, y = p
    if wall == 'left':
        return (2 * left - x, y)
    else:
        if wall == 'right':
            return (2 * right - x, y)
        else:
            if wall == 'top':
                return (x, 2 * top - y)
            else:
                if wall == 'bottom':
                    return (x, 2 * bottom - y)
def line_intersect_wall(cue, target, wall, left, right, top, bottom):
    cx, cy = cue
    tx, ty = target
    dx, dy = (tx - cx, ty - cy)
    if dx == 0 and dy == 0:
        return None

    if wall == 'left':
        t = (left - cx) / dx if dx != 0 else None
    elif wall == 'right':
        t = (right - cx) / dx if dx != 0 else None
    elif wall == 'top':
        t = (top - cy) / dy if dy != 0 else None
    elif wall == 'bottom':
        t = (bottom - cy) / dy if dy != 0 else None
    else:
        return None

    if t is None or t <= 0:
        return None

    x = cx + t * dx
    y = cy + t * dy
    if wall in ['left', 'right'] and not top <= y <= bottom:
        return None
    if wall in ['top', 'bottom'] and not left <= x <= right:
        return None
    return (x, y)
def cue_cushion_paths(cue_ball, balls, team_type, mid_pockets, corner_pockets, table_width, table_height, ball_radius):
    results = []
    left = ball_radius
    right = table_width - ball_radius
    top = ball_radius
    bottom = table_height - ball_radius
    pockets = [(p, 'mid') for p in mid_pockets] + [(p, 'corner') for p in corner_pockets]
    pockets_2 = [(ball_radius, ball_radius), (table_width - ball_radius, ball_radius), (table_width - ball_radius, table_height - ball_radius), (ball_radius, table_height - ball_radius), (table_width / 2, ball_radius), (table_width / 2, table_height - ball_radius)]
    walls = ['left', 'right', 'top', 'bottom']
    for ball in balls:
        if ball[4]!= team_type:
            continue
        else:
            bpos = (ball[0], ball[1])
            for pocket, ptype in pockets:
                dist_bpos_pocket = dist(bpos, pocket)
                if dist_bpos_pocket > ball_radius * 20:
                    continue
                else:
                    ghost = compute_ghost_ball(bpos, pocket, ball_radius)
                    if ghost is None:
                        continue
                    else:
                        for wall in walls:
                            mirrored = mirror_point(ghost, wall, left, right, top, bottom)
                            hit = line_intersect_wall((cue_ball[0], cue_ball[1]), mirrored, wall, left, right, top, bottom)
                            if hit is None:
                                continue
                            else:
                                if dist(hit, cue_ball) < ball_radius:
                                    continue
                                else:
                                    if any((dist(hit, p) < ball_radius * 3 for p in pockets_2)):
                                        continue
                                    else:
                                        if not shot_angle_ok(hit, ghost, bpos, 75 - dist_bpos_pocket * 4 / ball_radius):
                                            continue
                                        else:
                                            if ptype == 'mid' and parallel_to_y(bpos, pocket) < 0.9:
                                                    continue
                                            if path_blocked(cue_ball[0], cue_ball[1], hit[0], hit[1], balls, ball_radius, ignore_ball=None):
                                                continue
                                            else:
                                                if path_blocked(hit[0], hit[1], ghost[0], ghost[1], balls, ball_radius, ignore_ball=ball):
                                                    continue
                                                else:
                                                    if path_blocked(bpos[0], bpos[1], pocket[0], pocket[1], balls, ball_radius, ignore_ball=ball):
                                                        continue
                                                    else:
                                                        angle = math.atan2(hit[1] - cue_ball[1], hit[0] - cue_ball[0])
                                                        results.append((angle, hit, ghost, bpos, pocket))
    return results
def ball_cushion_paths(cue_ball, balls, team_type, mid_pockets, corner_pockets, table_width, table_height, ball_radius):
    results = []
    left = ball_radius
    right = table_width - ball_radius
    top = ball_radius
    bottom = table_height - ball_radius
    pockets = [(p, 'mid') for p in mid_pockets] + [(p, 'corner') for p in corner_pockets]
    pockets_2 = [(ball_radius, ball_radius), (table_width - ball_radius, ball_radius), (table_width - ball_radius, table_height - ball_radius), (ball_radius, table_height - ball_radius), (table_width / 2, ball_radius), (table_width / 2, table_height - ball_radius)]
    walls = ['left', 'right', 'top', 'bottom']
    for ball in balls:
        if ball[4]!= team_type:
            continue
        else:
            bpos = (ball[0], ball[1])
            for pocket, ptype in pockets:
                for wall in walls:
                    mirrored_pocket = mirror_point(pocket, wall, left, right, top, bottom)
                    hit = line_intersect_wall(bpos, mirrored_pocket, wall, left, right, top, bottom)
                    if hit is None:
                        continue
                    else:
                        if dist(bpos, hit) < ball_radius * 1:
                            continue
                        else:
                            if any((dist(hit, p) < ball_radius * 3 for p in pockets_2)):
                                continue
                            else:
                                ghost = compute_ghost_ball(bpos, hit, ball_radius)
                                if ghost is None:
                                    continue
                                else:
                                    if not shot_angle_ok(cue_ball, ghost, bpos, 50):
                                        continue
                                    else:
                                        if ptype == 'mid' and parallel_to_y(hit, pocket) < 0.9:
                                                continue
                                        if path_blocked(cue_ball[0], cue_ball[1], ghost[0], ghost[1], balls, ball_radius, ignore_ball=ball):
                                            continue
                                        else:
                                            if path_blocked(bpos[0], bpos[1], hit[0], hit[1], balls, ball_radius, ignore_ball=ball):
                                                continue
                                            else:
                                                if path_blocked(hit[0], hit[1], pocket[0], pocket[1], balls, ball_radius, ignore_ball=ball):
                                                    continue
                                                else:
                                                    angle = math.atan2(ghost[1] - cue_ball[1], ghost[0] - cue_ball[0])
                                                    results.append((angle, ghost, bpos, hit, pocket))
    return results
def combination_paths(cue_ball, balls, team_type, mid_pockets, corner_pockets, ball_radius):
    results = []
    pockets = [(p, 'mid') for p in mid_pockets] + [(p, 'corner') for p in corner_pockets]
    team_balls = [b for b in balls if b[4] == team_type]
    for ball2 in team_balls:
        b2 = (ball2[0], ball2[1])
        for pocket, ptype in pockets:
            if path_blocked(b2[0], b2[1], pocket[0], pocket[1], balls, ball_radius, ignore_ball=ball2):
                continue
            else:
                if ptype == 'mid' and parallel_to_y(b2, pocket) < 0.9:
                        continue
                ghost2 = compute_ghost_ball(b2, pocket, ball_radius)
                if ghost2 is None:
                    continue
                else:
                    for ball1 in team_balls:
                        if ball1 == ball2:
                            continue
                        else:
                            b1 = (ball1[0], ball1[1])
                            if path_blocked(b1[0], b1[1], ghost2[0], ghost2[1], balls, ball_radius, ignore_ball=ball2, ignore_ball2=ball1):
                                continue
                            else:
                                dist_ball2_pocket = dist(pocket, b2)
                                if not shot_angle_ok(b1, ghost2, b2, 75 - dist_ball2_pocket * 3 / ball_radius):
                                    continue
                                else:
                                    ghost1 = compute_ghost_ball(b1, ghost2, ball_radius)
                                    if ghost1 is None:
                                        continue
                                    else:
                                        if path_blocked(cue_ball[0], cue_ball[1], ghost1[0], ghost1[1], balls, ball_radius, ignore_ball=ball1):
                                            continue
                                        else:
                                            if not shot_angle_ok(cue_ball, ghost1, b1, 75):
                                                continue
                                            else:
                                                aim_angle = math.atan2(ghost1[1] - cue_ball[1], ghost1[0] - cue_ball[0])
                                                results.append((aim_angle, ghost1, b1, ghost2, b2, pocket))
    return results
