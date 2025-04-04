"""
Team: Pyquaticus
Diane Hamilton
George Mason University

bound.py
    main loop for 3d visualizations
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

# import drones, env
from .entity.drone import UUV, UAV
from .entity.cube import Environment

# starts uuv and uav and environment variables
env = Environment()
uav = UAV()
uuv = UUV()

# create keybinds
# using wasd for uav
key_map_uav = {
    b'w': (0, 1, 0),
    b's': (0, -1, 0),
    b'a': (-1, 0, 0),
    b'd': (1, 0, 0),
    b' ': (0, 0, 1)
}

# using arrow keys for uuv
key_map_uuv = {
    pygame.K_UP: (0, 1, 0),
    pygame.K_DOWN: (0, -1, 0),
    pygame.K_LEFT: (-1, 0, 0),
    pygame.K_RIGHT: (1, 0, 0),
    pygame.K_RETURN: (0, 0, 1)
}


def setup():
    print("setting up background and enabling 3d rendering")
    
    # Set background color to white
    glClearColor(1, 1, 1, 1)  
    # Enable depth testing for 3D rendering
    glEnable(GL_DEPTH_TEST)

    # Set up perspective projection
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    
    # Set the perspective (field of view, aspect ratio, near and far planes)
    gluPerspective(45, 1.33, 0.1, 1000.0)  # FOV, aspect ratio, near plane, far plane
    
    # Switch back to modelview matrix
    glMatrixMode(GL_MODELVIEW)
    
    # Move the camera back a little so that the cube is visible
    glTranslatef(0.0, 0.0, -200.0)  # Adjust the camera position along the z-axis

def draw_scene():
    # print("drawing scene")
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    # Reset the view
    glLoadIdentity()

    # Draw the environment (the bounding box) and drones
    env.draw_bounding_box()
    # uav.draw()
    # uuv.draw()

    pygame.display.flip()  # Swap buffers for smooth animation

#  normal keyboard callback
def key_handler_uav(key, x, y):
    """Handle keyboard inputs for controlling drones."""
    if key in key_map_uav:
        uav.move(*key_map_uav.get(key))
    
    # Redraw the scene
    pygame.display.flip()

# special keyboard callback
def key_handler_uuv(key, x, y):
    if key in key_map_uuv:
        uuv.move(*key_map_uuv.get(key))

    # Redraw the scene
    pygame.display.flip()
    
# escape keyboard callback
# def key_handler_esc(key, x, y):
#     if key ==b'\x1b':
#         print("Escape key pressed. Annihilating window...")
#         glutLeaveMainLoop()  # Exits the GLUT main loop and closes the window
#         cleanup()  # Call a cleanup function to release any resources
#         return

# initialize and simulate movement
def simulate():
    # Initialize PyGame
    pygame.init()
    display = (800, 600)
    # OpenGL with Pygame window
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    
    setup()
    
    # event loop
    running = True
    while running:
        # loop thru all events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        draw_scene()
    pygame.quit()
    
    # x = sys.argv
    # print(x)
    # print(bool(glutInit))
    # glutInit(sys.argv)
    # glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    # glutInitWindowSize(800, 600)
    # glutCreateWindow("Drone Simulation")

    # # Set up scene
    # setup()

    # # Register display and keyboard functions
    # glutDisplayFunc(draw_scene)
    # glutKeyboardFunc(key_handler_uav)
    # glutSpecialFunc(key_handler_uuv)

    # # Start the GLUT event loop
    # glutMainLoop()

