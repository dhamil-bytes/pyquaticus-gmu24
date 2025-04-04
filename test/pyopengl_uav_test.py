from OpenGL.GLUT import glutInit
from pyopengl.bound import simulate

def main():
    print("this is a test")

    print("checking pyopengl installs")
    if not bool(glutInit):
        print("Failed OpenGL.GLUT")
        return
    else:
        print("GLUT working properly.. proceeding")
    
    print("executing pyopengl sim")
    simulate()


if __name__ == "__main__":
    main()