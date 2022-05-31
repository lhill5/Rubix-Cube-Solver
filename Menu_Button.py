from OpenGL.GL import *
from graphics_misc import *


class Color_Button:
    def __init__(self, id):
        self.id = id

    def draw(self, x: float, y: float, color: list):
        glPushMatrix()

        square_vertices = shift(x, y)

        glBegin(GL_QUADS)
        for surf in square_surfaces:
            glColor3fv(color)
            for v in surf:
                glVertex3fv(square_vertices[v])
        glEnd()

        glPopMatrix()
