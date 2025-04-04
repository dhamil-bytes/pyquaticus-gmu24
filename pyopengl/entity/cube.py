"""
Team: Pyquaticus
Diane Hamilton
George Mason University

cube.py
    initializes cube world for drones to live in
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

class Environment:
    def __init__(self, size=50):
        # max of 100
        self.size = size  # The size of the cube boundary

    def draw_bounding_box(self):
        # Draw the bounding box (cube) that represents the environment.
        glPushMatrix()
        
        # Set color for the cube boundary (e.g., wireframe)
        glColor3f(0, 0, 0)  # Red for visualizing the boundary
        
        # Move the cube so that its minimum corner starts at (0,0,0)
        # glTranslatef(0, 0, -self.size / 2)
        
        half_size = self.size / 2  # Calculate half size for easier positioning
        vertices = [
            (-half_size, -half_size,  half_size),  # Front-bottom-left
            ( half_size, -half_size,  half_size),  # Front-bottom-right
            ( half_size,  half_size,  half_size),  # Front-top-right
            (-half_size,  half_size,  half_size),  # Front-top-left
            (-half_size, -half_size, -half_size),  # Back-bottom-left
            ( half_size, -half_size, -half_size),  # Back-bottom-right
            ( half_size,  half_size, -half_size),  # Back-top-right
            (-half_size,  half_size, -half_size),  # Back-top-left
        ]

        # Edges for the cube (pairs of vertex indices)
        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),  # Front face
            (4, 5), (5, 6), (6, 7), (7, 4),  # Back face
            (0, 4), (1, 5), (2, 6), (3, 7)   # Connect front and back faces
        ]

        # Draw the edges as lines
        glBegin(GL_LINES)
        for edge in edges:
            for vertex in edge:
                glVertex3fv(vertices[vertex])
        glEnd()
        
        glPopMatrix()