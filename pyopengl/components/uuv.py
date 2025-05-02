from OpenGL.GL import *
from OpenGL.GLU import *
from .game_object import GameObject
from .drone import Drone
import math


# extension of drone class with restrictions on xz-axis movement
class UUV(Drone):
    def __init__(self, color=(1.0, 0.0, 0.0), size=1.0):
        # get from super class
        super().__init__(color, size)

    # new restrictions to up and down movement...
    def move_upward(self):
        # calculate new position
        new_y = self.position[1] + self.speed
        
        if self.environment:
            half_height = self.environment.height / 2
            
            # Only update if within bounds and not colliding
            if (-half_height < new_y < 0):
                self.position[1] = new_y

    def move_downward(self):
        # calculate new position
        new_y = self.position[1] - self.speed
        
        if self.environment:
            half_height = self.environment.height / 2
            
            # Only update if within bounds and not colliding
            if (-half_height < new_y < 0):
                self.position[1] = new_y

