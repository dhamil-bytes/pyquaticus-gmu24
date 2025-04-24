def _to_speed_heading(self, action_dict):
    """
    Processes the raw discrete actions.

    Returns:
        dict from agent id -> (speed, relative heading, vertical speed)
    """
    processed_action_dict = OrderedDict()
    for player in self.players.values():
        if player.id in action_dict:
            default_action = True
            try:
                action_dict[player.id] / 2
            except:
                default_action = False
            if default_action:
                speed, heading, vspd = self._discrete_action_to_speed_relheading(
                    action_dict[player.id]
                )
                # Scale speed to agent's max speed
                speed = self.max_speeds[player.id] * speed
                # Use 3D movement helper for vertical speed
                vspd = process_3d_movement(player, action_dict, self.max_speeds)
            else:
                # Waypoint navigation case
                _, heading = mag_bearing_to(
                    player.pos,
                    self.config_dict["aquaticus_field_points"][action_dict[player.id]],
                    player.heading,
                )
                if (-0.3 <= self.get_distance_between_2_points(
                        player.pos,
                        self.config_dict["aquaticus_field_points"][action_dict[player.id]],
                    ) <= 0.3
                ):
                    speed = 0.0
                else:
                    speed = self.max_speeds[player.id]
                vspd = 0.0  # No vertical movement for waypoint nav
        else:
            # if no action provided, stop moving
            speed, heading, vspd = 0.0, player.heading, 0.0

        processed_action_dict[player.id] = np.array([speed, heading, vspd], dtype=np.float32)

    # Update 3D state after processing all actions
    update_3d_state(self.state, self.players)
    
    return processed_action_dict
