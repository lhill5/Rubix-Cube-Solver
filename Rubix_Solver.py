class Solver:
    def __init__(self, rubix_cube):
        self.rubix_cube = rubix_cube
        self.rubix_cube_colors = self.rubix_cube.colors
        self.moves = []  # list of moves to solve the current rubix cube

    def solve_cube(self):
        self.solve_white_cross()
        self.solve_white_side()
        self.solve_second_layer()
        self.solve_yellow_cross()
        self.align_yellow_corners()
        self.solve_yellow_corners()
        self.solve_final_corners()

    def solve_white_cross(self):
        front_side = self.rubix_cube.get_relative_side('white', 'F')
        left_side = self.rubix_cube.get_relative_side('white', 'L')
        right_side = self.rubix_cube.get_relative_side('white', 'R')
        up_side = self.rubix_cube.get_relative_side('white', 'U')
        down_side = self.rubix_cube.get_relative_side('white', 'D')
        back_side = self.rubix_cube.get_relative_side('white', 'B')

        turn_cube = True
        turns = 100

        while turn_cube:
            turn_cube = False

            # look for white edge squares on bottom-layer
            for side in [left_side, right_side, up_side, down_side]:
                if turns == 0:
                    continue

                face = self.rubix_cube.get_face_by_side(side)

                if face[7] == 'W':
                    print(f'white edge on bottom layer')
                    turn_cube = True
                    turns -= 1
                    square = f'{side}5'  # circular index
                    cur_side = self.align_with_center_color(side, square)
                    self.turn_side(cur_side, repeat=2)
                    self.swap_top_edges(cur_side)

            # look for white edge squares in middle layer
            for side in [left_side, right_side, up_side, down_side]:
                if turns == 0:
                    continue

                face = self.rubix_cube.get_face_by_side(side)
                if face[3] == 'W':
                    print(f'white edge on middle layer, left side')
                    turn_cube = True
                    turns -= 1
                    self.swap_middle_left_layer_edge_piece(side)
                elif face[5] == 'W':
                    print(f'white edge on middle layer, right side')
                    turn_cube = True
                    turns -= 1
                    self.swap_middle_right_layer_edge_piece(side)

            # (verified) look for white edge squares in top layer
            # align with center color and swap_top_edges
            for side in [left_side, right_side, up_side, down_side]:
                if turns == 0:
                    continue

                face = self.rubix_cube.get_face_by_side(side)
                if face[1] == 'W':
                    print(f'white edge on top layer')
                    turn_cube = True
                    turns -= 1

                    self.turn_side(side, repeat=2)
                    square = f'{side}5'  # circular index
                    cur_side = self.align_with_center_color(side, square)
                    self.turn_side(cur_side, repeat=2)
                    self.swap_top_edges(cur_side)

            # (verified) look for white edge squares on D side below bottom edge square
            # just align with center color and flip, no swap_top_edges
            for side in [left_side, right_side, up_side, down_side]:
                if turns == 0:
                    continue

                s_adjacent_square = self.rubix_cube.get_adjacent_edge_square(f'{side}5', get_index=True)  # circular index
                s_adjacent_side, s_adjacent_index = s_adjacent_square
                adjacent_square_color = self.rubix_cube.get_square_color(s_adjacent_side, int(s_adjacent_index))
                if adjacent_square_color == 'W':
                    # breakpoint()
                    print(f'white edge on D side')
                    turn_cube = True
                    turns -= 1
                    # [below parameters explained]: currently on side (will be used to rotate in reference to this side), and white square is adjacent index
                    c_adjacent_square = self.rubix_cube.to_circular(s_adjacent_square)
                    cur_side = self.align_with_center_color(side, c_adjacent_square)
                    self.turn_side(cur_side, repeat=2)

            # look for white square along white-cross but not aligned
            # just FF then repeat above checks
            for side, cross_index in zip([left_side, right_side, up_side, down_side], [3, 5, 1, 7]):
                if turns == 0:
                    continue

                cur_face = self.rubix_cube.get_face_by_side(side)
                front_face = self.rubix_cube.get_face_by_side(front_side)
                # if white square is already in 'white cross' area and not aligned properly on current side
                if front_face[cross_index] == 'W' and cur_face[1] != cur_face[4]:
                    print(f'white edge on white cross')
                    turn_cube = True
                    turns -= 1

                    self.turn_side(side, repeat=2)
                    s_adjacent_square = self.rubix_cube.get_adjacent_edge_square(f'{side}5', get_index=True)  # circular index
                    # [below parameters explained]: currently on side (will be used to rotate in reference to this side), and white square is adjacent index
                    c_adjacent_square = self.rubix_cube.to_circular(s_adjacent_square)
                    cur_side = self.align_with_center_color(side, c_adjacent_square)
                    self.turn_side(cur_side, repeat=2)

            # print(f'moves: {self.rubix_cube.moves}')
            # print(f'reverse moves: {self.rubix_cube.get_reverse_moves()}')

    def solve_white_side(self):
        front_side = self.rubix_cube.get_relative_side('yellow', 'F')
        left_side = self.rubix_cube.get_relative_side('yellow', 'L')
        right_side = self.rubix_cube.get_relative_side('yellow', 'R')
        up_side = self.rubix_cube.get_relative_side('yellow', 'U')
        down_side = self.rubix_cube.get_relative_side('yellow', 'D')
        back_side = self.rubix_cube.get_relative_side('yellow', 'B')

        face = self.rubix_cube.get_face_by_side(front_side)
        corner_squares = self.rubix_cube.get_side_corners(front_side)

        # gets all corners on yellow side that have a white square
        white_corners = []
        for corner_square in corner_squares:
            s_corner_index, corner_color = corner_square
            adjacent_corner1_color, adjacent_corner2_color = self.rubix_cube.get_adjacent_corner_squares(s_corner_index, is_square_index=True)
            if corner_color == 'W' or adjacent_corner1_color == 'W' or adjacent_corner2_color == 'W':
                corner_colors = [corner_color, adjacent_corner1_color, adjacent_corner2_color]
                corner_colors.remove('W')
                assert(len(corner_colors) == 2)
                white_corners.append(corner_colors)

        # aligns corner with white square on correct side, moves square to white face until corner colors match
        for i, corner_pair in enumerate(white_corners):
            color1, color2 = corner_pair

            cur_side = self.align_white_corner(color1, color2)


        turn_cube = True
        while turn_cube:
            turn_cube = False
            
    def solve_second_layer(self):
        pass

    def solve_yellow_cross(self):
        pass

    def align_yellow_corners(self):
        pass

    def solve_yellow_corners(self):
        pass

    def solve_final_corners(self):
        pass

    def turn_side(self, side, repeat=1):
        self.rubix_cube.turn_from_str(side, repeat=repeat)

    # square should be in circular index format
    def align_with_center_color(self, cur_side, square):
        # get color of below square (one we need to match with it's side)

        match_color = self.rubix_cube.get_adjacent_edge_square(square)

        # get side of side we want to move to (matches color)
        dest_side = self.rubix_cube.get_side_by_color(match_color)
        # turn cube to align square's color with center color
        if cur_side != dest_side:
            layer = 'top' if square[-1] == 1 else 'bottom'
            self.rubix_cube.shortest_horizontal_turn(cur_side, dest_side, layer)

        return dest_side

    # functions to execute a sequence of moves to help solve the cube
    def swap_top_edges(self, side):
        moves = ["F", "U'", "R", "U"]
        for move in moves:
            # gets move we should make depending on which side we're currently on
            self.rubix_cube.turn_relative_move(side, move)

    def swap_middle_left_layer_edge_piece(self, side):
        moves = ["L'", "D", "L"]
        for move in moves:
            self.rubix_cube.turn_relative_move(side, move)

    def swap_middle_right_layer_edge_piece(self, side):
        moves = ["R'", "D", "R"]
        for move in moves:
            self.rubix_cube.turn_relative_move(side, move)

