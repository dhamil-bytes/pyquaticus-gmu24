import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from .game_object import GameObject
from .drone import Drone
from .home_base import HomeBase
from .flag import Flag
from .divider_wall import DividerWall, Equator
from .rectangle import Rectangle

from typing import List

class Environment(GameObject):
    def __init__(self, width=20, height=10, depth=20):
        super().__init__()
        self.width = width
        self.height = height
        self.depth = depth
        self.rotation_x = 0
        self.rotation_y = 0
        self.last_mouse_pos = None
        
        # Store game objects
        self.drone1 = None
        self.drone2 = None
        self.base1 = None
        self.base2 = None
        self.flag1 = None
        self.flag2 = None
        self.rectangle = None
        
    def handle_mouse(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                self.last_mouse_pos = pygame.mouse.get_pos()
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click release
                self.last_mouse_pos = None
                
        elif event.type == pygame.MOUSEMOTION:
            if self.last_mouse_pos is not None:  # If dragging
                current_pos = pygame.mouse.get_pos()
                delta_x = current_pos[0] - self.last_mouse_pos[0]
                delta_y = current_pos[1] - self.last_mouse_pos[1]
                
                # Update rotation
                self.rotation_y += delta_x * 0.5
                self.rotation_x += delta_y * 0.5
                
                self.last_mouse_pos = current_pos
        
    def set_drone_objects(self, drone1, drone2, pos1=[-10, 0, 0], pos2=[10, 0, 0]):
        # Store references to game objects
        self.drone1 = drone1
        self.drone2 = drone2
        
        # Set environment reference in drones for boundary checking
        self.drone1.environment = self
        self.drone2.environment = self
        
        # Position drones in the middle
        self.drone1.position = pos1  # Left center
        self.drone2.position = pos2   # Right center
        
        # Make drones face each other
        self.drone1.rotation = [0, 90, 0]   # Face right
        self.drone2.rotation = [0, -90, 0]  # Face left
        
    
    def set_flag_objects(self, flag1, flag2, base1, base2):
        # setting base
        self.base1 = base1
        self.base2 = base2
        # Position bases on the floor
        self.base1.position = [-15, 0, 0]   # Left front
        self.base2.position = [15, 0, 0]    # Right front
        
        # setting flags
        self.flag1 = flag1
        self.flag2 = flag2
        # Position flags on their bases
        self.flag1.position = [-15, 0, 0]   # On base1
        self.flag2.position = [15, 0, 0]    # On base2
        
        

    # includes divider wall
    def set_obstacle(self):
        # divider wall
        self.divider_wall = DividerWall(height=self.height, depth=self.depth)
        self.divider_wall.position = [0,0-(self.height/2),0]

        # equator
        self.equater_wall = Equator(width=self.width, depth=self.depth)
        self.equater_wall.position = [0,0,0]


        # Position rectangle in the middle and rotate it
        self.rectangle = Rectangle()
        self.rectangle.position = [0, 0, 0]  # Center on floor
        self.rectangle.rotation = [0, 75, 0]  # Rotate 30 degrees left around Y axis

    def update_drone_pos(self, reset=False, drone1=True, drone2=True, pos1=[-10,0,0], pos2=[10,0,0]):          
        # do something
        if reset:
            # Position drones in the middle
            self.drone1.position = [-10,0,0]  # Left center
            self.drone2.position = [10,0,0]   # Right center
            
            # Make drones face each other
            self.drone1.rotation = [0, 90, 0]   # Face right
            self.drone2.rotation = [0, -90, 0]  # Face left
        else:
            if drone1:
                self.drone1.position = pos1
            if drone2:
                self.drone2.position = pos2
    
    def draw(self):
        # Save the current matrix and apply base transformations
        glPushMatrix()
        super().apply_transformations()
        
        # Apply additional rotations for mouse control
        glRotatef(self.rotation_x, 1, 0, 0)
        glRotatef(self.rotation_y, 0, 1, 0)
        
        # Draw bases first (they're on the ground)
        if self.base1 and self.base2:
            # Draw first base
            glPushMatrix()
            self.base1.apply_transformations()
            self.base1.draw()
            glPopMatrix()
            
            # Draw second base
            glPushMatrix()
            self.base2.apply_transformations()
            self.base2.draw()
            glPopMatrix()
        
        # Draw flags
        if self.flag1 and self.flag2:
            glPushMatrix()
            self.flag1.apply_transformations()
            self.flag1.draw()
            glPopMatrix()
            
            glPushMatrix()
            self.flag2.apply_transformations()
            self.flag2.draw()
            glPopMatrix()
        
        # Draw drones before the wall for proper transparency
        # Define the vertices of the rectangular container
        w, h, d = self.width/2, self.height/2, self.depth/2
        vertices = [
            # Bottom face
            [-w, -h, -d], [w, -h, -d], [w, -h, d], [-w, -h, d],
            # Top face
            [-w, h, -d], [w, h, -d], [w, h, d], [-w, h, d]
        ]

        # Draw only edges with thick black lines
        glLineWidth(4.0)
        glColor3f(0.0, 0.0, 0.0)  # Black color for edges
        
        # Define the edges of the box (12 edges in total)
        edges = [
            # Bottom square
            (0, 1), (1, 2), (2, 3), (3, 0),
            # Top square
            (4, 5), (5, 6), (6, 7), (7, 4),
            # Vertical edges
            (0, 4), (1, 5), (2, 6), (3, 7)
        ]
        
        # Draw edges before wall for proper transparency
        glBegin(GL_LINES)
        for edge in edges:
            for vertex_index in edge:
                glVertex3fv(vertices[vertex_index])
        glEnd()
        
        if self.drone1 and self.drone2:
            # Draw first drone
            glPushMatrix()
            self.drone1.apply_transformations()
            self.drone1.draw()
            glPopMatrix()
            
            # Draw second drone
            glPushMatrix()
            self.drone2.apply_transformations()
            self.drone2.draw()
            glPopMatrix()
            
        # Draw divider wall
        self.divider_wall.draw()
        
        self.equater_wall.draw()
        
        # Draw rhombus
        if self.rectangle.visible:
            glPushMatrix()
            self.rectangle.draw()
            glPopMatrix()
        
        glPopMatrix()  # Pop the environment matrix
