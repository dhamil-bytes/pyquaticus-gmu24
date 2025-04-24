"""3D movement related functionality for PyQuaticus."""
from collections import OrderedDict
import numpy as np

def process_3d_movement(player, action_dict, max_speeds):
    """Process 3D movement for Drones and UUVs."""
    if not hasattr(player, 'max_vertical_speed'):
        return 0.0  # Not a 3D vehicle
        
    if player.id not in action_dict:
        return 0.0  # No action provided
        
    try:
        action = action_dict[player.id]
        action_tuple = ACTION_MAP[action]
        vspd = action_tuple[2]  # Vertical speed component
        return player.max_vertical_speed * vspd
    except:
        return 0.0  # Invalid action

def update_3d_state(state, players):
    """Update state dictionary with 3D movement information."""
    if 'agent_z_position' not in state:
        state['agent_z_position'] = np.zeros(len(players))
        state['agent_z_velocity'] = np.zeros(len(players))
    
    for i, player in enumerate(players.values()):
        if hasattr(player, 'z_pos'):
            state['agent_z_position'][i] = player.z_pos
            state['agent_z_velocity'][i] = player.z_vel
