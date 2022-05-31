import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *


vertices = (
    (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, -1),
    (1, -1, 1), (1, 1, 1), (-1, -1, 1), (-1, 1, 1)
)

edges = ((0, 1), (0, 3), (0, 4), (2, 1), (2, 3), (2, 7), (6, 3), (6, 4), (6, 7), (5, 1), (5, 4), (5, 7))
surfaces = ((0, 1, 2, 3), (3, 2, 7, 6), (6, 7, 5, 4), (4, 5, 1, 0), (1, 5, 7, 2), (4, 0, 3, 6))
colors = ((1, 0, 0), (0, 1, 0), (1, 0.5, 0), (1, 1, 0), (1, 1, 1), (0, 0, 1))


def shift(vertices, val):
    new_vertices = []
    for vert in vertices:
        new_vert = [vert[0] + val, vert[1], vert[2]]
        new_vertices.append(new_vert)

    return new_vertices


def Cube(vertices, id, angle):
    glPushMatrix()
    glRotatef(angle, 1, 0, 0)

    glBegin(GL_QUADS)
    for surface in surfaces:
        x = 0
        for vertex in surface:
            x += 1
            glColor3fv(colors[id])
            glVertex3fv(vertices[vertex])
    glEnd()
    glPopMatrix()


def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -10)
    ang = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        glRotatef(0, 1, 0, 0)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        Cube(shift(vertices, 2), 0, ang)
        Cube(shift(vertices, -2), 1, 0)
        ang += 5

        pygame.display.flip()
        pygame.time.wait(10)


main()
