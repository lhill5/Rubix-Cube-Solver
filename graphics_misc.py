vertices = (
    (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, -1),
    (1, -1, 1), (1, 1, 1), (-1, -1, 1), (-1, 1, 1)
)

edges = ((0, 1), (0, 3), (0, 4), (2, 1), (2, 3), (2, 7), (6, 3), (6, 4), (6, 7), (5, 1), (5, 4), (5, 7))
surfaces = ((0, 1, 2, 3), (3, 2, 7, 6), (6, 7, 5, 4), (4, 5, 1, 0), (1, 5, 7, 2), (4, 0, 3, 6))
#              blue(back)  orange(left)  green(front)  red(right)  white(up)  yellow(down)
rgb_colors = [(20, 13, 79), (255, 101, 68), (103, 218, 76), (190, 56, 47), (217, 220, 237), (237, 244, 76)]
colors = [[val / 255 for val in color] for color in rgb_colors]
colors_dict = {'B': colors[0], 'O': colors[1], 'G': colors[2], 'R': colors[3], 'W': colors[4], 'Y': colors[5]}
square_surfaces = ((6, 7, 5, 4),)


def shift(x, y):
    new_vertices = []
    for vert in vertices:
        new_vert = [vert[0] + x, vert[1] + y, vert[2]]
        new_vertices.append(new_vert)

    return new_vertices
