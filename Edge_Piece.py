from Square import Square


class Edges:
    # in circular index format
    edge_indices = [('F1', 'U5'), ('U1', 'B1'), ('B5', 'D5'), ('D1', 'F5'),
                    ('F7', 'L3'), ('L7', 'B3'), ('B7', 'R3'), ('R7', 'F3'),
                    ('U7', 'L1'), ('L5', 'D7'), ('D3', 'R5'), ('R1', 'U3')]

    def __init__(self, colors):
        self.colors = colors
        self.edges = []

        for edge_i in self.edge_indices:
            self.edges.append(self.Edge(self.colors, edge_i))

    # finds edge that square is on by its square id
    def get_edge(self, square_id):
        for edge in self.edges:
            if square_id in edge:
                return edge

    def get_adjacent_edge_color(self, square_id):
        edge = self.get_edge(square_id)
        return edge.get_adjacent_color(square_id)

    class Edge:
        def __init__(self, colors, edge):
            self.colors = colors
            self.edge = edge
            self.squares = []

            for square_id in edge:
                square_color = self.get_square_color(square_id)
                self.squares.append(Square(square_id, square_color))

        def get_square_color(self, square_index):
            side, index = square_index
            return self.colors[side][index]

        def get_edge_colors(self):
            colors = [square.color for square in self.squares]
            return colors

        def get_adjacent_color(self, square_id):
            adj_squares = [square.color for square in self.squares if square.circular_id != square_id]
            return adj_squares[0]  # should only be one adjacent square
