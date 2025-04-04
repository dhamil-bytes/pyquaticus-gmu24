"""
Team: Pyquaticus
Diane Hamilton
George Mason University

drones.py
    initializes drone entities for some UAV or UUV
"""

import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

from abc import ABC, abstractmethod

# abstract drone class that handles movement
class Drone:
    def __init__(self, x=0, y=0, z=0):
        self.position = [x, y, z]

    @property
    @abstractmethod
    def bounds(self):
        """Each subclass must define its own movement constraints"""
        pass

    @abstractmethod
    def draw(self):
        """Each subclass must define its own draw constraints"""
        pass
    
    def move(self, dx, dy, dz):
        """
        move the object within the bounding box

        Args:
            dx (int): displacement on the x axis from original x position
            dy (int): displacement on the y axis from original y position
            dz (int): displacement on the z axis from original z position
            bounds (dict): {
                            'x': (min_x(int), max_x(int)), 
                            'y': (min_y(int), max_y(int)),
                            'z': (min_z(int), max_z(int))
                            }
        """

        x, y, z = self.position
        min_x, max_x = self.bounds.get('x')
        min_y, max_y = self.bounds.get('y')
        min_z, max_z = self.bounds.get('z')

        new_x = min(max(x + dx, min_x), max_x)
        new_y = min(max(y + dy, min_y), max_y)
        new_z = min(max(z + dz, min_z), max_z)
        self.position = [new_x, new_y, new_z]


# assigns UAV as baby class of Drone
# adopts all attributes of Drone class
class UAV(Drone):
    def __init__(self, x=0, y=50, z=0):
        # get superclass constructor
        super().__init__(x,y,z)
        
    # apply bounds constraint to the unmanned aerial vehicle
    @property
    def bounds(self):
        return {
                'x': (-1, 100),
                'y': (49, 100),
                'z': (-1, 100)
                }
    
    def draw(self):
        """Draws the Drone as a simple 3D cube."""
        vertices = [
            # Front face
            (-1.0, -1.0,  1.0), ( 1.0, -1.0,  1.0), ( 1.0,  1.0,  1.0), (-1.0,  1.0,  1.0),
            # Back face
            (-1.0, -1.0, -1.0), (-1.0,  1.0, -1.0), ( 1.0,  1.0, -1.0), ( 1.0, -1.0, -1.0),
            # Left face
            (-1.0, -1.0, -1.0), (-1.0, -1.0,  1.0), (-1.0,  1.0,  1.0), (-1.0,  1.0, -1.0),
            # Right face
            ( 1.0, -1.0, -1.0), ( 1.0, -1.0,  1.0), ( 1.0,  1.0,  1.0), ( 1.0,  1.0, -1.0),
            # Top face
            (-1.0,  1.0, -1.0), (-1.0,  1.0,  1.0), ( 1.0,  1.0,  1.0), ( 1.0,  1.0, -1.0),
            # Bottom face
            (-1.0, -1.0, -1.0), ( 1.0, -1.0, -1.0), ( 1.0, -1.0,  1.0), (-1.0, -1.0,  1.0)
        ]

        # Cube indices to define faces (quads)
        indices = [
            (0, 1, 2, 3),  # front face
            (4, 5, 6, 7),  # back face
            (8, 9, 10, 11),  # left face
            (12, 13, 14, 15),  # right face
            (16, 17, 18, 19),  # top face
            (20, 21, 22, 23)  # bottom face
        ]
        
        glPushMatrix()
        glTranslatef(*self.position)
        glColor3f(1.0, 0.0, 0.0)  # Red color for the cube
        
        glBegin(GL_QUADS)
        for face in indices:
            for vertex in face:
                glVertex3fv(vertices[vertex])
        glEnd()

        glPopMatrix()

# assigns UUV as baby class of Drone
# adopts all attributes of Drone class
class UUV(Drone):
    def __init__(self, x=0, y=0, z=0):
        # get superclass constructor
        super().__init__(x,y,z)

    # apply bounds constraint to the unmanned underwater vehicle
    @property
    def bounds(self):
        return {
                'x': (-1, 100), 
                'y': (-1, 50),
                'z': (-1, 100)
                }    

    def draw(self):
        """Draws the Drone as a simple 3D cube."""
        vertices = [
            # Front face
            (-1.0, -1.0,  1.0), ( 1.0, -1.0,  1.0), ( 1.0,  1.0,  1.0), (-1.0,  1.0,  1.0),
            # Back face
            (-1.0, -1.0, -1.0), (-1.0,  1.0, -1.0), ( 1.0,  1.0, -1.0), ( 1.0, -1.0, -1.0),
            # Left face
            (-1.0, -1.0, -1.0), (-1.0, -1.0,  1.0), (-1.0,  1.0,  1.0), (-1.0,  1.0, -1.0),
            # Right face
            ( 1.0, -1.0, -1.0), ( 1.0, -1.0,  1.0), ( 1.0,  1.0,  1.0), ( 1.0,  1.0, -1.0),
            # Top face
            (-1.0,  1.0, -1.0), (-1.0,  1.0,  1.0), ( 1.0,  1.0,  1.0), ( 1.0,  1.0, -1.0),
            # Bottom face
            (-1.0, -1.0, -1.0), ( 1.0, -1.0, -1.0), ( 1.0, -1.0,  1.0), (-1.0, -1.0,  1.0)
        ]

        # Cube indices to define faces (quads)
        indices = [
            (0, 1, 2, 3),  # front face
            (4, 5, 6, 7),  # back face
            (8, 9, 10, 11),  # left face
            (12, 13, 14, 15),  # right face
            (16, 17, 18, 19),  # top face
            (20, 21, 22, 23)  # bottom face
        ]
        
        glPushMatrix()
        glTranslatef(*self.position)
        glColor3f(0.0, 0.0, 1.0)  # Red color for the cube
        
        glBegin(GL_QUADS)
        for face in indices:
            for vertex in face:
                glVertex3fv(vertices[vertex])
        glEnd()

        glPopMatrix()