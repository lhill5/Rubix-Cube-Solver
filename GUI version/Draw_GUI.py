from color_choices import *
from Rubix_Cube import RubixCube
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel
from PyQt5.QtCore import Qt


class GUIApp(QWidget):

    def __init__(self):
        super().__init__()

        self.x = 0
        self.y = 130
        self.square_size = 130
        self.selected_color = colors['red']
        self.rubix_cube = RubixCube()

        self.setWindowTitle('QCheckBox')
        self.setGeometry(150, 0, 390, 630)
        self.label = QLabel(self)

        self.initUI()
        self.show()

    def initUI(self):
        self.draw_title()
        self.draw_color_menu()
        self.draw_RubixCube_side('F')  # draw front of rubix cube (white side)
        self.draw_rotate_buttons()

    def draw_title(self):
        self.label.setText("Pick a Color")
        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(16)
        self.label.setFont(font)

        # move, resize to entire width, and center-align
        self.label.move(0, 20)
        self.label.resize(390, 20)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setMinimumHeight(10)

    def draw_color_menu(self):
        color_keys = colors.keys()
        color_vals = colors.values()

        x = 14
        for color_str, color in zip(color_keys, color_vals):
            self.draw_color_option(color_str, color, x, 50)
            x += self.square_size * 4 / 10 + 10

    def draw_RubixCube_side(self, side: str):
        rubix_side = self.rubix_cube.get_side(side)

        for r in range(3):
            for c in range(3):
                color = rubix_side.get_square_color(r, c)
                btn = self.draw_square(side, r, c, color)
                rubix_side.set_square(r, c, color, btn)

                self.x += self.square_size
            self.x = 0
            self.y += self.square_size

    def draw_rotate_buttons(self):
        self.draw_rotate_button("Left", 296, 560)
        self.draw_rotate_button("Right", 354, 560)
        self.draw_rotate_button("Up", 325, 530)
        self.draw_rotate_button("Down", 325, 590)

    def draw_square(self, side: str, r: int, c: int, color: str) -> QPushButton:
        btn = QPushButton(f'{side}, {r}, {c}', self)
        btn.setStyleSheet(f"background-color: {color}; color:{color}; border:1px solid; border-color:white;")
        btn.setGeometry(self.x, self.y, self.square_size, self.square_size)
        btn.setMinimumHeight(10)

        btn.clicked.connect(self.change_color)
        return btn

    def draw_color_option(self, btn_id: int, color: str, x: int, y: int):
        btn = QPushButton(btn_id, self)
        btn.setStyleSheet(f"background-color: {color}; color:{color};")
        btn.setGeometry(int(x), int(y), int(self.square_size * 4 / 10), int(self.square_size * 4 / 10))
        btn.setMinimumHeight(10)

        btn.clicked.connect(self.pick_color)

    def draw_rotate_button(self, btn_id: str, x: int, y: int):
        btn = QPushButton(f'{btn_id[0]}', self)
        btn.setGeometry(x, y, 25, 25)
        btn.setMinimumHeight(10)
        btn.setFont(QFont('Times', 1))
        btn.setIcon(QIcon(f'images/{btn_id.lower()}_arrow.png'))
        btn.setStyleSheet(f"background-color: white; color: black;")

        btn.clicked.connect(self.rotate_cube)

    def change_color(self):
        # print("button pressed")
        rbt = self.sender().text()

        side, r, c = rbt.split(',')
        r, c = int(r), int(c)

        rubix_side = self.rubix_cube.get_side(side)
        btn = rubix_side.get_square_button(r, c)
        if btn is not None:
            btn.setStyleSheet(f"background-color: {self.selected_color}; color:{self.selected_color}; border:1px solid; border-color:white;")

    def update_side(self):
        rubix_side = self.rubix_cube.get_side('F')
        for r in range(3):
            for c in range(3):
                btn = rubix_side.get_square_button(r, c)

                if btn is not None:
                    btn.setStyleSheet(f"background-color: {rubix_side.color}; color:{rubix_side.color}; border:1px solid; border-color:white;")

    def pick_color(self):
        rbt = self.sender().text()
        self.selected_color = colors[rbt]

    def rotate_cube(self):
        bt = self.sender().text()
        if bt == 'L':
            self.rubix_cube.rotate_left()
        elif bt == 'R':
            self.rubix_cube.rotate_right()
        elif bt == 'U':
            self.rubix_cube.rotate_up()
        else:
            self.rubix_cube.rotate_down()
        self.update_side()

        # self.draw_RubixCube_side('F')  # draw front of rubix cube (white side)

