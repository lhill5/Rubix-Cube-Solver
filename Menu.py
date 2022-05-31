from OpenGL.GL import *

from graphics_misc import *
from Menu_Button import Color_Button


class Menu:
    def __init__(self):
        self.buttons = [Color_Button(i) for i in range(6)]
        self.colors = list(colors)

    def draw(self):
        x, y = -12.5, 10

        glPushMatrix()
        glRotatef(0, 0, 0, 0)
        for square, color in zip(self.buttons, self.colors):
            square.draw(x, y, color)
            x += 5

        glPopMatrix()

