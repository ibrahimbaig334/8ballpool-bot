import os
import sys
import math
import random

_CORE_DIR = os.path.dirname(os.path.abspath(__file__))
_BINARIES_DIR = os.path.join(_CORE_DIR, 'binaries')
if _BINARIES_DIR not in sys.path:
    sys.path.insert(0, _BINARIES_DIR)

try:
    from binaries import simulate_core
except ImportError:
    print('Error: Could not import simulate_core. Make sure you have compiled the C++ script with pybind11.')
    sys.exit(1)
SIM_WIDTH = 254.0
SIM_HEIGHT = 127.0
BALL_RADIUS_SIM = 3.800475
POCKETS = [((-130.56), (-67.06)), (0.0, (-69.92)), (130.56, (-67.06)), (130.56, 67.06), (0.0, 69.92), ((-130.56), 67.06)]
POCKETS_SCREEN = [((-130.56), (-67.06)), (0.0, (-69.92)), (130.56, (-67.06)), (130.56, 67.06), (0.0, 69.92), ((-130.56), 67.06)]
def to_sim_coords(screen_x, screen_y, table_screen_w):
    screen_to_sim = SIM_WIDTH / table_screen_w
    sim_x = (screen_x - table_screen_w / 2) * screen_to_sim
    sim_y = (screen_y - table_screen_w * (SIM_HEIGHT / SIM_WIDTH) / 2) * screen_to_sim
    return (sim_x, sim_y)
def to_screen_coords(sim_x, sim_y, table_screen_w):
    screen_to_sim = SIM_WIDTH / table_screen_w
    scr_x = sim_x / screen_to_sim + table_screen_w / 2
    scr_y = sim_y / screen_to_sim + table_screen_w * (SIM_HEIGHT / SIM_WIDTH) / 2
    return (scr_x, scr_y)
def simulate_shot(cue_pos, black_pos, team_balls, opp_balls, aim_angle_rad, POWER, MAX_POWER, table_screen_w):
    global POCKETS_SCREEN
    POCKETS_SCREEN = [to_screen_coords(x, y, table_screen_w) for x, y in POCKETS]
    cue_pos_sim = to_sim_coords(cue_pos[0], cue_pos[1], table_screen_w)
    black_pos_sim = to_sim_coords(black_pos[0], black_pos[1], table_screen_w)
    team_balls_sim = [to_sim_coords(b[0], b[1], table_screen_w) for b in team_balls]
    opp_balls_sim = [to_sim_coords(b[0], b[1], table_screen_w) for b in opp_balls]
    sim_results = simulate_core.get_simplified_billiard_prediction(cue_pos_sim, black_pos_sim, team_balls_sim, opp_balls_sim, aim_angle_rad, POWER, MAX_POWER, 100)
    balls_data = sim_results.get('balls', [])
    pocketed = sim_results.get('pocketed', [])
    first_hit_id = sim_results.get('first_hit_id', (-2))
    cue_hit_wall_first = sim_results.get('cue_hit_wall_first')
    converted_balls = []
    for ball in balls_data:
        new_ball = dict(ball)
        new_path = []
        for x, y in ball.get('path', []):
            sx, sy = to_screen_coords(x, y, table_screen_w)
            new_path.append((sx, sy))
        new_ball['path'] = new_path
        fx, fy = ball.get('final_pos', (0.0, 0.0))
        new_ball['final_pos'] = to_screen_coords(fx, fy, table_screen_w)
        converted_balls.append(new_ball)
    return (converted_balls, pocketed, first_hit_id, cue_hit_wall_first)
def generate_random_table():
    positions = []
    def get_valid_pos():
        margin = BALL_RADIUS_SIM
        while True:
            px = random.uniform(-SIM_WIDTH / 2 + margin, SIM_WIDTH / 2 - margin)
            py = random.uniform(-SIM_HEIGHT / 2 + margin, SIM_HEIGHT / 2 - margin)
            if not any((math.hypot(px - ox, py - oy) < BALL_RADIUS_SIM * 2 for ox, oy in positions)):
                return (px, py)
    cue_pos = get_valid_pos()
    positions.append(cue_pos)
    black_pos = get_valid_pos()
    positions.append(black_pos)
    num_team = random.randint(1, 7)
    team_balls = []
    for _ in range(num_team):
        pos = get_valid_pos()
        team_balls.append(pos)
        positions.append(pos)
    num_opp = random.randint(1, 7)
    opp_balls = []
    for _ in range(num_opp):
        pos = get_valid_pos()
        opp_balls.append(pos)
        positions.append(pos)
    return (cue_pos, black_pos, team_balls, opp_balls)
