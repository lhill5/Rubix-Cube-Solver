import pygame
from RubixCube import RubixCube
from Rubix_Solver import Solver


def main():
    rubixCube = RubixCube(3, 1.5)
    rubixCube.rotate_right(repeat=0.25)
    rubixCube.rotate_up(repeat=0.25)
    rubixCube.mainloop()

    # create rubix cube
    # create solver with rubix cube object
    # create graphics object for drawing rubix cube



if __name__ == '__main__':
    main()
    pygame.quit()
    quit()
