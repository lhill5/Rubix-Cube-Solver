from OpenGL.GL import *
from graphics_misc import *

# for each x,y,z record the color for the outward surface (manually code this)
# then in update function, say that before square color =


class Cube:
    def __init__(self, id, rubix_colors, N, scale):
        self.sides = ['B', 'L', 'F', 'R', 'U', 'D']
        self.colors = {side: None for side in self.sides}

        self.rubix_colors = rubix_colors
        self.N = N
        self.scale = scale

        self.current_i = [*id]
        self.x, self.y, self.z = self.current_i
        self.rot = [[1 if i == j else 0 for i in range(3)] for j in range(3)]

    def isAffected(self, axis, slice, dir):
        return self.current_i[axis] == slice

    def update(self, prev_state: dict, axis, slice, dir):
        if not self.isAffected(axis, slice, dir):
            return prev_state

        i, j = (axis + 1) % 3, (axis + 2) % 3
        for k in range(3):
            self.rot[k][i], self.rot[k][j] = -self.rot[k][j] * dir, self.rot[k][i] * dir

        # current color = new current color
        prev_index = self.current_i.copy()

        self.current_i[i], self.current_i[j] = (
            self.current_i[j] if dir < 0 else self.N - 1 - self.current_i[j],
            self.current_i[i] if dir > 0 else self.N - 1 - self.current_i[i]
        )

    def transformMat(self):
        scaleA = [[s * self.scale for s in a] for a in self.rot]
        scaleT = [(p - (self.N - 1) / 2) * 2.1 * self.scale for p in self.current_i]
        return [*scaleA[0], 0, *scaleA[1], 0, *scaleA[2], 0, *scaleT, 1]

    def draw(self, col, surf, vert, animate, angle, axis, slice, dir, ang_x, ang_y):
        glPushMatrix()

        glRotatef(ang_y, 0, 1, 0)
        glRotatef(ang_x, 1, 0, 0)

        if animate and self.isAffected(axis, slice, dir):
            glRotatef(angle * dir, *[1 if i == axis else 0 for i in range(3)])
        glMultMatrixf(self.transformMat())

        glBegin(GL_QUADS)

        for s in range(len(surf)):
            side, color, index, rgb_color = self.get_surface_color(s)
            self.colors[side] = color
            glColor3fv(rgb_color)

            for j in surf[s]:
                glVertex3fv(vertices[j])
        glEnd()
        glPopMatrix()

    def get_surface_color(self, surface):
        side = self.sides[surface]

        square_i = 0
        if side == 'F':
            square_i = (self.x + ((2 - self.y) * 3))
        elif side == 'L':
            square_i = (self.z + ((2 - self.y) * 3))
        elif side == 'R':
            square_i = (self.x + ((2 - self.y) * 3)) - self.z
        elif side == 'U':
            square_i = self.x + self.z * 3
        elif side == 'D':
            square_i = self.x + (2-self.z) * 3
        elif side == 'B':
            square_i = (2 - self.y) * 3 + (2 - self.x)
        else:
            print(f'error, {side} is an invalid side')
            exit(0)

        color_str = self.rubix_colors[side][square_i]
        side_color = colors_dict[color_str]

        return side, color_str, square_i, side_color

    def on_face(self, face):
        if face == 'front':
            return self.z == 2
        elif face == 'left':
            return self.x == 0
        elif face == 'right':
            return self.x == 2
        elif face == 'up':
            return self.y == 2
        elif face == 'down':
            return self.y == 0
        elif face == 'back':
            return self.z == 0
        else:
            pass
