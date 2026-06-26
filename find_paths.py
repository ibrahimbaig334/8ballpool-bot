import math
from math2 import *


def get_adjacent_walls_for_pocket(pocket, ptype, table_width, table_height):
    """
    Return the set of wall names that are physically adjacent (attached) to
    the given pocket.

    Rules (billiard physics):
      - Corner pockets have TWO adjacent walls – the side wall and the end
        wall that meet at that corner.
      - Mid (side) pockets have ONE adjacent wall – the long rail the pocket
        sits on.

    For a 1-cushion shot these walls are INVALID because the rebounding ball
    would strike the pocket jaw instead of entering cleanly.  For 2+ cushion
    shots this restriction does NOT apply.
    """
    px, py = pocket
    invalid = set()

    # Which long rail is the pocket on?
    if py < table_height / 2:
        invalid.add('top')
    else:
        invalid.add('bottom')

    # Corner pockets also involve the nearest side rail
    if ptype == 'corner':
        if px < table_width / 2:
            invalid.add('left')
        else:
            invalid.add('right')

    return invalid


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
        d = distance_point_to_segment(bx, by, x1, y1, x2, y2)
        if d < BALL_RADIUS * 2:
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
        cos_val = dot / (mag1 * mag2)
        cos_val = max(-1.0, min(1.0, cos_val))
        angle = math.degrees(math.acos(cos_val))
        return angle < max_angle_deg


def direct_paths(cue_ball, balls, team_type, mid_pockets, corner_pockets, BALL_RADIUS):
    results = []
    all_pockets = [(p, 'mid') for p in mid_pockets] + [(p, 'corner') for p in corner_pockets]
    for ball in balls:
        if ball[4] != team_type:
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
        if ball[4] != team_type:
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
        if ball[4] != team_type:
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


# ==================== MULTI-CUSHION HELPER FUNCTIONS ====================


def generate_wall_sequences(n, walls=None):
    """
    Generate all sequences of n walls with no consecutive same wall.
    For n=1: 4 sequences, n=2: 12, n=3: 36, n=4: 108.
    """
    if walls is None:
        walls = ['left', 'right', 'top', 'bottom']
    if n == 0:
        return [[]]
    if n == 1:
        return [[w] for w in walls]
    result = []
    for seq in generate_wall_sequences(n - 1, walls):
        for w in walls:
            if w != seq[-1]:
                result.append(seq + [w])
    return result


def find_first_wall_hit(sx, sy, tx, ty, left, right, top, bottom):
    """
    Find which wall the ray from (sx, sy) toward (tx, ty) hits first.
    Returns (wall_name, hit_point) or (None, None) if no wall is hit.
    Used to validate that the intended wall in a sequence is actually
    the first wall the ball/cue would encounter.
    """
    dx = tx - sx
    dy = ty - sy
    if dx == 0 and dy == 0:
        return None, None

    best_t = float('inf')
    best_wall = None
    best_point = None

    # Check left wall (x = left)
    if dx != 0:
        t = (left - sx) / dx
        if t > 1e-9:
            y = sy + t * dy
            if top <= y <= bottom and t < best_t:
                best_t = t
                best_wall = 'left'
                best_point = (left, y)

    # Check right wall (x = right)
    if dx != 0:
        t = (right - sx) / dx
        if t > 1e-9:
            y = sy + t * dy
            if top <= y <= bottom and t < best_t:
                best_t = t
                best_wall = 'right'
                best_point = (right, y)

    # Check top wall (y = top)
    if dy != 0:
        t = (top - sy) / dy
        if t > 1e-9:
            x = sx + t * dx
            if left <= x <= right and t < best_t:
                best_t = t
                best_wall = 'top'
                best_point = (x, top)

    # Check bottom wall (y = bottom)
    if dy != 0:
        t = (bottom - sy) / dy
        if t > 1e-9:
            x = sx + t * dx
            if left <= x <= right and t < best_t:
                best_t = t
                best_wall = 'bottom'
                best_point = (x, bottom)

    return best_wall, best_point


# ==================== MULTI-CUSHION PATH FUNCTIONS ====================


def ball_cushion_paths_n(cue_ball, balls, team_type, mid_pockets, corner_pockets, table_width, table_height, ball_radius, num_cushions):
    """
    Find ball cushion (bank) shots with num_cushions bounces (1-4).
    The target ball bounces off num_cushions cushions before going into the pocket.

    Mirror approach:
      For wall sequence [w1, w2, ..., wn]:
        T[0] = pocket
        T[i] = mirror(T[i-1], w_{n-i+1})   for i = 1..n
      The ball aims at T[n].
      Bounce i: line from previous position to T[n-i] intersects wall w_i.

    Returns list of (aim_angle, ghost, bpos, first_bounce, pocket).
    """
    results = []
    left = ball_radius
    right = table_width - ball_radius
    top = ball_radius
    bottom = table_height - ball_radius
    pockets = [(p, 'mid') for p in mid_pockets] + [(p, 'corner') for p in corner_pockets]
    pockets_2 = [
        (ball_radius, ball_radius),
        (table_width - ball_radius, ball_radius),
        (table_width - ball_radius, table_height - ball_radius),
        (ball_radius, table_height - ball_radius),
        (table_width / 2, ball_radius),
        (table_width / 2, table_height - ball_radius)
    ]

    wall_sequences = generate_wall_sequences(num_cushions)

    for ball in balls:
        if ball[4] != team_type:
            continue
        bpos = (ball[0], ball[1])

        for pocket, ptype in pockets:
            for wall_seq in wall_sequences:
                # Compute mirrored targets: T[0]=pocket, T[i]=mirror(T[i-1], wall_seq[n-i])
                targets = [pocket]
                for i in range(num_cushions):
                    w = wall_seq[num_cushions - 1 - i]
                    targets.append(mirror_point(targets[-1], w, left, right, top, bottom))

                # Trace through wall sequence to find bounce points
                bounce_points = []
                current_start = bpos
                valid = True

                for i in range(num_cushions):
                    aim_target = targets[num_cushions - i]
                    intended_wall = wall_seq[i]

                    # Find intersection with intended wall
                    hit = line_intersect_wall(current_start, aim_target, intended_wall, left, right, top, bottom)
                    if hit is None:
                        valid = False
                        break

                    # Validate: the intended wall must be the first wall the ray hits
                    actual_wall, _ = find_first_wall_hit(
                        current_start[0], current_start[1],
                        aim_target[0], aim_target[1],
                        left, right, top, bottom
                    )
                    if actual_wall != intended_wall:
                        valid = False
                        break

                    # Skip if bounce is too close to starting position
                    if dist(current_start, hit) < ball_radius * 1:
                        valid = False
                        break

                    # Skip if bounce is near a pocket opening
                    if any(dist(hit, p) < ball_radius * 3 for p in pockets_2):
                        valid = False
                        break

                    # For a single-cushion shot the bounce wall must NOT be
                    # adjacent to the target pocket (that would clip the jaw).
                    # Multi-cushion shots are exempt because the ball first
                    # hits a far cushion before arriving at the pocket rail.
                    if num_cushions == 1:
                        adj = get_adjacent_walls_for_pocket(pocket, ptype, table_width, table_height)
                        if intended_wall in adj:
                            valid = False
                            break

                    bounce_points.append(hit)
                    current_start = hit

                if not valid:
                    continue

                # Compute ghost ball: cue must send ball toward the first bounce point
                ghost = compute_ghost_ball(bpos, bounce_points[0], ball_radius)
                if ghost is None:
                    continue

                # Check shot angle at the ghost (cue -> ghost -> ball direction)
                if not shot_angle_ok(cue_ball, ghost, bpos, 50):
                    continue

                # Check mid-pocket angle for the final segment (last bounce -> pocket)
                if ptype == 'mid' and parallel_to_y(bounce_points[-1], pocket) < 0.9:
                    continue

                # Check cue -> ghost path is clear
                if path_blocked(cue_ball[0], cue_ball[1], ghost[0], ghost[1], balls, ball_radius, ignore_ball=ball):
                    continue

                # Check all ball path segments for blockages
                # Segments: bpos -> bounce[0], bounce[i] -> bounce[i+1], ..., bounce[-1] -> pocket
                segments = [(bpos, bounce_points[0])]
                for j in range(len(bounce_points) - 1):
                    segments.append((bounce_points[j], bounce_points[j + 1]))
                segments.append((bounce_points[-1], pocket))

                blocked = False
                for seg_start, seg_end in segments:
                    if path_blocked(seg_start[0], seg_start[1], seg_end[0], seg_end[1], balls, ball_radius, ignore_ball=ball):
                        blocked = True
                        break
                if blocked:
                    continue

                angle = math.atan2(ghost[1] - cue_ball[1], ghost[0] - cue_ball[0])
                results.append((angle, ghost, bpos, bounce_points[0], pocket))

    return results


def cue_cushion_paths_n(cue_ball, balls, team_type, mid_pockets, corner_pockets, table_width, table_height, ball_radius, num_cushions):
    """
    Find cue cushion (kick) shots with num_cushions bounces (1-4).
    The cue ball bounces off num_cushions cushions before hitting the target ball.

    Mirror approach:
      For wall sequence [w1, w2, ..., wn]:
        T[0] = ghost (where cue must be to pot the ball)
        T[i] = mirror(T[i-1], w_{n-i+1})   for i = 1..n
      The cue aims at T[n].
      Bounce i: line from previous position to T[n-i] intersects wall w_i.

    Returns list of (aim_angle, first_bounce, ghost, bpos, pocket).
    """
    results = []
    left = ball_radius
    right = table_width - ball_radius
    top = ball_radius
    bottom = table_height - ball_radius
    pockets = [(p, 'mid') for p in mid_pockets] + [(p, 'corner') for p in corner_pockets]
    pockets_2 = [
        (ball_radius, ball_radius),
        (table_width - ball_radius, ball_radius),
        (table_width - ball_radius, table_height - ball_radius),
        (ball_radius, table_height - ball_radius),
        (table_width / 2, ball_radius),
        (table_width / 2, table_height - ball_radius)
    ]

    wall_sequences = generate_wall_sequences(num_cushions)

    for ball in balls:
        if ball[4] != team_type:
            continue
        bpos = (ball[0], ball[1])

        for pocket, ptype in pockets:
            dist_bpos_pocket = dist(bpos, pocket)
            # Relax distance filter for multi-cushion: allow farther balls
            max_dist = ball_radius * (20 if num_cushions <= 1 else 50 * num_cushions)
            if dist_bpos_pocket > max_dist:
                continue

            ghost = compute_ghost_ball(bpos, pocket, ball_radius)
            if ghost is None:
                continue

            for wall_seq in wall_sequences:
                # Compute mirrored targets for the ghost ball position
                targets = [ghost]
                for i in range(num_cushions):
                    w = wall_seq[num_cushions - 1 - i]
                    targets.append(mirror_point(targets[-1], w, left, right, top, bottom))

                # Trace through wall sequence to find bounce points
                bounce_points = []
                current_start = (cue_ball[0], cue_ball[1])
                valid = True

                for i in range(num_cushions):
                    aim_target = targets[num_cushions - i]
                    intended_wall = wall_seq[i]

                    hit = line_intersect_wall(current_start, aim_target, intended_wall, left, right, top, bottom)
                    if hit is None:
                        valid = False
                        break

                    # Validate: intended wall must be the first wall the ray hits
                    actual_wall, _ = find_first_wall_hit(
                        current_start[0], current_start[1],
                        aim_target[0], aim_target[1],
                        left, right, top, bottom
                    )
                    if actual_wall != intended_wall:
                        valid = False
                        break

                    # Skip if bounce is too close to starting position
                    if dist(hit, current_start) < ball_radius:
                        valid = False
                        break

                    # Skip if bounce is near a pocket opening
                    if any(dist(hit, p) < ball_radius * 3 for p in pockets_2):
                        valid = False
                        break

                    # For a single-cushion cue-kick shot the cue bounce wall
                    # must NOT be adjacent to the target pocket.  The cue
                    # arriving from the pocket's own cushion would clip the jaw
                    # and result in a foul.  Multi-cushion shots are exempt.
                    if num_cushions == 1:
                        adj = get_adjacent_walls_for_pocket(pocket, ptype, table_width, table_height)
                        if intended_wall in adj:
                            valid = False
                            break

                    bounce_points.append(hit)
                    current_start = hit

                if not valid:
                    continue

                # Check shot angle from the last bounce point to the ghost
                max_angle = 75 - dist_bpos_pocket * 4 / ball_radius
                if not shot_angle_ok(bounce_points[-1], ghost, bpos, max_angle):
                    continue

                # Check mid-pocket angle
                if ptype == 'mid' and parallel_to_y(bpos, pocket) < 0.9:
                    continue

                # Check all cue path segments for blockages
                # Segments: cue -> bounce[0], bounce[i] -> bounce[i+1], ..., bounce[-1] -> ghost
                cue_segments = [((cue_ball[0], cue_ball[1]), bounce_points[0])]
                for j in range(len(bounce_points) - 1):
                    cue_segments.append((bounce_points[j], bounce_points[j + 1]))
                cue_segments.append((bounce_points[-1], ghost))

                blocked = False
                for seg_idx, (seg_start, seg_end) in enumerate(cue_segments):
                    # Only ignore target ball on the last segment (cue is hitting the target)
                    ignore = ball if seg_idx == len(cue_segments) - 1 else None
                    if path_blocked(seg_start[0], seg_start[1], seg_end[0], seg_end[1], balls, ball_radius, ignore_ball=ignore):
                        blocked = True
                        break
                if blocked:
                    continue

                # Check ball -> pocket path is clear
                if path_blocked(bpos[0], bpos[1], pocket[0], pocket[1], balls, ball_radius, ignore_ball=ball):
                    continue

                # Aim angle is from cue ball toward the first bounce point
                angle = math.atan2(bounce_points[0][1] - cue_ball[1], bounce_points[0][0] - cue_ball[0])
                results.append((angle, bounce_points[0], ghost, bpos, pocket))

    return results