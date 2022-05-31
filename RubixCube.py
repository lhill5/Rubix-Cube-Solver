import pygame
import random, json, os, time
from pygame.locals import *
from collections import defaultdict
import re, copy
from multimethod import multimethod

from OpenGL.GL import *
from OpenGL.GLU import *

from graphics_misc import *
from Cube import Cube
from Menu import Menu
from Rubix_Solver import Solver

CW = -1
CCW = 1

# todo - replace MW and MH with corner/edge classes


class RubixCube:
    def __init__(self, N, scale):
        self.init_graphics()
        self.sides = ['B', 'L', 'F', 'R', 'U', 'D']  # back, left, front, right, up, down
        self.sides_by_color = ['B', 'O', 'G', 'R', 'W', 'Y']  # blue, orange, green, red, white, yellow
        self.color_words = ['blue', 'orange', 'green', 'red', 'white', 'yellow']

        # used to get left/right/up/etc. side relative to any side
        self.relative_sides = {"F": {"L": "L", "R": "R", "U": "U", "D": "D", "F": "F", "B": "B"},
                               "B": {"L": "R", "R": "L", "U": "U", "D": "D", "F": "B", "B": "F"},
                               "L": {"L": "B", "R": "F", "U": "U", "D": "D", "F": "L", "B": "R"},
                               "R": {"L": "F", "R": "B", "U": "U", "D": "D", "F": "R", "B": "L"},
                               "U": {"L": "L", "R": "R", "U": "B", "D": "F", "F": "U", "B": "D"},
                               "D": {"L": "L", "R": "R", "U": "F", "D": "B", "F": "D", "B": "U"}}

        self.relative_moves = {"F": {"L": "L", "R": "R", "U": "U", "D": "D", "F": "F", "B": "B"},
                               "B": {"L": "R'", "R": "L'", "U": "U", "D": "D", "F": "B'", "B": "F'"},
                               "L": {"L": "B", "R": "F", "U": "U", "D": "D", "F": "L'", "B": "R'"},
                               "R": {"L": "F'", "R": "B'", "U": "U", "D": "D", "F": "R", "B": "L"},
                               "U": {"L": "L", "R": "R", "U": "B'", "D": "F'", "F": "U", "B": "D"},
                               "D": {"L": "L", "R": "R", "U": "F", "D": "B", "F": "D'", "B": "U'"}}

        # used for indexing cube in a circular way, similar to how rotating the cube works
        # indices are circular, values are square
        self.circular_indices = [0, 1, 2, 5, 8, 7, 6, 3, 0]

        self.animate, self.animate_ang, self.animate_speed = False, 0, 5
        self.horizontal_rotate, self.vertical_rotate = (0, 0), (0, 0)
        self.N = N

        # get colors of rubix cube from json file, stays the same for rotation/turn code
        self.static_colors = read_rubix_cube_colors()
        # contains colors of each square for entire cube
        self.colors = self.get_rubix_faces()
        # contains side and index of each axis for easy indexing
        self.axis_squares = self.get_axis_squares()

        # used to return sequence of moves to solve the cube
        self.solver = Solver(self)

        cr = range(self.N)
        self.cubes = [Cube((x, y, z), self.static_colors, self.N, scale) for x in cr for y in cr for z in cr]

        # used to keep track of cube locations after rotation
        self.cube_ids = {(x, y, z): x * 9 + y + 3 * z for x in cr for y in cr for z in cr}
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
            K_1: (0, 0, -1), K_2: (0, 2, -1), K_3: (1, 0, -1),
            K_4: (1, 2, -1), K_5: (2, 0, -1), K_6: (2, 2, -1),
            K_F1: (0, 0, 1), K_F2: (0, 2, 1), K_F3: (1, 0, 1),
            K_F4: (1, 2, 1), K_F5: (2, 0, 1), K_F6: (2, 2, 1),
        }
        self.move_lookup = {
            K_6: "F", K_F6: "F'", K_5: "B", K_F5: "B'",
            K_1: "L", K_F1: "L'", K_2: "R", K_F2: "R'",
            K_4: "U", K_F4: "U'", K_3: "D", K_F3: "D'"
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
        rotate, rotate_key = False, None
        turn, turn_key = False, None

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == KEYDOWN:
                    # arrow keys for moving cube left/right/up/down
                    if event.key in self.rot_cube_map:
                        rotate = True
                        rotate_key = event.key

                    if event.key == K_SPACE:
                        self.scramble()
                    if event.key == K_r:
                        self.reset_cube()
                    if event.key == K_s:
                        self.solve()

                    # key 1-9 to rotate cube
                    if not self.animate and event.key in self.rot_slice_map:
                        self.add_move(event.key)
                        self.animate, self.action = True, self.rot_slice_map[event.key]
                        turn, turn_key = True, event.key

                if event.type == KEYUP:
                    if event.key in self.rot_cube_map:
                        rotate = rotate_key = None
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

            if rotate:
                self.rotate(rotate_key, repeat=1)
            if turn:
                self.turn_from_str(self.move_lookup[turn_key])
                turn = turn_key = False

            # for side in self.sides:
            #     print(f'{side}: {self.colors[side]} ', end="")
            # print()

            pygame.time.wait(10)

    def solve(self):
        self.solver.solve_cube()
        moves = self.solver.moves
        for move in moves:
            # move cube based on solution
            pass

    def scramble(self, num_rotations=20):
        possible_moves = list(self.move_lookup.values())

        for i in range(num_rotations):
            move = random.choice(possible_moves)
            self.turn_from_str(move)

    def reset_cube(self):
        reverse_moves = self.get_reverse_moves()
        for reverse_move in reverse_moves:
            self.turn_from_str(reverse_move)
        self.moves = []

    def add_move(self, key_move):
        move = self.move_lookup[key_move] if key_move in self.move_lookup else key_move
        self.moves.append(move)

    def get_reverse_moves(self):
        reverse_moves = []
        for move in self.moves[::-1]:
            opposite_move = get_opposite_move(move)
            reverse_moves.append(opposite_move)
        return reverse_moves

    def turn_from_str(self, move, repeat=1):
        print(f'{move}, {repeat}')

        while repeat:
            if move == "F":
                self.turn_F()
            elif move == "F'":
                self.turn_F_prime()
            elif move == "B":
                self.turn_B()
            elif move == "B'":
                self.turn_B_prime()
            elif move == "L":
                self.turn_L()
            elif move == "L'":
                self.turn_L_prime()
            elif move == "R":
                self.turn_R()
            elif move == "R'":
                self.turn_R_prime()
            elif move == "U":
                self.turn_U()
            elif move == "U'":
                self.turn_U_prime()
            elif move == "D":
                self.turn_D()
            elif move == "D'":
                self.turn_D_prime()
            else:
                print('error, invalid side rotation')
                exit(0)
            repeat -= 1

            self.update_colors(move)

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

    def shortest_horizontal_turn(self, start_side, end_side, layer):
        # get number of turns we need

        left_side = self.relative_sides[start_side]['L']
        right_side = self.relative_sides[start_side]['R']
        back_side = self.relative_sides[start_side]['B']

        left_side_color = self.get_center_color(left_side)
        right_side_color = self.get_center_color(right_side)
        back_side_color = self.get_center_color(back_side)

        end_side_color = self.get_center_color(end_side)
        move_face = 'D' if layer == 'bottom' else 'U'

        if left_side_color == end_side_color:
            self.turn_relative_move(start_side, move_face)

        if right_side_color == end_side_color:
            self.turn_relative_move(start_side, f"{move_face}'")

        if back_side_color == end_side_color:
            self.turn_relative_move(start_side, move_face, repeat=2)

    def turn_relative_move(self, side, move, repeat=1):
        relative_move = self.get_relative_move(side, move)
        self.turn_from_str(relative_move, repeat=repeat)

    def turn_side(self):
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
                        cube.update(self.prev_state, *self.action)
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

    def turn_F(self):
        self.animate, self.action = True, self.rot_slice_map[K_6]
        self.add_move(K_6)
        self.turn_side()

    def turn_F_prime(self):
        self.animate, self.action = True, self.rot_slice_map[K_F6]
        self.add_move(K_F6)
        self.turn_side()

    def turn_B(self):
        self.animate, self.action = True, self.rot_slice_map[K_5]
        self.add_move(K_5)
        self.turn_side()

    def turn_B_prime(self):
        self.animate, self.action = True, self.rot_slice_map[K_F5]
        self.add_move(K_F5)
        self.turn_side()

    def turn_L(self):
        self.animate, self.action = True, self.rot_slice_map[K_1]
        self.add_move(K_1)
        self.turn_side()

    def turn_L_prime(self):
        self.animate, self.action = True, self.rot_slice_map[K_F1]
        self.add_move(K_F1)
        self.turn_side()

    def turn_R(self):
        self.animate, self.action = True, self.rot_slice_map[K_2]
        self.add_move(K_2)
        self.turn_side()

    def turn_R_prime(self):
        self.animate, self.action = True, self.rot_slice_map[K_F2]
        self.add_move(K_F2)
        self.turn_side()

    def turn_U(self):
        self.animate, self.action = True, self.rot_slice_map[K_4]
        self.add_move(K_4)
        self.turn_side()

    def turn_U_prime(self):
        self.animate, self.action = True, self.rot_slice_map[K_F4]
        self.add_move(K_F4)
        self.turn_side()

    def turn_D(self):
        self.animate, self.action = True, self.rot_slice_map[K_3]
        self.add_move(K_3)
        self.turn_side()

    def turn_D_prime(self):
        self.animate, self.action = True, self.rot_slice_map[K_F3]
        self.add_move(K_F3)
        self.turn_side()

    def update_colors(self, move):
        # can pass either a keypress (1-9) or a string move like F/R/U'/etc.
        if move in self.move_lookup:
            turn = self.move_lookup[move]
        else:
            turn = move

        side = turn[0]
        dir = CW if len(turn) == 1 else CCW  # F for example is CW, and F' is CCW

        self.update_face_colors(side, dir)
        self.update_axis_colors(side, dir)

    def update_face_colors(self, face, dir):
        # ignore center square when updating face's colors, cannot change
        unique_square_indices = self.circular_indices[:-1]
        dir = -dir if face in ['B', 'D', 'L'] else dir  # from F face's perspective, CW movement of B side is CCW and vice versa

        # breakpoint()

        colors_copy = copy.deepcopy(self.colors[face])
        for circular_i, square_i in enumerate(unique_square_indices):
            nxt_i = get_circular_face_offset(unique_square_indices, circular_i, dir)  # gets circular index of new color square (offset by +-2 from current i)
            nxt_square_i = unique_square_indices[nxt_i]  # gets square index of above nxt_i, since self.colors is indexed as a rectangle
            self.colors[face][square_i] = colors_copy[nxt_square_i]

    def update_axis_colors(self, axis, dir):
        colors_copy = copy.deepcopy(self.colors)
        for index, square in enumerate(self.axis_squares[axis]):
            cur_face, cur_circular_i = re.findall(r'[A-Za-z]+|\d+', square)
            cur_square_i = self.circular_to_square_index(int(cur_circular_i))

            # get square color that's moving into this square's place
            nxt_index = (index + (3*dir)) % 12
            nxt_square = self.axis_squares[axis][nxt_index]
            nxt_face, nxt_circular_i = re.findall(r'[A-Za-z]+|\d+', nxt_square)
            nxt_square_i = self.circular_to_square_index(int(nxt_circular_i))
            nxt_color = colors_copy[nxt_face][nxt_square_i]

            self.colors[cur_face][cur_square_i] = nxt_color

    def get_rubix_faces(self):
        faces = {}

        for side in self.static_colors:
            faces[side] = copy.deepcopy(self.static_colors[side])
        return faces

    def get_axis_squares(self):
        # sets square indices of each possible move (front, back, left, right, up, down axis rotation)
        F_axis = ['U6', 'U5', 'U4', 'R8', 'R7', 'R6', 'D2', 'D1', 'D0', 'L4', 'L3', 'L2']  # F top-left is 0, goes right
        B_axis = ['U0', 'U1', 'U2', 'R2', 'R3', 'R4', 'D4', 'D5', 'D6', 'L6', 'L7', 'L8']  # U top-right is 0, goes left
        L_axis = ['F6', 'F7', 'F8', 'U6', 'U7', 'U8', 'B2', 'B3', 'B4', 'D6', 'D7', 'D8']  # F bottom-left is 0, goes up
        R_axis = ['F4', 'F3', 'F2', 'U4', 'U3', 'U2', 'B8', 'B7', 'B6', 'D4', 'D3', 'D2']  # F bottom-right is 0, goes up
        U_axis = ['F2', 'F1', 'F0', 'L2', 'L1', 'L0', 'B2', 'B1', 'B0', 'R2', 'R1', 'R0']  # F top-right is 0, goes left
        D_axis = ['F4', 'F5', 'F6', 'L4', 'L5', 'L6', 'B4', 'B5', 'B6', 'R4', 'R5', 'R6']  # F bottom-right is 0, goes left
        MV_axis = ['F5', 'FC', 'F1', 'U5', 'UC', 'U1', 'B1', 'BC', 'B5', 'D5', 'DC', 'D1']  # middle vertical axis
        MH_axis = ['L5', 'LC', 'L1', 'U7', 'UC', 'U3', 'R1', 'RC', 'R5', 'D3', 'DC', 'D7']  # middle horizontal axis
        axis_squares = {'F': F_axis, 'B': B_axis, 'L': L_axis, 'R': R_axis, 'U': U_axis, 'D': D_axis, 'MV': MV_axis, 'MH': MH_axis}

        return axis_squares

    # returns colors from side of rubix cube according to center color square
    def get_face(self, color):
        side = self.get_side_by_color(color)
        return self.colors[side]

    def get_face_by_side(self, side):
        return self.colors[side]

    def get_square_color(self, side, index):
        return self.colors[side][index]

    def get_side_by_color(self, color):
        color_index = self.sides_by_color.index(color)
        return self.sides[color_index]

    def circular_to_square_index(self, circular_i):
        circular_i = int(circular_i)
        return self.circular_indices[circular_i]

    def square_to_circular_index(self, square_i):
        square_i = int(square_i)
        return self.circular_indices.index(square_i)

    # converts a square index like 'F5' into a circular index like 'F3'
    def to_circular(self, index):
        square_list = split(index)
        square_list[-1] = str(self.square_to_circular_index(index[-1]))
        return ''.join(square_list)

    # converts a circular index like 'F3' into a square index like 'F5'
    def to_square(self, index):
        square_list = split(index)
        square_list[-1] = str(self.circular_to_square_index(index[-1]))
        return ''.join(square_list)

    def get_relative_move(self, side, move):
        relative_move = self.relative_moves[side][move[0]]
        if "'" in move:
            relative_move = get_reverse_move(relative_move)

        return relative_move

    def get_relative_side(self, color, rel_side):
        color = self.color_word_to_abbrev(color)
        color_side = self.get_side_by_color(color)
        return self.relative_sides[color_side][rel_side]

    def get_relative_face(self, color, side):
        relative_side = self.get_relative_side(color, side)
        relative_face = self.colors[relative_side]

    def color_word_to_abbrev(self, color):
        if len(color) == 1:
            return color

        index = self.color_words.index(color)
        return self.sides_by_color[index]

    def get_center_color(self, side):
        return self.colors[side][4]

    # square should be in circular index format
    def get_adjacent_edge_square(self, square, get_index=False, is_circular=True, is_square=False):
        if is_square:
            square = self.to_circular(square)

        edge_square1 = get_square_on_adjacent_face(self.axis_squares['MV'], square)
        edge_square2 = get_square_on_adjacent_face(self.axis_squares['MH'], square)

        edge_square = edge_square1 if edge_square1 else edge_square2

        # ci = circular index, si = square index
        adjacent_square_side, adjacent_square_ci = edge_square
        adjacent_square_si = self.circular_to_square_index(adjacent_square_ci)
        adjacent_square_color = self.get_square_color(adjacent_square_side, adjacent_square_si)
        adjacent_square_index = f'{adjacent_square_side}{adjacent_square_si}'
        return adjacent_square_index if get_index else adjacent_square_color

    # square should be in circular index format
    def get_adjacent_corner_squares(self, square, get_index=False, is_square_index=False):
        if is_square_index:
            square = self.to_circular(square)

        corner_square1 = get_square_on_adjacent_face(self.axis_squares['MV'], square)
        corner_square2 = get_square_on_adjacent_face(self.axis_squares['MH'], square)

        # ci = circular index, si = square index
        adjacent_square_side1, adjacent_square_ci1 = corner_square1
        adjacent_square_si1 = self.circular_to_square_index(adjacent_square_ci1)
        adjacent_square_color1 = self.get_square_color(adjacent_square_side1, adjacent_square_si1)
        adjacent_square_index1 = f'{adjacent_square_side1}{adjacent_square_si1}'

        adjacent_square_side2, adjacent_square_ci2 = corner_square2
        adjacent_square_si2 = self.circular_to_square_index(adjacent_square_ci2)
        adjacent_square_color2 = self.get_square_color(adjacent_square_side2, adjacent_square_si2)
        adjacent_square_index2 = f'{adjacent_square_side2}{adjacent_square_si2}'

        return (adjacent_square_index1, adjacent_square_index2) if get_index else (adjacent_square_color1, adjacent_square_color2)

    # returns squares in square index format
    def get_side_corners(self, side):
        indices = [0, 2, 6, 8]

        square_list = []
        for index in indices:
            square_index = f'{side}{index}'
            color = self.get_square_color(side, index)
            square_list.append((square_index, color))
        return square_list

    # returns squares in square index format
    def get_side_edges(self, side):
        indices = [1, 3, 5, 7]

        square_list = []
        for index in indices:
            square_index = f'{side}{index}'
            color = self.get_square_color(side, index)
            square_list.append((square_index, color))
        return square_list


# square should be in circular index format
def get_square_on_adjacent_face(axis, square):
    side, _ = square

    if square in axis:
        index = axis.index(square)
        prev_index = (index - 1) % 12
        nxt_index = (index + 1) % 12
        prev_side = axis[prev_index][0]
        nxt_side = axis[nxt_index][0]

        # case where we're on the wrong axis, left/right or up/down is on the same side
        if prev_side == side and nxt_side == side:
            return None

        # since square is at the bottom/top, we know prev/next item in list is the
        # bottom square, must be on a different side
        if prev_side != side:
            return axis[prev_index]
        else:
            assert(nxt_side != side)
            return axis[nxt_index]


def get_reverse_move(move):
    if len(move) == 1:
        return move + "'"
    else:
        return move[0]


def get_circular_face_offset(indices, index, dir):
    nxt_i = (index + (2 * dir)) % 8  # gets circular index of new color square (offset by +-2 from current i)
    return nxt_i


def get_circular_axis_offset(indices, index, dir):
    nxt_i = (indices.index(index) + (3 * dir)) % 12  # gets circular index of new color square (offset by +-2 from current i)
    return nxt_i


def read_rubix_cube_colors():
    mixed_cube = 'RubixCube_mixed2.json'
    solved_cube = 'RubixCube_solved.json'
    with open(mixed_cube, 'r') as file:
        data = json.load(file)
    return data


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
        square_i = x + (2 - z) * 3
    elif side == 'back':
        square_i = (2 - y) * 3 + (2 - x)
    else:
        print('error, invalid side')
        exit(0)

    return square_i


def split(word):
    return [char for char in word]
