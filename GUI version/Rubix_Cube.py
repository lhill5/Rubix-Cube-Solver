from color_choices import colors
from PyQt5.QtWidgets import QPushButton
from copy import deepcopy, copy


class RubixCube:
    def __init__(self):
        self.sides = {'F': self.Side('F', 'white'), 'L': self.Side('L', 'orange'), 'R': self.Side('R', 'red'), 'B': self.Side('B', 'yellow'), 'U': self.Side('U', 'blue'), 'D': self.Side('D', 'green')}
        self.moves = None

    class Side:
        def __init__(self, side, color_str):
            self.side = side
            # center color of this side
            self.color_str = color_str
            self.color = colors[color_str]
            # contains all colors
            self.squares = [[self.Square(self.color) for _ in range(3)] for _ in range(3)]

        class Square:
            def __init__(self, color):
                self.color = color
                self.btn = None

            def copy(self, copy_square):
                self.color = copy_square.color

        def get_square(self, r: int, c: int):
            return self.squares[r][c]

        def get_square_color(self, r: int, c: int):
            return self.get_square(r, c).color

        def get_square_button(self, r: int, c: int):
            return self.get_square(r, c).btn

        def set_square(self, r: int, c: int, color: str, btn: QPushButton):
            self.squares[r][c].color = color
            self.squares[r][c].btn = btn

        def assign(self, copy_side):
            self.color_str = copy_side.color_str
            self.color = copy_side.color

            for row, copy_row in zip(self.squares, copy_side.squares):
                for square, copy_square in zip(row, copy_row):
                    square.copy(copy_square)

    def copy_side(self, side):
        side_cpy = self.Side(side.side, side.color_str)
        for r in range(3):
            for c in range(3):
                side_cpy.squares[r][c].copy(side.squares[r][c])

        return side_cpy

    def get_side(self, side):
        return self.sides[side]

    def get_side_color(self, side):
        return self.get_side(side).color

    def solve(self):
        pass

    def rotate_left(self):
        tmp_front_side = self.copy_side(self.sides['F'])
        self.sides['F'].assign(self.sides['L'])
        self.sides['L'].assign(self.sides['B'])
        self.sides['B'].assign(self.sides['R'])
        self.sides['R'].assign(tmp_front_side)

    def rotate_right(self):
        tmp_front_side = self.copy_side(self.sides['F'])
        self.sides['F'].assign(self.sides['R'])
        self.sides['R'].assign(self.sides['B'])
        self.sides['B'].assign(self.sides['L'])
        self.sides['L'].assign(tmp_front_side)

    def rotate_up(self):
        tmp_front_side = self.copy_side(self.sides['F'])
        self.sides['F'].assign(self.sides['U'])
        self.sides['U'].assign(self.sides['B'])
        self.sides['B'].assign(self.sides['D'])
        self.sides['D'].assign(tmp_front_side)

    def rotate_down(self):
        tmp_front_side = self.copy_side(self.sides['F'])
        self.sides['F'].assign(self.sides['D'])
        self.sides['D'].assign(self.sides['B'])
        self.sides['B'].assign(self.sides['U'])
        self.sides['U'].assign(tmp_front_side)
