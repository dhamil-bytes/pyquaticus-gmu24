from OpenGL.GLUT import glutInit
from pyopengl.bound import execute_game

def main():
    print("this is a test")

    print("checking pyopengl installs")
    if not bool(glutInit):
        print("Failed OpenGL.GLUT")
        return
    else:
        print("GLUT working properly.. proceeding")
    
    print("executing pyopengl sim")
    execute_game()


if __name__ == "__main__":
    main()