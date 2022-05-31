
class Square:
    # used for indexing cube in a circular way, similar to how rotating the cube works
    # indices are circular, values are square
    circular_indices = [0, 1, 2, 5, 8, 7, 6, 3, 0]

    # expects index to be in circular index format
    def __init__(self, square_id, color):
        self.side, index = square_id  # ex: "F", "3"
        self.index = int(index)
        self.color = color  # ex: "R" (red)

        self.circular_id = square_id  # ex: "F3"
        self.square_id = self.get_square_id()  # ex: "F5"

    # converts a square index like 'F5' into a circular index like 'F3'
    def get_circular_id(self, index):
        circular_i = self.circular_indices.index(self.index)
        return f'{self.side}{circular_i}'

    # converts a circular index like 'F3' into a square index like 'F5'
    def get_square_id(self):
        square_i = self.circular_indices[self.index]
        return f'{self.side}{square_i}'


def split(word):
    return [char for char in word]
