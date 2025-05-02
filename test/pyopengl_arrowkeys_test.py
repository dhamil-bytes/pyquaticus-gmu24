import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import glutInit
from pyopengl.bound import Game

def main():
    print("this is a test")

    print("checking pyopengl installs")
    if not bool(glutInit):
        print("Failed OpenGL.GLUT")
        return
    else:
        print("GLUT working properly.. proceeding")
    
    print("executing pyopengl sim")

    game = Game()
    while True:
        current_time = pygame.time.get_ticks()
        delta_time = (current_time - game.last_time) / 1000.0  # Convert to seconds
        game.last_time = current_time

        if not game.handle_events():
            pygame.quit()
            return

        # Update game state
        game.update()
        
        # Clear the screen and depth buffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Reset the modelview matrix
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Apply camera transform
        game.camera.apply()
        
        # Draw the environment
        game.environment.draw()
        
        # Draw the 2D button on top
        game.draw_button()
        
        # Swap the display buffers
        pygame.display.flip()
        
        # Control the frame rate
        game.clock.tick(60)

if __name__ == "__main__":
    main()