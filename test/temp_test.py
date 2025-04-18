

import copy
import time
import pyquaticus.config
from pyquaticus import pyquaticus_v0
from pyquaticus.envs.pyquaticus import Team
from pyquaticus.envs.enable_3d_movement import patch_env_for_3d, _get_polygon_intersection  
from pyquaticus.envs.pyquaticus import PyQuaticusEnv

config = copy.deepcopy(pyquaticus.config.config_dict_std)
config["dynamics"] = ["drone", "drone"] 
config["render_mode"] = None  

PyQuaticusEnv._get_polygon_intersection = _get_polygon_intersection

env = pyquaticus_v0.PyQuaticusEnv(render_mode=None, team_size=1, config_dict=config)

patch_env_for_3d(env)

obs = env.reset()

blue_agent_id = env.agents_of_team[Team.BLUE_TEAM][0].id

z_up_action = 18

print("Testing z-axis movement:")
for i in range(5):
    obs, rewards, terminated, truncated, info = env.step({blue_agent_id: z_up_action})
    z_pos = env.players[blue_agent_id].state.get("z_pos", None)
    print(f"Step {i+1}: Blue agent position = {env.players[blue_agent_id].pos}, z = {z_pos:.2f}")
    time.sleep(0.1)

env.close()
