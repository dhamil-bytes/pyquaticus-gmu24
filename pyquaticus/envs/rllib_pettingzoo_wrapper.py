# DISTRIBUTION STATEMENT A. Approved for public release. Distribution is unlimited.
#
# This material is based upon work supported by the Under Secretary of Defense for
# Research and Engineering under Air Force Contract No. FA8702-15-D-0001. Any opinions,
# findings, conclusions or recommendations expressed in this material are those of the
# author(s) and do not necessarily reflect the views of the Under Secretary of Defense
# for Research and Engineering.
#
# (C) 2023 Massachusetts Institute of Technology.
#
# The software/firmware is provided to you on an As-Is basis
#
# Delivered to the U.S. Government with Unlimited Rights, as defined in DFARS
# Part 252.227-7013 or 7014 (Feb 2014). Notwithstanding any copyright notice, U.S.
# Government rights in this work are defined by DFARS 252.227-7013 or DFARS
# 252.227-7014 as detailed above. Use of this work other than as specifically
# authorized by the U.S. Government may violate any copyrights that exist in this
# work.

# SPDX-License-Identifier: BSD-3-Clause

from ray.rllib.env.wrappers.pettingzoo_env import ParallelPettingZooEnv as RLlibParallelPettingZooEnv
from typing import Optional

from pyquaticus.dynamics.dynamics import Drone, UUV


class ParallelPettingZooWrapper(RLlibParallelPettingZooEnv):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Track which agents are 3D-capable
        self.is_3d_agent = {}
        for agent_id in self.env.possible_agents:
            agent = self.env.agents[agent_id]
            self.is_3d_agent[agent_id] = isinstance(agent, (Drone, UUV))

    def reset(self, *, seed: Optional[int] = None, options: Optional[dict] = None):
        # Initialize 3D positions for Drones and UUVs
        obs, info = self.env.reset(seed=seed, options=options)
        
        # Update observation spaces for 3D agents
        for agent_id in self.env.agents:
            if self.is_3d_agent[agent_id]:
                obs[agent_id].update({
                    'z_pos': 0.0,  # Initial z position
                    'z_vel': 0.0   # Initial z velocity
                })
        
        return obs, info
        info = {}
        return self.par_env.reset(seed=seed, options=options), info

    def render(self):
        return self.par_env.render()
