import lib.stddraw as stddraw  # used for displaying the game grid
from lib.color import Color, COLOR_DICT, WHITE  # used for coloring the game grid
from point import Point  # used for tile positions
import numpy as np  # fundamental Python module for scientific computing
import copy
import os
from lib.picture import Picture

# A class for modeling the game grid
class GameGrid:
    # A constructor for creating the game grid based on the given arguments
    def __init__(self, grid_h, grid_w):
        # set the dimensions of the game grid as the given arguments
        self.grid_height = grid_h
        self.grid_width = grid_w

        # Contains all tile locations that touches to the ground
        self.bottom_boundries = set()
        for i in range(self.grid_width):
            self.bottom_boundries.add((0, i))

        # create a tile matrix to store the tiles locked on the game grid
        self.tile_matrix = np.full((grid_h, grid_w), None)
        # create the tetromino that is currently being moved on the game grid
        self.current_tetromino = None
        # the game_over flag shows whether the game is over or not
        self.game_over = False
        # set the color used for the empty grid cells
        self.empty_cell_color = Color(203, 191, 177)
        # set the colors used for the grid lines and the grid boundaries
        self.line_color = Color(187, 173, 159)
        self.boundary_color = Color(71, 64, 71)
        # thickness values used for the grid lines and the grid boundaries
        self.line_thickness = 0.003
        self.box_thickness = self.line_thickness

    # A method for displaying the game grid
    def display(self, score, paused, muted, delay=250, next_=None):
        # clear the background to empty_cell_color
        stddraw.clear(self.empty_cell_color)
        # draw the game grid
        self.draw_grid()
        # draw the current/active tetromino if it is not None
        # (the case when the game grid is updated)
        if self.current_tetromino is not None:
            self.current_tetromino.draw()
        # draw a box around the game grid
        self.draw_boundaries()

        # Displays the info menu
        self.display_info(score)
        # Displays the buttons
        self.display_buttons(paused, muted)

        if next_ is not None:
            self.display_next_tetromino(next_)

        # show the resulting drawing with a pause duration = 250 ms
        stddraw.show(delay)

    # Displays the next tetromino and the text for it (no way)
    def display_next_tetromino(self, next_):
        row = 7
        col = 12 + (4 - len(next_[0])) / 2
        starting_col = col
        for i in next_:
            col = starting_col
            for j in i:
                if j is not None:
                    j.draw(Point(col, row), length=1)
                col = col + 1
            row = row - 1
        
        stddraw.setPenColor(Color(88, 90, 107))
        stddraw.filledRectangle(11.5, 8, 4, 1)
        
        stddraw.setFontFamily("Sans Serif")
        stddraw.setFontSize(30)
        stddraw.setPenColor(Color(208, 210, 227))
        stddraw.text(13.5, 8.5, "Next Tetromino")
        
    # Gets displayed while playing
    def display_info(self, score):
        # Adds the info box
        info_menu_color = Color(71, 64, 71)
        stddraw.setPenColor(info_menu_color)
        stddraw.filledRectangle(11.5, -0.5, 4, 20)

        # Box around the text 
        score_box_color = Color(88, 90, 107)
        stddraw.setPenColor(score_box_color)
        stddraw.filledRectangle(11.5, 13.5, 4, 2)

        # Logo of the game
        current_dir = os.path.dirname(os.path.realpath(__file__))
        img_file = current_dir + "/images/minilogo.png"
        stddraw.picture(Picture(img_file), 13.5, 18.8)

        # Logo of MEF
        img_file = current_dir + "/images/meflogo.png"
        stddraw.picture(Picture(img_file), 13.5, 1)

        # Adds the score text
        stddraw.setFontFamily("Helvetica")
        stddraw.setFontSize(35)
        stddraw.setPenColor(Color(208, 210, 227))
        text_to_display = "SCORE"
        stddraw.text(13.5, 15, text_to_display)
        text_to_display = str(score)
        stddraw.text(13.5, 14, text_to_display)
        stddraw.setFontSize(14)
        stddraw.text(13.5, 13.2, "Press \"r\" to reset the game!")
        stddraw.text(13.5, 12.7, "Press \"h\" to hard drop!")

        # Resets the pencil
        stddraw.setPenRadius()

    # Displays buttons (duh...)
    def display_buttons(self, paused, muted):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        img_file = current_dir + "/images/mainmenu.png"
        stddraw.picture(Picture(img_file), 13.5, 16.25)
        if paused:
            img_file = current_dir + "/images/continue.png"
        else:
            img_file = current_dir + "/images/pause.png"
        stddraw.picture(Picture(img_file), 12.5, 17.5)
        if muted:
            img_file = current_dir + "/images/muted.png"
        else:
            img_file = current_dir + "/images/unmuted.png"
        stddraw.picture(Picture(img_file), 14.5, 17.5)

    # Displays a win
    def display_win(self, score):
        # Overlay a semi-transparent dark layer
        stddraw.setPenColor(Color(0, 0, 0))  # Semi-transparent black
        stddraw.filledRectangle(-0.5, -0.5, 12, self.grid_height + 10)

        # Display WIN text
        stddraw.setFontFamily("Impact")
        stddraw.setFontSize(100)
        stddraw.setPenColor(Color(255, 215, 0))  # Gold color
        stddraw.text(self.grid_width / 2, self.grid_height / 2 + 2, "WIN!")
        stddraw.setFontSize(40)
        stddraw.text(self.grid_width / 2, self.grid_height / 2 - 2, f"Final Score: {score}")
        stddraw.show(3000)

    # A method for drawing the cells and the lines of the game grid
    def draw_grid(self):
        # for each cell of the game grid
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                # if the current grid cell is occupied by a tile
                if self.tile_matrix[row][col] is not None:
                    # draw this tile
                    self.tile_matrix[row][col].draw(Point(col, row))
        # draw the inner lines of the game grid
        stddraw.setPenColor(self.line_color)
        stddraw.setPenRadius(self.line_thickness)
        # x and y ranges for the game grid
        start_x, end_x = -0.5, self.grid_width - 0.5
        start_y, end_y = -0.5, self.grid_height - 0.5
        for x in np.arange(start_x + 1, end_x, 1):  # vertical inner lines
            stddraw.line(x, start_y, x, end_y)
        for y in np.arange(start_y + 1, end_y, 1):  # horizontal inner lines
            stddraw.line(start_x, y, end_x, y)
        stddraw.setPenRadius()  # reset the pen radius to its default value

    # A method for drawing the boundaries around the game grid
    def draw_boundaries(self):
        # draw a bounding box around the game grid as a rectangle
        stddraw.setPenColor(self.boundary_color)  # using boundary_color
        # set the pen radius as box_thickness (half of this thickness is visible
        # for the bounding box as its lines lie on the boundaries of the canvas)
        stddraw.setPenRadius(self.box_thickness)
        # the coordinates of the bottom left corner of the game grid
        pos_x, pos_y = -0.5, -0.5
        stddraw.rectangle(pos_x, pos_y, self.grid_width, self.grid_height)
        stddraw.setPenRadius()  # reset the pen radius to its default value

    # A method used checking whether the grid cell with the given row and column
    # indexes is occupied by a tile or not (i.e., empty)
    def is_occupied(self, row, col):
        # considering the newly entered tetrominoes to the game grid that may
        # have tiles with position.y >= grid_height
        if not self.is_inside(row, col):
            return False  # the cell is not occupied as it is outside the grid
        # the cell is occupied by a tile if it is not None
        return self.tile_matrix[row][col] is not None

    # A method for checking whether the cell with the given row and col indexes
    # is inside the game grid or not
    def is_inside(self, row, col):
        if row < 0 or row >= self.grid_height:
            return False
        if col < 0 or col >= self.grid_width:
            return False
        return True

    # A method that locks the tiles of a landed tetromino on the grid checking
    # if the game is over due to having any tile above the topmost grid row.
    # (This method returns True when the game is over and False otherwise.)
    def update_grid(self, tiles_to_lock, blc_position):
        # necessary for the display method to stop displaying the tetromino
        self.current_tetromino = None
        # lock the tiles of the current tetromino (tiles_to_lock) on the grid
        n_rows, n_cols = len(tiles_to_lock), len(tiles_to_lock[0])
        for col in range(n_cols):
            for row in range(n_rows):
                # place each tile (occupied cell) onto the game grid
                if tiles_to_lock[row][col] is not None:
                    # compute the position of the tile on the game grid
                    pos = Point()
                    pos.x = blc_position.x + col
                    pos.y = blc_position.y + (n_rows - 1) - row
                    if self.is_inside(pos.y, pos.x):
                        self.tile_matrix[pos.y][pos.x] = tiles_to_lock[row][col]
                    # the game is over if any placed tile is above the game grid
                    else:
                        self.game_over = True
        # return the value of the game_over flag
        return self.game_over

    def check_merge(self):
        n_rows, n_cols = self.grid_height, self.grid_width
        merges = []

        for col in range(n_cols):
            prev = None
            for row in range(n_rows):
                curr = self.tile_matrix[row][col]
                if (prev is not None and curr is not None
                        and curr.number == prev):
                    merges.append((row - 1, col))
                    merges.append((row, col))
                    break
                if curr is not None:
                    prev = curr.number
                else:
                    prev = None

        return merges

    # Merges two tiles
    def merge_tiles(self, row, col):
        cell = self.tile_matrix[row][col]
        if cell is not None:
            cell.number = cell.number * 2
            cell.background_color = COLOR_DICT[cell.number][0]
            cell.foreground_color = COLOR_DICT[cell.number][1]
            self.tile_matrix[row + 1][col] = None
            self.fall_after_merge(row, col)
        return cell.number
    # Moves the column above the tiles after a merge
    def fall_after_merge(self, row, col):
        current_row = row + 2
        current_tile = copy.deepcopy(self.tile_matrix[current_row][col])
        while current_tile is not None:
            self.tile_matrix[current_row][col] = None
            self.tile_matrix[current_row - 1][col] = current_tile
            current_row = current_row + 1
            current_tile = copy.deepcopy(self.tile_matrix[current_row][col])

    # Returns a list of connected tile locations starting from a location
    def get_connected_tiles(self, starting_location, tile_set, check_set):
        row, col = starting_location
        if self.is_occupied(row, col) and starting_location not in check_set:
            tile_set.add(starting_location)
            check_set.add(starting_location)
            if (row + 1, col) not in check_set:
                self.get_connected_tiles((row + 1, col), tile_set, check_set)
            if (row - 1, col) not in check_set:
                self.get_connected_tiles((row - 1, col), tile_set, check_set)
            if (row, col + 1) not in check_set:
                self.get_connected_tiles((row, col + 1), tile_set, check_set)
            if (row, col - 1) not in check_set:
                self.get_connected_tiles((row, col - 1), tile_set, check_set)
    # Applies get_connected_tiles to (almost) all tiles and returns a complete list of floating clumps(set of not connected tiles)
    def get_list_of_clumps(self):
        checked_tiles = set()
        total_clumps = []
        for i in range(1, self.grid_height):
            for j in range(self.grid_width):
                temp_set = set()
                self.get_connected_tiles((i, j), temp_set, checked_tiles)
                if temp_set and not temp_set & self.bottom_boundries:
                    total_clumps.append(temp_set)
        return total_clumps
    # Moves all the floating clumps down until atleast one is connected
    def drop_the_clumps(self):
        temp_list = self.get_list_of_clumps()
        while temp_list:
            for i in temp_list:
                for j in i:
                    current_tile = copy.deepcopy(self.tile_matrix[j[0]][j[1]])
                    self.tile_matrix[j[0]][j[1]] = None
                    self.tile_matrix[j[0] - 1][j[1]] = current_tile
            temp_list = self.get_list_of_clumps()

    # Finds full rows, changes their color and returns row indexes
    def find_full_rows(self):
        n_rows, n_cols = self.grid_height, self.grid_width
        rows = []
        for i in range(n_rows):
            is_full = True
            for j in range(n_cols):
                if self.tile_matrix[i][j] is None:
                    is_full = False
                    break
            if is_full:
                rows.append(i)
                for j in range(0, n_cols):
                    tile = self.tile_matrix[i][j]
                    tile.background_color = Color(79, 255, 0)
                    tile.foreground_color = WHITE
        return rows

    # Moves tiles above the rows that should be deleted one step down
    def remove_full_rows(self, rows):
        n_rows, n_cols = self.grid_height, self.grid_width

        for i in rows:
            for k in range(i, n_rows - 1):
                for j in range(n_cols):
                    self.tile_matrix[k][j] = self.tile_matrix[k + 1][j]

    def sum_scores_in_row(self, rows):
        cols = self.grid_width
        sum = 0
        for i in rows:
            for j in range(cols):
                if self.tile_matrix[i][j] is not None:
                    sum += self.tile_matrix[i][j].number
        return sum
