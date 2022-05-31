from Square import Square


class Corners:
    # in circular index format
    corner_indices = [('F0', 'L2', 'U6'), ('F2', 'R0', 'U4'), ('F4', 'R6', 'D2'), ('F6', 'L4', 'D0'),
                      ('B0', 'R2', 'U2'), ('B2', 'L0', 'U0'), ('B4', 'L6', 'D6'), ('B6', 'R4', 'D4')]

    def __init__(self, colors):
        self.colors = colors
        self.corners = []

        for corner_i in self.corner_indices:
            self.corners.append(self.Corner(self.colors, corner_i))

    # finds corner that square is on by its square id
    def get_corner(self, square_id):
        for corner in self.corners:
            if square_id in corner:
                return corner

    def get_adjacent_corner_colors(self, square_id):
        corner = self.get_corner(square_id)
        return corner.get_adjacent_colors(square_id)

    class Corner:
        def __init__(self, colors, corner):
            self.colors = colors
            self.corner = corner
            self.squares = []

            for square_id in corner:
                square_color = self.get_square_color(square_id)
                self.squares.append(Square(square_id, square_color))

        def get_square_color(self, square_index):
            side, index = square_index
            return self.colors[side][index]

        def get_corner_colors(self):
            colors = [square.color for square in self.squares]
            return colors

        def get_adjacent_colors(self, square_id):
            adjacent_colors = [square.color for square in self.squares if square.circular_id != square_id]
            return adjacent_colors