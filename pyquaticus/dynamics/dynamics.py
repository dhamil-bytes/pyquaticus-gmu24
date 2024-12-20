import numpy as np
from pyquaticus.utils.utils import clip, angle180
from pyquaticus.dynamics.dynamics_utils import rotation_matrix
from pyquaticus.utils.pid import PID
from pyquaticus.structs import RenderingPlayer


class Dynamics(RenderingPlayer):
    """
    Base class for dynamics
    """

    def __init__(
        self,
        gps_env: bool,
        meters_per_mercator_xy: float,
        dt: float,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.gps_env = gps_env
        self.meters_per_mercator_xy = meters_per_mercator_xy
        self.dt = dt

        self.state = {}

    def get_max_speed(self) -> float:

        raise NotImplementedError

    def reset(self):
        """
        Set all time-varying state/control values to their default initialization values.
        Do not change pos, speed, heading, is_tagged, has_flag, or on_own_side.
        """

        raise NotImplementedError

    def rotate(self, theta=180):
        """
        Set all time-varying state/control values to their default initialization values as in reset().
        Set speed to 0.
        Rotate heading theta degrees.
        Place agent at previous position.
        Do not change is_tagged, has_flag, or on_own_side.
        """

        raise NotImplementedError

    def _move_agent(self, desired_speed: float, heading_error: float):
        """
        Needs to update (at a minimum)

        - self.prev_pos
        - self.pos
        - self.speed
        - self.heading

        based on

        - desired_speed (m/s)
        - heading_error (deg)
        """

        raise NotImplementedError


class FixedWing(Dynamics):

    def __init__(
        self,
        min_speed: float = 10,
        max_speed: float = 20,
        min_turn_radius: float = 20,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.min_speed = min_speed
        self.max_speed = max_speed
        self.min_turn_radius = min_turn_radius

    def reset(self):
        """
        Set all time-varying state/control values to their default initialization values.
        Do not change pos, speed, heading, is_tagged, has_flag, or on_own_side.
        """

        pass  # Nothing needed here

    def rotate(self, theta=180):
        """
        Set all time-varying state/control values to their default initialization values as in reset().
        Set speed to 0.
        Rotate heading theta degrees.
        Place agent at previous position.
        Do not change is_tagged, has_flag, or on_own_side.
        """

        prev_pos = self.prev_pos
        self.prev_pos = self.pos
        self.pos = prev_pos
        self.speed = self.min_speed
        self.heading = angle180(self.heading + theta)


    def get_max_speed(self) -> float:
        return self.max_speed

    def _move_agent(self, desired_speed: float, heading_error: float):
        """
        Use Dubins vehicle dynamics to move the agent given a desired speed and heading error.

        Args:
            desired speed: desired speed, in m/s
            heading_error: heading error, in deg
        """

        new_speed = clip(desired_speed, self.min_speed, self.max_speed)

        desired_turn_rate = np.deg2rad(heading_error / self.dt)

        desired_turn_radius = new_speed / desired_turn_rate

        new_turn_radius = max(desired_turn_radius, self.min_turn_radius)

        new_turn_rate = np.rad2deg(new_speed / new_turn_radius)

        new_heading = self.heading + np.sign(heading_error) * new_turn_rate * self.dt

        # Propagate vehicle position based on new_heading and new_speed
        hdg_rad = np.deg2rad(self.heading)
        new_hdg_rad = np.deg2rad(new_heading)
        avg_speed = (new_speed + self.speed) / 2.0
        if self.gps_env:
            avg_speed = avg_speed / self.meters_per_mercator_xy
        s = np.sin(new_hdg_rad) + np.sin(hdg_rad)
        c = np.cos(new_hdg_rad) + np.cos(hdg_rad)
        avg_hdg = np.arctan2(s, c)
        # Note: sine/cos swapped because of the heading / angle difference
        new_ag_pos = [
            self.pos[0] + np.sin(avg_hdg) * avg_speed * self.dt,
            self.pos[1] + np.cos(avg_hdg) * avg_speed * self.dt,
        ]

        self.prev_pos = self.pos
        self.pos = np.asarray(new_ag_pos)
        self.speed = clip(new_speed, 0.0, self.max_speed)
        self.heading = angle180(new_heading)



class SingleIntegrator(Dynamics):

    def __init__(self, max_speed: float = 10, max_turn_rate: float = 90, **kwargs):

        super().__init__(**kwargs)

        self.max_speed = max_speed
        self.max_turn_rate = max_turn_rate

    def reset(self):
        """
        Set all time-varying state/control values to their default initialization values.
        Do not change pos, speed, heading, is_tagged, has_flag, or on_own_side.
        """

        pass  # Nothing needed here

    def rotate(self, theta=180):
        """
        Set all time-varying state/control values to their default initialization values as in reset().
        Set speed to 0.
        Rotate heading theta degrees.
        Place agent at previous position.
        Do not change is_tagged, has_flag, or on_own_side.
        """

        prev_pos = self.prev_pos
        self.prev_pos = self.pos
        self.pos = prev_pos
        self.speed = 0
        self.heading = angle180(self.heading + theta)


    def get_max_speed(self) -> float:
        return self.max_speed

    def _move_agent(self, desired_speed: float, heading_error: float):
        """
        Use single-integrator unicycle dynamics to move the agent given a desired speed and heading error.

        Args:
            desired speed: desired speed, in m/s
            heading_error: heading error, in deg
        """

        new_speed = clip(desired_speed, -self.max_speed, self.max_speed)
        turn_rate = clip(
            heading_error / self.dt, -self.max_turn_rate, self.max_turn_rate
        )
        new_heading = self.heading + turn_rate * self.dt

        # Propagate vehicle position based on new_heading and new_speed
        hdg_rad = np.deg2rad(self.heading)
        new_hdg_rad = np.deg2rad(new_heading)
        avg_speed = (new_speed + self.speed) / 2.0
        if self.gps_env:
            avg_speed = avg_speed / self.meters_per_mercator_xy
        s = np.sin(new_hdg_rad) + np.sin(hdg_rad)
        c = np.cos(new_hdg_rad) + np.cos(hdg_rad)
        avg_hdg = np.arctan2(s, c)
        # Note: sine/cos swapped because of the heading / angle difference
        new_ag_pos = [
            self.pos[0] + np.sin(avg_hdg) * avg_speed * self.dt,
            self.pos[1] + np.cos(avg_hdg) * avg_speed * self.dt,
        ]

        self.prev_pos = self.pos
        self.pos = np.asarray(new_ag_pos)
        self.speed = clip(new_speed, 0.0, self.max_speed)
        self.heading = angle180(new_heading)



class LargeUSV(Dynamics):

    def __init__(
        self,
        max_speed: float = 12,  # meters / s
        speed_factor: float = (
            20.0 / 3
        ),  # multiplicative factor for desired_speed -> desired_thrust
        thrust_map: np.ndarray = np.array(  # piecewise linear mapping from desired_thrust to speed
            [[-100, 0, 20, 40, 60, 80, 100], [-3, 0, 3, 6, 9, 12, 12]]
        ),
        max_thrust: float = 70,  # limit on vehicle thrust
        max_rudder: float = 100,  # limit on vehicle rudder actuation
        turn_loss: float = 0.85,
        turn_rate: float = 50,
        max_acc: float = 0.5,  # meters / s**2
        max_dec: float = 0.5,  # meters / s**2
        **kwargs,
    ):

        super().__init__(**kwargs)

        self.max_speed = max_speed
        self.speed_factor = speed_factor
        self.thrust_map = thrust_map
        self.max_thrust = max_thrust
        self.max_rudder = max_rudder
        self.turn_loss = turn_loss
        self.turn_rate = turn_rate
        self.max_acc = max_acc
        self.max_dec = max_dec

        self.state["thrust"] = 0

        self._pid_controllers = {
            "speed": PID(dt=kwargs["dt"], kp=1.0, ki=0.0, kd=0.0, integral_max=0.07),
            "heading": PID(
                dt=kwargs["dt"], kp=0.35, ki=0.0, kd=0.07, integral_max=0.07
            ),
        }

    def reset(self):
        """
        Set all time-varying state/control values to their default initialization values.
        Do not change pos, speed, heading, is_tagged, has_flag, or on_own_side.
        """

        self.state["thrust"] = 0

    def rotate(self, theta=180):
        """
        Set all time-varying state/control values to their default initialization values as in reset().
        Set speed to 0.
        Rotate heading theta degrees.
        Place agent at previous position.
        Do not change is_tagged, has_flag, or on_own_side.
        """

        prev_pos = self.prev_pos
        self.prev_pos = self.pos
        self.pos = prev_pos
        self.speed = 0
        self.heading = angle180(self.heading + theta)

        self.state["thrust"] = 0

    def get_max_speed(self) -> float:
        return self.max_speed

    def _move_agent(self, desired_speed: float, heading_error: float):
        """
        Use MOOS-IVP default dynamics to move the agent given a desired speed and heading error.
        Adapted from https://oceanai.mit.edu/ivpman/pmwiki/pmwiki.php?n=IvPTools.USimMarineV22

        Args:
            desired speed: desired speed, in m/s
            heading_error: heading error, in deg
        """

        # desired heading is relative to current heading
        speed_error = desired_speed - self.speed
        desired_speed = self._pid_controllers["speed"](speed_error)
        desired_rudder = self._pid_controllers["heading"](heading_error)

        desired_thrust = self.state["thrust"] + self.speed_factor * desired_speed

        desired_thrust = clip(desired_thrust, -self.max_thrust, self.max_thrust)
        desired_rudder = clip(desired_rudder, -self.max_rudder, self.max_rudder)

        # propagate vehicle speed
        raw_speed = np.interp(
            desired_thrust, self.thrust_map[0, :], self.thrust_map[1, :]
        )
        new_speed = min(
            raw_speed * 1 - ((abs(desired_rudder) / 100) * self.turn_loss),
            self.max_speed,
        )
        if (new_speed - self.speed) / self.dt > self.max_acc:
            new_speed = self.speed + self.max_acc * self.dt
        elif (self.speed - new_speed) / self.dt > self.max_dec:
            new_speed = self.speed - self.max_dec * self.dt

        # propagate vehicle heading
        raw_d_hdg = desired_rudder * (self.turn_rate / 100) * self.dt
        thrust_d_hdg = raw_d_hdg * (1 + (abs(desired_thrust) - 50) / 50)

        # eliminated to fix heading error when agent is slowing down and turning
        
        # if desired_thrust < 0:
        #     thrust_d_hdg = -thrust_d_hdg

        self.state["thrust"] = desired_thrust

        # if not moving, then can't turn
        if (new_speed + self.speed) / 2.0 < 0.5:
            thrust_d_hdg = 0.0
        new_heading = angle180(self.heading + thrust_d_hdg)

        # Propagate vehicle position based on new_heading and new_speed
        hdg_rad = np.deg2rad(self.heading)
        new_hdg_rad = np.deg2rad(new_heading)
        avg_speed = (new_speed + self.speed) / 2.0
        if self.gps_env:
            avg_speed = avg_speed / self.meters_per_mercator_xy
        s = np.sin(new_hdg_rad) + np.sin(hdg_rad)
        c = np.cos(new_hdg_rad) + np.cos(hdg_rad)
        avg_hdg = np.arctan2(s, c)
        # Note: sine/cos swapped because of the heading / angle difference
        new_ag_pos = [
            self.pos[0] + np.sin(avg_hdg) * avg_speed * self.dt,
            self.pos[1] + np.cos(avg_hdg) * avg_speed * self.dt,
        ]

        self.prev_pos = self.pos
        self.pos = np.asarray(new_ag_pos)
        self.speed = clip(new_speed, 0.0, self.max_speed)
        self.heading = angle180(new_heading)


class Heron(Dynamics):

    def __init__(
        self,
        max_speed: float = 3.5,  # meters / s
        speed_factor: float = 20.0,  # multiplicative factor for desired_speed -> desired_thrust
        thrust_map: np.ndarray = np.array(  # piecewise linear mapping from desired_thrust to speed
            [[-100, 0, 20, 40, 60, 80, 100], [-2, 0, 1, 2, 3, 5, 5]]
        ),
        max_thrust: float = 70,  # limit on vehicle thrust
        max_rudder: float = 100,  # limit on vehicle rudder actuation
        turn_loss: float = 0.85,
        turn_rate: float = 70,
        max_acc: float = 1,  # meters / s**2
        max_dec: float = 1,  # meters / s**2
        **kwargs,
    ):

        super().__init__(**kwargs)

        self.max_speed = max_speed
        self.speed_factor = speed_factor
        self.thrust_map = thrust_map
        self.max_thrust = max_thrust
        self.max_rudder = max_rudder
        self.turn_loss = turn_loss
        self.turn_rate = turn_rate
        self.max_acc = max_acc
        self.max_dec = max_dec

        self.state["thrust"] = 0

        self._pid_controllers = {
            "speed": PID(dt=kwargs["dt"], kp=1.0, ki=0.0, kd=0.0, integral_max=0.07),
            "heading": PID(
                dt=kwargs["dt"], kp=0.35, ki=0.0, kd=0.07, integral_max=0.07
            ),
        }

    def reset(self):
        """
        Set all time-varying state/control values to their default initialization values.
        Do not change pos, speed, heading, is_tagged, has_flag, or on_own_side.
        """

        self.state["thrust"] = 0

    def rotate(self, theta=180):
        """
        Set all time-varying state/control values to their default initialization values as in reset().
        Set speed to 0.
        Rotate heading theta degrees.
        Place agent at previous position.
        Do not change is_tagged, has_flag, or on_own_side.
        """

        prev_pos = self.prev_pos
        self.prev_pos = self.pos
        self.pos = prev_pos
        self.speed = 0
        self.heading = angle180(self.heading + theta)

        self.state["thrust"] = 0

    def get_max_speed(self) -> float:
        return self.max_speed

    def _move_agent(self, desired_speed: float, heading_error: float):
        """
        Use MOOS-IVP default dynamics to move the agent given a desired speed and heading error.
        Adapted from https://oceanai.mit.edu/ivpman/pmwiki/pmwiki.php?n=IvPTools.USimMarineV22

        Args:
            desired speed: desired speed, in m/s
            heading_error: heading error, in deg
        """

        # desired heading is relative to current heading
        speed_error = desired_speed - self.speed
        desired_speed = self._pid_controllers["speed"](speed_error)
        desired_rudder = self._pid_controllers["heading"](heading_error)

        desired_thrust = self.state["thrust"] + self.speed_factor * desired_speed

        desired_thrust = clip(desired_thrust, -self.max_thrust, self.max_thrust)
        desired_rudder = clip(desired_rudder, -self.max_rudder, self.max_rudder)

        # propagate vehicle speed
        raw_speed = np.interp(
            desired_thrust, self.thrust_map[0, :], self.thrust_map[1, :]
        )
        new_speed = min(
            raw_speed * 1 - ((abs(desired_rudder) / 100) * self.turn_loss),
            self.max_speed,
        )
        if (new_speed - self.speed) / self.dt > self.max_acc:
            new_speed = self.speed + self.max_acc * self.dt
        elif (self.speed - new_speed) / self.dt > self.max_dec:
            new_speed = self.speed - self.max_dec * self.dt

        # propagate vehicle heading
        raw_d_hdg = desired_rudder * (self.turn_rate / 100) * self.dt
        thrust_d_hdg = raw_d_hdg * (1 + (abs(desired_thrust) - 50) / 50)

        # eliminated to fix heading error when agent is slowing down and turning

        # if desired_thrust < 0:
        #     thrust_d_hdg = -thrust_d_hdg

        self.state["thrust"] = desired_thrust

        # if not moving, then can't turn
        if (new_speed + self.speed) / 2.0 < 0.5:
            thrust_d_hdg = 0.0
        new_heading = angle180(self.heading + thrust_d_hdg)

        # Propagate vehicle position based on new_heading and new_speed
        hdg_rad = np.deg2rad(self.heading)
        new_hdg_rad = np.deg2rad(new_heading)
        avg_speed = (new_speed + self.speed) / 2.0
        if self.gps_env:
            avg_speed = avg_speed / self.meters_per_mercator_xy
        s = np.sin(new_hdg_rad) + np.sin(hdg_rad)
        c = np.cos(new_hdg_rad) + np.cos(hdg_rad)
        avg_hdg = np.arctan2(s, c)
        # Note: sine/cos swapped because of the heading / angle difference
        new_ag_pos = [
            self.pos[0] + np.sin(avg_hdg) * avg_speed * self.dt,
            self.pos[1] + np.cos(avg_hdg) * avg_speed * self.dt,
        ]

        self.prev_pos = self.pos
        self.pos = np.asarray(new_ag_pos)
        self.speed = clip(new_speed, 0.0, self.max_speed)
        self.heading = angle180(new_heading)



class Drone(Dynamics):

    def __init__(self, max_speed: float = 10, **kwargs):
        super().__init__(**kwargs)

        self.max_speed = max_speed

        addl_state = {
            "pitch": 0,
            "roll": 0,
            "yaw": 0,
            "pitch_rate": 0,
            "roll_rate": 0,
            "yaw_rate": 0,
            "x_vel": 0,
            "y_vel": 0,
        }
        self.state.update(addl_state)

    def reset(self):
        """
        Set all time-varying state/control values to their default initialization values.
        Do not change pos, speed, heading, is_tagged, has_flag, or on_own_side.
        """

        new_state = {
            "pitch": 0,
            "roll": 0,
            "yaw": 0,
            "pitch_rate": 0,
            "roll_rate": 0,
            "yaw_rate": 0,
            "x_vel": 0,
            "y_vel": 0,
        }
        self.state.update(new_state)

    def rotate(self, theta=180):
        """
        Set all time-varying state/control values to their default initialization values as in reset().
        Set speed to 0.
        Rotate heading theta degrees.
        Place agent at previous position.
        Do not change is_tagged, has_flag, or on_own_side.
        """

        prev_pos = self.prev_pos
        self.prev_pos = self.pos
        self.pos = prev_pos
        self.speed = 0
        self.heading = angle180(self.heading + theta)

        new_state = {
            "pitch": 0,
            "roll": 0,
            "yaw": 0,
            "pitch_rate": 0,
            "roll_rate": 0,
            "yaw_rate": 0,
            "x_vel": 0,
            "y_vel": 0,
        }
        self.state.update(new_state)

    def get_max_speed(self) -> float:
        return self.max_speed

    def _move_agent(self, desired_speed: float, heading_error: float):
        """
        Use quadcopter dynamics to move the agent given a desired speed and heading error.
        Adapted from https://github.com/AtsushiSakai/PythonRobotics?tab=readme-ov-file#drone-3d-trajectory-following

        Args:
            desired speed: desired speed, in m/s
            heading_error: heading error, in deg
        """

        desired_speed = clip(desired_speed, 0, self.max_speed)

        # Constants
        g = 9.81
        m = 0.2
        Ixx = 1
        Iyy = 1
        Izz = 1

        # PID control coefficients
        Kp_x = 1
        Kp_y = 1
        Kp_z = 1
        Kp_roll = 100
        Kp_pitch = 100
        Kp_yaw = 25

        Kd_x = 1
        Kd_y = 1
        Kd_z = 1
        Kd_roll = 5
        Kd_pitch = 5
        Kd_yaw = 5

        # Convert heading error (deg) to desired yaw
        self.state["yaw"] = np.deg2rad(self.heading)
        yaw_error = np.deg2rad(heading_error)
        des_yaw = self.state["yaw"] + yaw_error

        # Calculate desired acceleration in x and y directions
        des_x_vel = desired_speed * np.sin(des_yaw)
        cur_x_vel = self.state["x_vel"]
        des_x_acc = clip((des_x_vel - cur_x_vel) / self.dt, -10, 10)
        des_y_vel = desired_speed * np.cos(des_yaw)
        cur_y_vel = self.state["y_vel"]
        des_y_acc = clip((des_y_vel - cur_y_vel) / self.dt, -10, 10)

        # Placeholders for z for now so that it is easier to add in the future
        des_z_pos = 0
        des_z_vel = 0
        des_z_acc = 0
        z_pos = 0
        z_vel = 0

        # Calculate vertical thrust and roll, pitch, and yaw torques.
        thrust = m * (
            g + des_z_acc + Kp_z * (des_z_pos - z_pos) + Kd_z * (des_z_vel - z_vel)
        )

        roll_torque = (
            Kp_roll
            * (
                ((des_x_acc * np.cos(self.state["yaw"]) + des_y_acc * np.sin(self.state["yaw"])) / g)
                - self.state["roll"]
            )
            - Kd_roll * self.state["roll_rate"]
        )

        pitch_torque = (
            Kp_pitch
            * (
                ((des_x_acc * np.sin(self.state["yaw"]) - des_y_acc * np.cos(self.state["yaw"])) / g)
                - self.state["pitch"]
            )
            - Kd_pitch * self.state["pitch_rate"]
        )

        yaw_torque = Kp_yaw * (des_yaw - self.state["yaw"]) - Kd_yaw * self.state["yaw_rate"]

        # Get roll, pitch, and yaw rates from torques and moments of inertia
        self.state["roll_rate"] += roll_torque * self.dt / Ixx
        self.state["pitch_rate"] += pitch_torque * self.dt / Iyy
        self.state["yaw_rate"] += yaw_torque * self.dt / Izz

        # Propagate roll, pitch, and yaw (and heading for proper rendering)
        self.state["roll"] += self.state["roll_rate"] * self.dt
        self.state["pitch"] += self.state["pitch_rate"] * self.dt
        self.state["yaw"] += self.state["yaw_rate"] * self.dt
        self.state["yaw"] = np.arctan2(np.sin(self.state["yaw"]), np.cos(self.state["yaw"]))
        self.heading = np.rad2deg(self.state["yaw"])

        # Transform into world frame to get x, y, and z accelerations, velocities, and positions
        R = rotation_matrix(self.state["roll"], self.state["pitch"], self.state["yaw"])
        acc = (np.matmul(R, np.array([0, 0, thrust]).T) - np.array([0, 0, m * g]).T) / m
        x_acc = acc[0]
        y_acc = acc[1]
        z_acc = acc[2]
        self.state["x_vel"] = cur_x_vel + x_acc * self.dt
        self.state["y_vel"] = cur_y_vel + y_acc * self.dt
        z_vel += z_acc * self.dt
        z_pos += z_vel * self.dt

        avg_x_vel = (cur_x_vel + self.state["x_vel"]) / 2.0
        avg_y_vel = (cur_y_vel + self.state["y_vel"]) / 2.0
        if self.gps_env:
            avg_x_vel = avg_x_vel / self.meters_per_mercator_xy
            avg_y_vel = avg_y_vel / self.meters_per_mercator_xy

        x_pos = self.pos[0] + avg_x_vel * self.dt
        y_pos = self.pos[1] + avg_y_vel * self.dt

        self.prev_pos = self.pos
        self.pos = np.asarray([x_pos, y_pos])
        self.speed = np.sqrt(np.power(cur_x_vel, 2) + np.power(cur_y_vel, 2))



class DoubleIntegrator(Dynamics):

    def __init__(
        self,
        max_speed: float = 10,
        max_accel: float = 1,
        max_turn_rate: float = 90,
        max_angular_accel: float = 180,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.max_speed = max_speed
        self.max_accel = max_accel
        self.max_turn_rate = max_turn_rate
        self.max_angular_accel = max_angular_accel

        self.state["turn_rate"] = 0

    def reset(self):
        """
        Set all time-varying state/control values to their default initialization values.
        Do not change pos, speed, heading, is_tagged, has_flag, or on_own_side.
        """

        self.state["turn_rate"] = 0

    def rotate(self, theta=180):
        """
        Set all time-varying state/control values to their default initialization values as in reset().
        Set speed to 0.
        Rotate heading theta degrees.
        Place agent at previous position.
        Do not change is_tagged, has_flag, or on_own_side.
        """

        prev_pos = self.prev_pos
        self.prev_pos = self.pos
        self.pos = prev_pos
        self.speed = 0
        self.heading = angle180(self.heading + theta)

        self.state["turn_rate"] = 0

    def get_max_speed(self) -> float:
        return self.max_speed

    def _move_agent(self, desired_speed: float, heading_error: float):
        """
        Use double-integrator unicycle dynamics to move the agent given a desired speed and heading error.

        Args:
            desired speed: desired speed, in m/s
            heading_error: heading error, in deg
        """

        # Get and clip desired linear and angular acceleration
        desired_acc = (desired_speed - self.speed) / self.dt

        desired_turn_rate = heading_error / self.dt
        desired_alpha = (desired_turn_rate - self.state["turn_rate"]) / self.dt

        desired_acc = clip(desired_acc, -self.max_accel, self.max_accel)
        desired_alpha = clip(
            desired_alpha, -self.max_angular_accel, self.max_angular_accel
        )

        # Calculate new linear speed and turn rate
        new_speed = self.speed + desired_acc * self.dt
        new_speed = clip(new_speed, -self.max_speed, self.max_speed)

        new_turn_rate = self.state["turn_rate"] + desired_alpha * self.dt
        new_turn_rate = clip(new_turn_rate, -self.max_turn_rate, self.max_turn_rate)

        self.state["turn_rate"] = new_turn_rate
        new_heading = self.heading + new_turn_rate * self.dt

        # Propagate vehicle position based on new speed and heading
        hdg_rad = np.deg2rad(self.heading)
        new_hdg_rad = np.deg2rad(new_heading)
        avg_speed = (new_speed + self.speed) / 2.0
        if self.gps_env:
            avg_speed = avg_speed / self.meters_per_mercator_xy
        s = np.sin(new_hdg_rad) + np.sin(hdg_rad)
        c = np.cos(new_hdg_rad) + np.cos(hdg_rad)
        avg_hdg = np.arctan2(s, c)
        # Note: sine/cos swapped because of the heading / angle difference
        new_ag_pos = [
            self.pos[0] + np.sin(avg_hdg) * avg_speed * self.dt,
            self.pos[1] + np.cos(avg_hdg) * avg_speed * self.dt,
        ]

        self.prev_pos = self.pos
        self.pos = np.asarray(new_ag_pos)
        self.speed = clip(new_speed, 0.0, self.max_speed)
        self.heading = angle180(new_heading)

