import numpy as np
from shapely.geometry import LineString

def normalize_vector(v):
    v = np.asarray(v)
    norm = np.linalg.norm(v)
    return v / norm if norm != 0 else v

def extend_to_3d(vec):
    vec = np.asarray(vec)
    if vec.shape[0] == 2:
        return np.append(vec, 0.0)
    return vec

def unify_vector_shapes(*vecs):
    return [extend_to_3d(v) for v in vecs]

def vector_to(p1, p2):
    p1, p2 = unify_vector_shapes(p1, p2)
    return p2 - p1

def mag_bearing_to(p1, p2):
    vec = vector_to(p1, p2)
    mag = np.linalg.norm(vec)
    bearing = np.arctan2(vec[1], vec[0])
    return mag, bearing

def closest_point_on_line(a, b, p):
    a, b, p = unify_vector_shapes(a, b, p)
    ab = b - a
    t = np.dot(p - a, ab) / np.dot(ab, ab)
    t = np.clip(t, 0, 1)
    return a + t * ab

def extend_scrimmage_line(midpoint, direction, length=1000):
    direction = normalize_vector(direction[:2])
    start = np.array(midpoint[:2]) - direction * length
    end = np.array(midpoint[:2]) + direction * length
    return [start, end]

def _segment_intersection(a1, a2, b1, b2):
    a1, a2, b1, b2 = map(lambda p: np.array(p)[:2], [a1, a2, b1, b2])
    da = a2 - a1
    db = b2 - b1
    dp = a1 - b1
    dap = np.array([-da[1], da[0]])
    denom = np.dot(dap, db)
    if denom == 0:
        return None
    num = np.dot(dap, dp)
    intersect = (num / denom.astype(float)) * db + b1
    return np.array([intersect[0], intersect[1], 0.0])


def set_agent_position_3d(agent, pos):
    agent.pos = extend_to_3d(pos)
    agent.state['x_pos'] = agent.pos[0]
    agent.state['y_pos'] = agent.pos[1]
    agent.state['z_pos'] = agent.pos[2]

def set_agent_heading_3d(agent, heading):
    heading = extend_to_3d(heading)
    agent.heading = heading / np.linalg.norm(heading) if np.linalg.norm(heading) else heading

def integrate_agent_motion_3d(agent, action_vec, dt):
    action_vec = extend_to_3d(action_vec)
    if not hasattr(agent, "pos"):
        agent.pos = np.zeros(3)
    agent.pos += action_vec * dt
    set_agent_position_3d(agent, agent.pos)
    if np.linalg.norm(action_vec) > 1e-5:
        set_agent_heading_3d(agent, action_vec)

def reset_agent_position_and_heading(agent, default_pos=(0, 0, 0), default_heading=(1, 0, 0)):
    set_agent_position_3d(agent, default_pos)
    set_agent_heading_3d(agent, default_heading)

def state_to_obs_with_z(agent):
    return {
        "x": agent.state.get("x_pos", 0.0),
        "y": agent.state.get("y_pos", 0.0),
        "z": agent.state.get("z_pos", 0.0),
        "heading": extend_to_3d(agent.heading) if hasattr(agent, 'heading') else np.zeros(3)
    }

def patch_env_for_3d(env):
    for agent in env.players.values():
        reset_agent_position_and_heading(agent)

    original_step = env.step

    def step_with_3d(action_dict):
        for aid, action in action_dict.items():
            agent = env.players[aid]
            if isinstance(action, (list, np.ndarray)):
                integrate_agent_motion_3d(agent, action, dt=1.0)
        return original_step(action_dict)

    env.step = step_with_3d
    return env

def flags_on_opposite_sides(flag1_pos, flag2_pos, scrim_midpoint, scrim_vec):
    f1_vec = np.array(flag1_pos)[:2] - np.array(scrim_midpoint)[:2]
    f2_vec = np.array(flag2_pos)[:2] - np.array(scrim_midpoint)[:2]
    normal_2d = np.array(scrim_vec)[:2]
    dot1 = np.dot(f1_vec, normal_2d)
    dot2 = np.dot(f2_vec, normal_2d)
    if dot1 == 0 or dot2 == 0:
        return np.sign(f1_vec[0]) != np.sign(f2_vec[0])
    return np.sign(dot1) != np.sign(dot2)

# Not working

# def get_scrimmage_vector(flag1, flag2):
#     vec = np.array(flag2) - np.array(flag1)
#     if np.allclose(vec[:2], [0, 0]):
#         return np.array([1.0, 0.0])
#     if np.allclose(vec[1], 0.0):
#         return np.array([0.0, 1.0])
#     normal = np.array([-vec[1], vec[0]])
#     return normalize_vector(normal)

# def safe_distance(p1, p2):
#     p1, p2 = unify_vector_shapes(p1, p2)
#     return np.linalg.norm(p1 - p2)

# def safe_scrimmage_intersections(scrim_coords, env_edges):
#     intersections = []
#     scrim_line = LineString(scrim_coords)
#     for seg in env_edges:
#         seg_line = LineString(seg)
#         inter = scrim_line.intersection(seg_line)
#         if not inter.is_empty:
#             if inter.geom_type == 'Point':
#                 intersections.append(np.array(inter.coords[0]))
#             elif inter.geom_type == 'MultiPoint':
#                 for pt in inter:
#                     intersections.append(np.array(pt.coords[0]))
#     return np.array(intersections)
