#Updated test file to verify z-axis movement for PyQuaticusEnv (3D-enabled)

import copy
import time
import pyquaticus.config
from pyquaticus import pyquaticus_v0
from pyquaticus.envs.pyquaticus import Team
from pyquaticus.envs.enable_3d_movement import patch_env_for_3d, _get_polygon_intersection  
from pyquaticus.envs.pyquaticus import PyQuaticusEnv

config = copy.deepcopy(pyquaticus.config.config_dict_std)
config["dynamics"] = ["drone", "drone"]  # using Drone dynamics for 3D
config["render_mode"] = None  # no rendering needed for this test


# Inject 3D-safe method into the class
PyQuaticusEnv._get_polygon_intersection = _get_polygon_intersection

# Now create environment
env = pyquaticus_v0.PyQuaticusEnv(render_mode=None, team_size=1, config_dict=config)

# Enable z-axis logic and step patching
patch_env_for_3d(env)

# Reset environment
obs = env.reset()

# Setup agent IDs
blue_agent_id = env.agents_of_team[Team.BLUE_TEAM][0].id

# Action for blue agent to move upward slowly (id=18 based on arrowkeys_3d_cords_test.py)
z_up_action = 18

# Step environment and print z-position
print("Testing z-axis movement:")
for i in range(5):
    obs, rewards, terminated, truncated, info = env.step({blue_agent_id: z_up_action})
    z_pos = env.players[blue_agent_id].state.get("z_pos", None)
    print(f"Step {i+1}: Blue agent position = {env.players[blue_agent_id].pos}, z = {z_pos:.2f}")
    time.sleep(0.1)

env.close()
