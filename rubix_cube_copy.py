import pygame
import random, json, os, time
from pygame.locals import *
from collections import defaultdict

from OpenGL.GL import *
from OpenGL.GLU import *

from graphics_misc import *
from Cube import Cube
from Menu import Menu
from Rubix_Solver import Solver


class RubixCube:
    def __init__(self, N, scale):
        self.init_graphics()
        self.solver = Solver(self)
        self.sides = ['back', 'left', 'front', 'right', 'up', 'down']
        self.face_colors = {side: ['' for _ in range(9)] for side in self.sides}

        self.animate, self.animate_ang, self.animate_speed = False, 0, 5
        self.horizontal_rotate, self.vertical_rotate = (0, 0), (0, 0)
        self.N = N

        # get colors of rubix cube from json file
        self.colors = read_rubix_cube_colors()

        cr = range(self.N)
        self.cubes = [Cube((x, y, z), self.colors, self.N, scale) for x in cr for y in cr for z in cr]

        # used to keep track of cube locations after rotation
        self.cube_ids = {(x, y, z): x*9 + y+3 * z for x in cr for y in cr for z in cr}
        self.prev_state = {cube_id: cube_id for cube_id in self.cube_ids.keys()}

        self.clicked = False
        self.menu = Menu()

        self.rot_cube = (0, 0)
        self.action = (0, 0, 0)
        self.ang_x, self.ang_y = 0, 0
        horizontal_rotate, self.vertical_rotate = (0, 0), (0, 0)
        self.animate, self.animate_ang, self.animate_speed = False, 0, 5

        self.rot_cube_map = {K_UP: (-1, 0), K_DOWN: (1, 0), K_LEFT: (0, -1), K_RIGHT: (0, 1)}
        self.rot_slice_map = {
            K_1: (0, 0, 1), K_2: (0, 1, 1), K_3: (0, 2, 1), K_4: (1, 0, 1), K_5: (1, 1, 1),
            K_6: (1, 2, 1), K_7: (2, 0, 1), K_8: (2, 1, 1), K_9: (2, 2, 1),
            K_F1: (0, 0, -1), K_F2: (0, 1, -1), K_F3: (0, 2, -1), K_F4: (1, 0, -1), K_F5: (1, 1, -1),
            K_F6: (1, 2, -1), K_F7: (2, 0, -1), K_F8: (2, 1, -1), K_F9: (2, 2, -1),
        }
        self.move_lookup = {
            K_F9: "F", K_9: "F'", K_F7: "B", K_7: "B'",
            K_1: "L", K_F1: "L'", K_F3: "R", K_3: "R'",
            K_F6: "U", K_6: "U'", K_F4: "D", K_4: "D'"
        }
        self.moves = []

    def init_graphics(self):
        pygame.init()
        display = (800, 600)
        pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
        glEnable(GL_DEPTH_TEST)

        glMatrixMode(GL_PROJECTION)
        gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)

    def mainloop(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == KEYDOWN:
                    # arrow keys for moving cube left/right/up/down
                    if event.key in self.rot_cube_map:
                        self.rot_cube = self.rot_cube_map[event.key]
                    if event.key == K_SPACE:
                        self.scramble()
                    if event.key == K_r:
                        self.reset_cube()
                    if event.key == K_s:
                        self.solver.solve_cube()

                    # key 1-9 to rotate cube
                    if not self.animate and event.key in self.rot_slice_map:
                        self.moves.append(event.key)
                        self.update_colors(event.key)
                        self.animate, self.action = True, self.rot_slice_map[event.key]

                if event.type == KEYUP:
                    if event.key in self.rot_cube_map:
                        self.rot_cube = (0, 0)
                if event.type == MOUSEBUTTONDOWN:
                    self.clicked = True
                elif event.type == MOUSEBUTTONUP:
                    self.clicked = False
                    self.horizontal_rotate = (0, 0)
                    self.vertical_rotate = (0, 0)

                if event.type == MOUSEMOTION:
                    # get different in current mouse position and previous mouse position
                    rel_x, rel_y = event.rel
                    rel_x = 0 if abs(rel_y) > abs(rel_x) else rel_x
                    rel_y = 0 if abs(rel_x) > abs(rel_y) else rel_y

                    if self.clicked:
                        if rel_y > 0:
                            self.vertical_rotate = (-1, 0)
                        elif rel_y < 0:
                            self.vertical_rotate = (1, 0)
                        else:
                            self.vertical_rotate = (0, 0)

                        if rel_x > 0:
                            self.horizontal_rotate = (0, 1)
                        elif rel_x < 0:
                            self.horizontal_rotate = (0, -1)
                        else:
                            self.horizontal_rotate = (0, 0)

                    # print(pygame.mouse.get_pos())

            self.ang_x += self.rot_cube[0] * 2
            self.ang_y += self.rot_cube[1] * 2

            self.ang_x += self.vertical_rotate[0] * 4
            self.ang_y += self.horizontal_rotate[1] * 4

            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            glTranslatef(0, 0, -40)

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            i = 0
            if self.animate:
                if self.animate_ang >= 90:
                    for cube in self.cubes:
                        self.prev_state = cube.update(self.prev_state, self.face_colors, *self.action)
                        for key, val in self.prev_state.items():
                            if key != val:
                                print(key, val)
                        i += 1

                    self.animate, self.animate_ang = False, 0

            for cube in self.cubes:
                cube.draw(colors, surfaces, vertices, self.animate, self.animate_ang, *self.action, self.ang_x, self.ang_y)

            self.menu.draw()

            if self.animate:
                self.animate_ang += self.animate_speed

            # get state of cube

            # for side in self.sides:
            #     for cube_id in self.cube_ids:
            #         if self.prev_state is None:
            #             breakpoint()

                    # prev_cube_id = self.prev_state[cube_id]
                    # prev_cube = self.cubes[self.cube_ids[prev_cube_id]]
                    # cube_colors = prev_cube.side_colors

                    # if prev_cube.on_face(face=side):
                    #     square_i = get_square_index(side, prev_cube.x, prev_cube.y, prev_cube.z)
                    #     self.face_colors[side][square_i] = cube_colors[side]

            for side in self.sides:
                print(f'side: {side}: {self.face_colors[side]}', end='')
            print()

            pygame.display.flip()
            pygame.time.wait(10)

    def scramble(self, num_rotations=20):
        possible_moves = list(self.move_lookup.values())

        for i in range(num_rotations):
            move = random.choice(possible_moves)
            self.rotate_from_str(move)

    def reset_cube(self):
        for m in self.moves[::-1]:
            try:
                move = self.move_lookup[m]
            except:
                breakpoint()
            opposite_move = get_opposite_move(move)
            self.rotate_from_str(opposite_move)
        self.moves = []

    def rotate_from_str(self, move):
        if move == "F":
            self.rotate_F()
        elif move == "F'":
            self.rotate_F_prime()
        elif move == "B":
            self.rotate_B()
        elif move == "B'":
            self.rotate_B_prime()
        elif move == "L":
            self.rotate_L()
        elif move == "L'":
            self.rotate_L_prime()
        elif move == "R":
            self.rotate_R()
        elif move == "R'":
            self.rotate_R_prime()
        elif move == "U":
            self.rotate_U()
        elif move == "U'":
            self.rotate_U_prime()
        elif move == "D":
            self.rotate_D()
        elif move == "D'":
            self.rotate_D_prime()
        else:
            print('error, invalid side rotation')
            exit(0)

    def rotate_down(self, repeat):
        cur_ang = self.ang_x
        while self.ang_x >= cur_ang - (90 * repeat):
            # print((self.ang_x), (90 * repeat))
            self.rotate(K_UP, repeat)

        self.reset_rotation()

    def rotate_up(self, repeat):
        cur_ang = self.ang_x
        while self.ang_x <= cur_ang + (90 * repeat):
            # print(abs(self.ang_x), abs(90 * repeat))
            self.rotate(K_DOWN, repeat)

        self.reset_rotation()

    def rotate_left(self, repeat):
        cur_ang = self.ang_y
        while self.ang_y <= cur_ang + (90 * repeat):
            # print(abs(self.ang_y), abs(90 * repeat))
            self.rotate(K_RIGHT, repeat)

        self.reset_rotation()

    def rotate_right(self, repeat):
        cur_ang = self.ang_y
        while self.ang_y >= cur_ang - (90 * repeat):
            # print(abs(self.ang_y), abs(90 * repeat))
            self.rotate(K_LEFT, repeat)

        self.reset_rotation()

    def rotate(self, dir, repeat=1):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        self.rot_cube = self.rot_cube_map[dir]
        self.ang_x += self.rot_cube[0] * 2
        self.ang_y += self.rot_cube[1] * 2

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0, 0, -40)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        for cube in self.cubes:
            cube.draw(colors, surfaces, vertices, self.animate, self.animate_ang, *self.action, self.ang_x, self.ang_y)

        pygame.display.flip()
        # pygame.time.wait(10)

    def reset_rotation(self):
        self.rot_cube = (0, 0)
        horizontal_rotate, self.vertical_rotate = (0, 0), (0, 0)

    def rotate_side(self):
        while self.animate:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            glTranslatef(0, 0, -40)

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            if self.animate:
                if self.animate_ang >= 90:
                    for cube in self.cubes:
                        self.prev_state = cube.update(self.prev_state, self.face_colors, *self.action)
                        if self.prev_state is None:
                            breakpoint()

                    self.animate, self.animate_ang = False, 0

            for cube in self.cubes:
                cube.draw(colors, surfaces, vertices, self.animate, self.animate_ang, *self.action, self.ang_x, self.ang_y)

            self.menu.draw()

            if self.animate:
                self.animate_ang += self.animate_speed

            pygame.display.flip()
            pygame.time.wait(10)

    def rotate_F(self):
        self.animate, self.action = True, self.rot_slice_map[K_F9]
        self.moves.append(K_F9)
        self.rotate_side()

    def rotate_F_prime(self):
        self.animate, self.action = True, self.rot_slice_map[K_9]
        self.moves.append(K_9)
        self.rotate_side()

    def rotate_B(self):
        self.animate, self.action = True, self.rot_slice_map[K_F7]
        self.moves.append(K_F7)
        self.rotate_side()

    def rotate_B_prime(self):
        self.animate, self.action = True, self.rot_slice_map[K_7]
        self.moves.append(K_7)
        self.rotate_side()

    def rotate_L(self):
        self.animate, self.action = True, self.rot_slice_map[K_1]
        self.moves.append(K_1)
        self.rotate_side()

    def rotate_L_prime(self):
        self.animate, self.action = True, self.rot_slice_map[K_F1]
        self.moves.append(K_F1)
        self.rotate_side()

    def rotate_R(self):
        self.animate, self.action = True, self.rot_slice_map[K_F3]
        self.moves.append(K_F3)
        self.rotate_side()

    def rotate_R_prime(self):
        self.animate, self.action = True, self.rot_slice_map[K_3]
        self.moves.append(K_3)
        self.rotate_side()

    def rotate_U(self):
        self.animate, self.action = True, self.rot_slice_map[K_F6]
        self.moves.append(K_F6)
        self.rotate_side()

    def rotate_U_prime(self):
        self.animate, self.action = True, self.rot_slice_map[K_6]
        self.moves.append(K_6)
        self.rotate_side()

    def rotate_D(self):
        self.animate, self.action = True, self.rot_slice_map[K_F4]
        self.moves.append(K_F4)
        self.rotate_side()

    def rotate_D_prime(self):
        self.animate, self.action = True, self.rot_slice_map[K_4]
        self.moves.append(K_4)
        self.rotate_side()

    def update_colors(self, key):
        pass


def read_rubix_cube_colors():
    mixed_cube = 'RubixCube_mixed.json'
    solved_cube = 'RubixCube_solved.json'
    with open(solved_cube, 'r') as file:
        data = json.load(file)
    return data


def get_side(index):
    side = ['back', 'left', 'front', 'right', 'up', 'down']
    return side[index]


def get_opposite_move(move):
    if len(move) == 1:
        return move + "'"
    else:
        return move[0]


def get_square_index(side, x, y, z):
    square_i = 0
    if side == 'front':
        square_i = (x + ((2 - y) * 3))
    elif side == 'left':
        square_i = (z + ((2 - y) * 3))
    elif side == 'right':
        square_i = (x + ((2 - y) * 3)) - z
    elif side == 'up':
        square_i = x + z * 3
    elif side == 'down':
        square_i = x + (2-z) * 3
    elif side == 'back':
        square_i = (2 - y) * 3 + (2 - x)
    else:
        print('error, invalid side')
        exit(0)

    return square_i
