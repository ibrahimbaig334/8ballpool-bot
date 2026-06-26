import math
TABLE_X_MIN = (-127.0)
TABLE_X_MAX = 127.0
TABLE_Y_MIN = (-63.5)
TABLE_Y_MAX = 63.5
ball_radius_ev = 3.800475
MID_POCKET_INDICES = {1, 4}
action = [None, None, (-0.8531844545073385), 0.5114593102707045, 0.7499797561554263, 0.07825022326845107, 0.9030268601261435, 0.35251917355723783, (-0.7454533974668375)]
def evaluate_result(balls_data, pocketed, first_hit_id, team_len):
    from simulation_use import POCKETS
    score = 0
    cue_pocketed = any((b['id'] == (-2) for b in pocketed))
    black_pocketed = any((b['id'] == (-1) for b in pocketed))
    if team_len == 0:
        hit_team_first = first_hit_id == (-1)
        team_pocketed = any((b['id'] == (-1) for b in pocketed))
    else:
        hit_team_first = 0 <= first_hit_id < team_len
        team_pocketed = any((0 <= b['id'] < team_len for b in pocketed))
    if cue_pocketed or (black_pocketed and team_len > 0) or (not hit_team_first) or (not team_pocketed):
        return (-9999)
    else:
        score += compute_openness(balls_data, team_len, POCKETS, pocketed) * ((action[2] + 1) * 5)
        score += compute_openness_cue(balls_data, team_len, pocketed) * ((action[3] + 1) * 5)
        score += compute_openness_cue2(balls_data, team_len, pocketed, POCKETS) * ((action[4] + 1) * 5)
        score += calculate_avg_nearest_neighbor_dist(balls_data, team_len, pocketed) * ((action[5] + 1) * 5)
        valid_grid = get_valid_cue_grid(balls_data, pocketed)
        score += compute_grid_potting_coverage(balls_data, team_len, pocketed, POCKETS, valid_grid) * ((action[6] + 1) * 5)
        score += compute_all_balls_pottable(balls_data, team_len, pocketed, POCKETS, valid_grid) * ((action[7] + 1) * 5)
        score += compute_balls_away_from_walls(balls_data, team_len, pocketed) * ((action[8] + 1) * 5)
        return score
def evaluate_result_cushion(balls_data, pocketed, team_len):
    """
    Relaxed evaluator for deliberate cue-cushion (kick) shots.
    The cue ball intentionally hits the cushion/wall before touching the target
    ball, so 'hit_team_first' is skipped.  Only the following fouls still
    disqualify the shot:
      - cue ball pocketed (scratch)
      - black ball pocketed while team balls remain
      - no team ball was pocketed at all
    Scoring uses the same position-quality metrics as the standard evaluator.
    """
    from simulation_use import POCKETS
    score = 0
    cue_pocketed = any((b['id'] == (-2) for b in pocketed))
    black_pocketed = any((b['id'] == (-1) for b in pocketed))
    if team_len == 0:
        team_pocketed = any((b['id'] == (-1) for b in pocketed))
    else:
        team_pocketed = any((0 <= b['id'] < team_len for b in pocketed))
    if cue_pocketed or (black_pocketed and team_len > 0) or (not team_pocketed):
        return (-9999)
    else:
        score += compute_openness(balls_data, team_len, POCKETS, pocketed) * ((action[2] + 1) * 5)
        score += compute_openness_cue(balls_data, team_len, pocketed) * ((action[3] + 1) * 5)
        score += compute_openness_cue2(balls_data, team_len, pocketed, POCKETS) * ((action[4] + 1) * 5)
        score += calculate_avg_nearest_neighbor_dist(balls_data, team_len, pocketed) * ((action[5] + 1) * 5)
        valid_grid = get_valid_cue_grid(balls_data, pocketed)
        score += compute_grid_potting_coverage(balls_data, team_len, pocketed, POCKETS, valid_grid) * ((action[6] + 1) * 5)
        score += compute_all_balls_pottable(balls_data, team_len, pocketed, POCKETS, valid_grid) * ((action[7] + 1) * 5)
        score += compute_balls_away_from_walls(balls_data, team_len, pocketed) * ((action[8] + 1) * 5)
        return score
def _build_cue_grid():
    """\n    Returns all 21 (x, y) grid positions before any overlap filtering.\n    Inset from every wall by 2 x ball_radius.\n    """
    inset = ball_radius_ev * 2
    x_min = TABLE_X_MIN + inset
    x_max = TABLE_X_MAX - inset
    y_min = TABLE_Y_MIN + inset
    y_max = TABLE_Y_MAX - inset
    cols = 7
    rows = 3
    positions = []
    for row in range(rows):
        t_y = row / (rows - 1)
        y = y_min + t_y * (y_max - y_min)
        for col in range(cols):
            t_x = col / (cols - 1)
            x = x_min + t_x * (x_max - x_min)
            positions.append((x, y))
    return positions
_CUE_GRID_ALL = _build_cue_grid()
def get_valid_cue_grid(balls_data, pocketed):
    """\n    Returns the subset of _CUE_GRID_ALL whose positions do not overlap any\n    ball currently on the table (all non-pocketed, non-cue balls).\n\n    Call this once per evaluation and pass the result to both grid score\n    functions so the overlap check is done only once.\n    """
    pocketed_ids = {p['id'] for p in pocketed}
    obstacles = [b['final_pos'] for b in balls_data if b['id']!= (-2) and b['id'] not in pocketed_ids]
    min_sep = ball_radius_ev * 2
    return [pos for pos in _CUE_GRID_ALL if not any((math.hypot(pos[0] - ox, pos[1] - oy) < min_sep for ox, oy in obstacles))]
def parallel_to_y(ball, pocket):
    """\n    Returns abs(dy) / length — how parallel the ball→pocket direction is to\n    the Y axis.  Values close to 1.0 mean the shot approaches the mid-pocket\n    nearly perpendicularly (straight in); values close to 0.0 mean it runs\n    almost along the rail and cannot drop.\n    """
    dx = pocket[0] - ball[0]
    dy = pocket[1] - ball[1]
    length = math.hypot(dx, dy)
    if length == 0:
        return 0
    else:
        return abs(dy) / length
def mid_pocket_reachable(ball_pos, pocket):
    """\n    For mid-pockets the shot must approach mostly perpendicular to the long\n    rail (parallel_to_y >= 0.9).  Corner pockets are always reachable from\n    any angle, so this always returns True for them.\n    """
    return parallel_to_y(ball_pos, pocket) >= 0.9
def _cue_goes_behind_target(cue_pos, target_pos, ghost_pos):
    """\n    Returns True if the cue would have to travel through or past the target\n    ball to reach the ghost contact point -- an impossible shot.\n\n    The ghost is always exactly 2*ball_radius from the target centre by\n    construction, so a distance-to-segment test always triggers falsely.\n    Instead we use a dot-product projection:\n\n        Project the target onto the cue->ghost ray.\n\n    If the target\'s projection t >= 1.0, the target sits at or beyond the\n    ghost along that ray, meaning the ghost is on the far side of the target\n    from the cue -- the cue must pass through the target to reach it (invalid).\n\n    If t < 1.0 the ghost is on the near side; the cue approaches the target\n    and makes contact without needing to cross it (valid).\n    """
    cx, cy = cue_pos
    tx, ty = target_pos
    gx, gy = ghost_pos
    dx = gx - cx
    dy = gy - cy
    len_sq = dx * dx + dy * dy
    if len_sq == 0:
        return False
    else:
        t = ((tx - cx) * dx + (ty - cy) * dy) / len_sq
        return t >= 1.0
def _cue_can_pot_ball(cue_pos, target_pos, target_id, pockets, obstacles_excl_target):
    """\n    Helper: given a hypothetical cue position, can it pot `target_pos` into\n    at least one pocket?\n\n    Checks per pocket:\n      1. Mid-pocket angle constraint (parallel_to_y >= 0.9).\n      2. Ghost ball is inside table bounds and does not overlap any obstacle.\n      3. The cue does NOT need to travel behind/through the target to reach\n         the ghost (target must not block the cue→ghost segment).\n      4. cue → ghost segment is unobstructed by other balls.\n      5. target → pocket segment is unobstructed.\n\n    `obstacles_excl_target` is a list of (id, pos) tuples for every ball on\n    the table except the target and the cue itself.\n    """
    obstacle_positions = [pos for _, pos in obstacles_excl_target]
    tx, ty = target_pos
    for p_idx, pocket in enumerate(pockets):
        px, py = pocket
        if p_idx in MID_POCKET_INDICES and (not mid_pocket_reachable((tx, ty), pocket)):
                continue
        ghost = compute_ghost_pos((tx, ty), pocket)
        if ghost is None:
            continue
        else:
            if not ghost_is_valid(ghost, obstacle_positions):
                continue
            else:
                if _cue_goes_behind_target(cue_pos, target_pos, ghost):
                    continue
                else:
                    blocked = False
                    gx, gy = ghost
                    for _, (ox, oy) in obstacles_excl_target:
                        if point_to_segment_distance(ox, oy, cue_pos[0], cue_pos[1], gx, gy) < ball_radius_ev * 2:
                            blocked = True
                            break
                    if blocked:
                        continue
                    else:
                        for _, (ox, oy) in obstacles_excl_target:
                            if point_to_segment_distance(ox, oy, tx, ty, px, py) < ball_radius_ev * 2:
                                blocked = True
                                break
                        if not blocked:
                            return True
    return False
def compute_grid_potting_coverage(balls_data, team_len, pocketed, pockets, valid_grid):
    """\n    Score 1 — Grid potting coverage.\n\n    Counts how many of the pre-filtered valid cue grid positions can pot at\n    least one team ball (or the black when team_len == 0) into at least one\n    pocket.  Overlap filtering is already done in valid_grid; no per-loop\n    check is needed here.\n\n    Returns an integer 0–21.\n    """
    pocketed_ids = {p['id'] for p in pocketed}
    if not valid_grid:
        return 0
    start_id = 0 if team_len > 0 else (-1)
    targets = []
    for b in balls_data:
        bid = b['id']
        if bid in pocketed_ids or bid == (-2):
            continue
        if start_id <= bid < team_len or (team_len == 0 and bid == (-1)):
            targets.append(b)
    if not targets:
        return 0
    all_obstacles = [(b['id'], b['final_pos']) for b in balls_data if b['id']!= (-2) and b['id'] not in pocketed_ids]
    coverage = 0
    for grid_pos in valid_grid:
        can_pot_any = False
        for target in targets:
            tid = target['id']
            obstacles_excl = [(bid, pos) for bid, pos in all_obstacles if bid!= tid]
            if _cue_can_pot_ball(grid_pos, target['final_pos'], tid, pockets, obstacles_excl):
                can_pot_any = True
                break
        if can_pot_any:
            coverage += 1
    return coverage
def compute_all_balls_pottable(balls_data, team_len, pocketed, pockets, valid_grid):
    """\n    Score 2 — All balls pottable.\n\n    Returns 10 if every remaining team ball (or the black when team_len == 0)\n    can be potted from at least one pre-filtered valid cue grid position.\n    Returns 0 if even one ball has no grid position from which it can be potted.\n    Overlap filtering is already done in valid_grid; no per-loop check needed.\n    """
    pocketed_ids = {p['id'] for p in pocketed}
    start_id = 0 if team_len > 0 else (-1)
    targets = []
    for b in balls_data:
        bid = b['id']
        if bid in pocketed_ids or bid == (-2):
            continue
        if start_id <= bid < team_len or (team_len == 0 and bid == (-1)):
            targets.append(b)
    if not targets:
        return 10
    if not valid_grid:
        return 0
    all_obstacles = [(b['id'], b['final_pos']) for b in balls_data if b['id']!= (-2) and b['id'] not in pocketed_ids]
    for target in targets:
        tid = target['id']
        obstacles_excl = [(bid, pos) for bid, pos in all_obstacles if bid!= tid]
        ball_pottable = False
        for grid_pos in valid_grid:
            if _cue_can_pot_ball(grid_pos, target['final_pos'], tid, pockets, obstacles_excl):
                ball_pottable = True
                break
        if not ball_pottable:
            return 0
    return 10
def compute_balls_away_from_walls(balls_data, team_len, pocketed):
    """\n    Score 3 — Balls away from walls.\n\n    Counts how many remaining team balls (and the black when team_len == 0)\n    have their centre at least 3 × ball_radius away from every cushion\n    (i.e. the ball is not hugging any wall).\n\n    Returns the raw count.\n    """
    min_wall_dist = ball_radius_ev * 3
    pocketed_ids = {p['id'] for p in pocketed}
    start_id = 0 if team_len > 0 else (-1)
    count = 0
    for b in balls_data:
        bid = b['id']
        if bid in pocketed_ids or bid == (-2):
            continue
        if not (start_id <= bid < team_len or (team_len == 0 and bid == (-1))):
            continue
        bx, by = b['final_pos']
        dist_left = bx - TABLE_X_MIN
        dist_right = TABLE_X_MAX - bx
        dist_bottom = by - TABLE_Y_MIN
        dist_top = TABLE_Y_MAX - by
        if dist_left >= min_wall_dist and dist_right >= min_wall_dist and dist_bottom >= min_wall_dist and dist_top >= min_wall_dist:
            count += 1
    return count
def compute_openness(ball_data, team_len, pockets, pocketed):
    score = 0
    for ball in ball_data:
        if (-1) <= ball['id'] < team_len and (not any((ball['id'] == b['id'] for b in pocketed))):
                    score += count_clear_pockets(ball['id'], pockets, ball_data, pocketed)
    return score / (team_len + 1)
def calculate_avg_nearest_neighbor_dist(balls_data, team_len, pocketed):
    """\n    Calculates the average distance from each team ball (and the black ball)\n    to its nearest neighbor on the table.\n    """
    target_balls = []
    all_balls = []
    for ball in balls_data:
        if not any((ball['id'] == b['id'] for b in pocketed)):
            if (-1) <= ball['id'] < team_len:
                    target_balls.append(ball['final_pos'])
            if ball['id']!= (-2):
                all_balls.append(ball['final_pos'])
    nearest_distances = []
    for target in target_balls:
        min_dist = float('inf')
        for neighbor in all_balls:
            if target == neighbor:
                continue
            else:
                dist = math.sqrt((target[0] - neighbor[0]) ** 2 + (target[1] - neighbor[1]) ** 2)
                if dist < min_dist:
                    min_dist = dist
        if min_dist!= float('inf'):
            nearest_distances.append(min_dist)
    if not nearest_distances:
        return 0.0
    else:
        return sum(nearest_distances) / len(nearest_distances)
def point_to_segment_distance(px, py, ax, ay, bx, by):
    """Distance from point P to line segment AB"""
    abx = bx - ax
    aby = by - ay
    apx = px - ax
    apy = py - ay
    ab_len_sq = abx * abx + aby * aby
    if ab_len_sq == 0:
        return math.hypot(px - ax, py - ay)
    else:
        t = (apx * abx + apy * aby) / ab_len_sq
        t = max(0.0, min(1.0, t))
        closest_x = ax + t * abx
        closest_y = ay + t * aby
        return math.hypot(px - closest_x, py - closest_y)
def compute_ghost_pos(target_pos, pocket):
    """\n    Compute the ghost ball position: the point where the cue ball centre\n    must be at the moment of contact to send target_pos toward pocket.\n\n    The ghost ball sits one full ball-diameter behind the target ball on the\n    line (pocket → target):\n        ghost = target + unit(target - pocket) * ball_diameter\n    """
    ball_diameter = ball_radius_ev * 2
    tx, ty = target_pos
    px, py = pocket
    dx = tx - px
    dy = ty - py
    length = math.hypot(dx, dy)
    if length == 0:
        return None
    else:
        ux = dx / length
        uy = dy / length
        return (tx + ux * ball_diameter, ty + uy * ball_diameter)
def ghost_is_valid(ghost_pos, obstacles_positions, x_min=TABLE_X_MIN, x_max=TABLE_X_MAX, y_min=TABLE_Y_MIN, y_max=TABLE_Y_MAX):
    """\n    Returns True when ghost_pos is:\n      1. Fully inside the table bounds (centre + radius within the cushions).\n      2. Not overlapping any obstacle ball (centre distance > 2 * ball_radius).\n    """
    gx, gy = ghost_pos
    if gx - ball_radius_ev < x_min or gx + ball_radius_ev > x_max or gy - ball_radius_ev < y_min or (gy + ball_radius_ev > y_max):
        return False
    else:
        min_sep = ball_radius_ev * 2
        for ox, oy in obstacles_positions:
            if math.hypot(gx - ox, gy - oy) < min_sep:
                return False
        return True
def count_clear_pockets(ball_id, pockets, balls_data, pocketed):
    """\n    Returns how many pockets have a clear straight path from ball_id\'s\n    final_pos to the pocket, taking into account:\n\n      0. [Mid-pockets only] ball→pocket direction must satisfy\n         parallel_to_y >= 0.9 (nearly perpendicular to long rail).\n      1. Ghost ball position is inside table bounds.\n      2. Ghost ball position does not overlap any other ball.\n      3. The straight line ball → pocket is unobstructed.\n    """
    pocketed_ids = {p['id'] for p in pocketed}
    target_ball = next((b for b in balls_data if b['id'] == ball_id), None)
    if not target_ball:
        return 0
    start = target_ball['final_pos']
    obstacles = []
    for b in balls_data:
        bid = b['id']
        if bid == ball_id or bid in pocketed_ids:
            continue
        obstacles.append((bid, b['final_pos']))
    obstacle_positions = [pos for _, pos in obstacles]
    clear_count = 0
    for p_idx, pocket in enumerate(pockets):
        px, py = pocket
        if p_idx in MID_POCKET_INDICES and not mid_pocket_reachable(start, pocket):
            continue
        ghost = compute_ghost_pos(start, pocket)
        if ghost is None:
            continue
        if not ghost_is_valid(ghost, obstacle_positions):
            continue
        blocked = False
        for _, pos in obstacles:
            ox, oy = pos
            dist = point_to_segment_distance(ox, oy, start[0], start[1], px, py)
            if dist < ball_radius_ev * 2:
                blocked = True
                break
        if not blocked:
            clear_count += 1
    return clear_count
def compute_openness_cue2(balls_data, team_len, pocketed, pockets):
    """\n    Returns fraction of team balls that have at least one valid pocket where:\n      - [Mid-pockets only] target ball→pocket direction satisfies\n        parallel_to_y >= 0.9,\n      - ghost position is inside the table and does not overlap any ball,\n      - cue → ghost segment is unobstructed,\n      - target ball → pocket segment is unobstructed.\n\n    cue ball id = -2\n    team balls ids = 0 to team_len-1\n    """
    pocketed_ids = {p['id'] for p in pocketed}
    cue = next((b for b in balls_data if b['id'] == (-2)), None)
    if cue is None:
        return 0.0
    cue_pos = cue['final_pos']
    obstacles = []
    for b in balls_data:
        bid = b['id']
        if bid == (-2) or bid in pocketed_ids:
            continue
        obstacles.append((bid, b['final_pos']))
    open_count = 0
    team_len2 = sum((1 for target_id in range(0, team_len) if target_id not in pocketed_ids))
    start_x = 0 if team_len2 > 0 else (-1)
    for target_id in range(start_x, team_len):
        if target_id in pocketed_ids:
            continue
        target = next((b for b in balls_data if b['id'] == target_id), None)
        if target is None:
            continue
        tx, ty = target['final_pos']
        obstacles_excl_target = [(bid, pos) for bid, pos in obstacles if bid!= target_id]
        obstacle_positions_excl_target = [pos for _, pos in obstacles_excl_target]
        is_open = False
        for p_idx, pocket in enumerate(pockets):
            px, py = pocket
            if p_idx in MID_POCKET_INDICES and not mid_pocket_reachable((tx, ty), pocket):
                continue
            ghost = compute_ghost_pos((tx, ty), pocket)
            if ghost is None:
                continue
            if not ghost_is_valid(ghost, obstacle_positions_excl_target):
                continue
            if _cue_goes_behind_target(cue_pos, (tx, ty), ghost):
                continue
            blocked = False
            gx, gy = ghost
            for _, (ox, oy) in obstacles_excl_target:
                dist = point_to_segment_distance(ox, oy, cue_pos[0], cue_pos[1], gx, gy)
                if dist < ball_radius_ev * 2:
                    blocked = True
                    break
            if blocked:
                continue
            for _, (ox, oy) in obstacles_excl_target:
                dist = point_to_segment_distance(ox, oy, tx, ty, px, py)
                if dist < ball_radius_ev * 2:
                    blocked = True
                    break
            if not blocked:
                is_open = True
                break
        if is_open:
            open_count += 1
    return open_count / (team_len + 1) * 8
def compute_openness_cue(balls_data, team_len, pocketed):
    """\n    Returns fraction of team balls that cue ball can directly see.\n\n    cue ball id = -2\n    team balls ids = 0 to team_len-1\n    """
    pocketed_ids = {p['id'] for p in pocketed}
    cue = next((b for b in balls_data if b['id'] == (-2)), None)
    if cue is None:
        return 0.0
    cue_pos = cue['final_pos']
    visible = 0
    team_len2 = sum(1 for target_id in range(0, team_len) if target_id not in pocketed_ids)
    start_x = 0 if team_len2 > 0 else (-1)
    for target_id in range(start_x, team_len):
        if target_id in pocketed_ids:
            continue
        target = next((b for b in balls_data if b['id'] == target_id), None)
        if target is None:
            continue
        tx, ty = target['final_pos']
        blocked = False
        for ball in balls_data:
            bid = ball['id']
            if bid == (-2) or bid == target_id or bid in pocketed_ids:
                continue
            ox, oy = ball['final_pos']
            dist = point_to_segment_distance(ox, oy, cue_pos[0], cue_pos[1], tx, ty)
            if dist < ball_radius_ev * 2:
                blocked = True
                break
        if not blocked:
            visible += 1
    return visible / (team_len + 1) * 8
def count_clear_pockets_legacy(ball_id, pockets, balls_data, pocketed):
    """\n    Original version without ghost-ball or mid-pocket check (kept for reference).\n    """
    pocketed_ids = {p['id'] for p in pocketed}
    target_ball = next((b for b in balls_data if b['id'] == ball_id), None)
    if not target_ball:
        return 0
    else:
        start = target_ball['final_pos']
        obstacles = [(b['id'], b['final_pos']) for b in balls_data if b['id']!= ball_id and b['id'] not in pocketed_ids]
        clear_count = 0
        for pocket in pockets:
            px, py = pocket
            blocked = False
            for _, pos in obstacles:
                ox, oy = pos
                dist = point_to_segment_distance(ox, oy, start[0], start[1], px, py)
                if dist < ball_radius_ev * 2:
                    blocked = True
                    break
            if not blocked:
                clear_count += 1
        return clear_count
