################################################################################
#                                                                              #
# The main program of Tetris 2048 Base Code                                    #
#                                                                              #
################################################################################

import lib.stddraw as stddraw  # for creating an animation with user interactions
from lib.picture import Picture  # used for displaying an image on the game menu
from lib.color import Color  # used for coloring the game menu
import os  # the os module is used for file and directory operations
from game_grid import GameGrid  # the class for modeling the game grid
from tetromino import Tetromino  # the class for modeling the tetrominoes
import random  # used for creating tetrominoes with random types (shapes)
import pygame
import time

# The main function where this program starts execution
def start():
   pygame.mixer.init()

   current_dir = os.path.dirname(os.path.realpath(__file__))
   lock_tetromino = pygame.mixer.Sound(current_dir + "/sounds/block_place.wav")
   clear_line = pygame.mixer.Sound(current_dir + "/sounds/clear.wav")
   loss = pygame.mixer.Sound(current_dir + "/sounds/lose.wav")
   win = pygame.mixer.Sound(current_dir + "/sounds/win.wav")
   merge = pygame.mixer.Sound(current_dir + "/sounds/merge.wav")
   
   # Score
   score = 0
   #Button states
   paused = False
   muted = False

   # set the dimensions of the game grid
   grid_h, grid_w = 20, 12
   # set the size of the drawing canvas (the displayed window)
   canvas_h, canvas_w = 45 * grid_h, 45 * grid_w + 180
   stddraw.setCanvasSize(canvas_w, canvas_h)
   # set the scale of the coordinate system for the drawing canvas
   stddraw.setXscale(-0.5, grid_w + 4 - 0.5)
   stddraw.setYscale(-0.5, grid_h - 0.5)

   # set the game grid dimension values stored and used in the Tetromino class
   Tetromino.grid_height = grid_h
   Tetromino.grid_width = grid_w
   # create the game grid
   grid = GameGrid(grid_h, grid_w)
   # create the first tetromino to enter the game grid (and the second one so we can display it)
   # by using the create_tetromino function defined below
   tetromino_list = [create_tetromino(), create_tetromino()]
   grid.current_tetromino = tetromino_list[0]
   # display a simple menu before opening the game
   # by using the display_game_menu function defined below
   display_game_menu(grid_h, grid_w + 4)
   full_rows = []

   # Resets the whole game when called
   def reset(reset_buttons=True):
      nonlocal score, grid, tetromino_list, full_rows, muted, paused
      score = 0
      grid = GameGrid(grid_h, grid_w)
      tetromino_list = [create_tetromino(), create_tetromino()]
      grid.current_tetromino = tetromino_list[0]
      full_rows = []
      if reset_buttons:
         paused = False
         muted = False
         pygame.mixer.music.set_volume(1)

   # the main game loop
   while True:
      if len(full_rows) != 0:
         score += grid.sum_scores_in_row(full_rows)
         grid.remove_full_rows(full_rows)
         if score >= 2048:
            win.play()
            grid.display_win(score)
            reset()
            display_game_menu(grid_h, grid_w + 4)
         if not muted:
            clear_line.play
         full_rows = []
         time.sleep(1)
         if tetromino_list[1] is not None:
            grid.display(score, paused, muted, next_=Tetromino.get_min_bounded_tile_matrix(tetromino_list[1]))
         else:
            grid.display(score, paused, muted)
      if stddraw.mousePressed():
         x = stddraw.mouseX()
         y = stddraw.mouseY()
         if (x < 14 and x > 13) and (y > 15.75 and y < 16.75):
            reset()
            display_game_menu(grid_h, grid_w + 4)
            continue
         elif (x < 13 and x > 12) and (y > 17 and y < 18):
            paused = not paused
            if paused:
               pygame.mixer.music.stop()
            else:
               pygame.mixer.music.play()
            continue
         elif (x < 15 and x > 14) and (y > 17 and y < 18):
            muted = not muted
            if muted:
               pygame.mixer.music.set_volume(0)
            else:
               pygame.mixer.music.set_volume(1)

      is_hard_dropped = False
      # check for any user interaction via the keyboard
      if stddraw.hasNextKeyTyped():  # check if the user has pressed a key
         key_typed = stddraw.nextKeyTyped()  # the most recently pressed key
         # if the left arrow key has been pressed
         if key_typed == "left" and not paused:
            # move the active tetromino left by one
            tetromino_list[0].move(key_typed, grid)
         # if the right arrow key has been pressed
         elif key_typed == "right" and not paused:
            # move the active tetromino right by one
            tetromino_list[0].move(key_typed, grid)
         # if the down arrow key has been pressed
         elif key_typed == "down" and not paused:
            # move the active tetromino down by one
            # (soft drop: causes the tetromino to fall down faster)
            tetromino_list[0].move(key_typed, grid)
         elif key_typed == 'up' and not paused:
            rotated = tetromino_list[0].rotate(grid)
         if key_typed == "h" and not paused:
            is_hard_dropped = True
            moved_down = True
            while moved_down:
               moved_down = tetromino_list[0].move("down", grid)
         if key_typed == "r":
            reset(False)
            continue
         # clear the queue of the pressed keys for a smoother interaction
         stddraw.clearKeysTyped()

      # move the active tetromino down by one at each iteration (auto fall)
      if not paused and not is_hard_dropped:
         success = tetromino_list[0].move("down", grid)
      else:
         success = True
      
      # lock the active tetromino onto the grid when it cannot go down anymore
      if not success or is_hard_dropped:
         if not muted:
            lock_tetromino.play()
         # get the tile matrix of the tetromino without empty rows and columns
         # and the position of the bottom left cell in this matrix
         tiles, pos = tetromino_list[0].get_min_bounded_tile_matrix(True)
         # update the game grid by locking the tiles of the landed tetromino
         game_over = grid.update_grid(tiles, pos)

         # get a list of tuples which contain coordinates of tiles that need to be merged
         # each two tuples are to be merged, first being the one below, the second above
         merges = grid.check_merge()
         grid.drop_the_clumps()
         if merges:
            while merges:
               for i in range(len(merges)//2):
                  score += grid.merge_tiles(merges[i*2][0], merges[i*2][1])
               grid.drop_the_clumps()
               merges = grid.check_merge()
            if not muted:
               merge.play()
            if score >= 2048:
               grid.display(score, paused, muted)
               win.play()
               grid.display_win(score)
               reset()
               display_game_menu(grid_h, grid_w + 4)

         full_rows = grid.find_full_rows()

         # end the main game loop if the game is over
         if game_over:
            break
         # create the next tetromino to enter the game grid
         # by using the create_tetromino function defined below
         tetromino_list = [tetromino_list[1], create_tetromino()]
         grid.current_tetromino = tetromino_list[0]

      # display the game grid with the current tetromino
      if tetromino_list[1] is not None:
         grid.display(score, paused, muted, next_=Tetromino.get_min_bounded_tile_matrix(tetromino_list[1]))
      else:
         grid.display(score, paused, muted)
      
   # print a message on the console when the game is over
   print("Game over")
   
# A function for creating random shaped tetrominoes to enter the game grid
def create_tetromino():
   # the type (shape) of the tetromino is determined randomly
   tetromino_types = ['I', 'O', 'Z', 'J', 'L', 'S', 'T']
   random_index = random.randint(0, len(tetromino_types) - 1)
   random_type = tetromino_types[random_index]
   # create and return the tetromino
   tetromino = Tetromino(random_type)
   return tetromino

# A function for displaying a simple menu before starting the game
def display_game_menu(grid_height, grid_width):
   # get the directory in which this python code file is placed
   current_dir = os.path.dirname(os.path.realpath(__file__))
   
   # Menu music
   pygame.mixer.music.load(current_dir + "/sounds/tetris.ogg")
   pygame.mixer.music.play(loops=-1)
   
   # the colors used for the menu
   background_color = Color(237, 224, 200)
   button_color = Color(119, 110, 101)
   text_color = Color(237, 224, 200)
   # clear the background drawing canvas to background_color
   stddraw.clear(background_color)
   # compute the path of the image file
   img_file = current_dir + "/images/menu_image.png"
   # the coordinates to display the image centered horizontally
   img_center_x, img_center_y = (grid_width - 1) / 2, grid_height - 7
   # the image is modeled by using the Picture class
   image_to_display = Picture(img_file)
   # add the image to the drawing canvas
   stddraw.picture(image_to_display, img_center_x, img_center_y)
   # the dimensions for the start game button
   button_w, button_h = grid_width - 12, 1
   # the coordinates of the bottom left corner for the start game button
   button_blc_x, button_blc_y = img_center_x - button_w / 2, 4.5
   # add the start game button as a filled rectangle
   stddraw.setPenColor(button_color)
   stddraw.filledRectangle(button_blc_x, button_blc_y, button_w, button_h)
   # add the text on the start game button
   stddraw.setFontFamily("Sans Serif")
   stddraw.setFontSize(40)
   stddraw.setPenColor(text_color)
   text_to_display = "Start"
   stddraw.text(img_center_x, 5, text_to_display)
   # the user interaction loop for the simple menu
   while True:
      # display the menu and wait for a short time (50 ms)
      stddraw.show(50)
      # check if the mouse has been left-clicked on the start game button
      if stddraw.mousePressed():
         # get the coordinates of the most recent location at which the mouse
         # has been left-clicked
         mouse_x, mouse_y = stddraw.mouseX(), stddraw.mouseY()
         # check if these coordinates are inside the button
         if mouse_x >= button_blc_x and mouse_x <= button_blc_x + button_w:
            if mouse_y >= button_blc_y and mouse_y <= button_blc_y + button_h:
               pygame.mixer.music.stop()
               pygame.mixer.music.load(current_dir + "/sounds/chronologica.ogg")
               pygame.mixer.music.play(loops=-1)
               break  # break the loop to end the method and start the game


# start() function is specified as the entry point (main function) from which
# the program starts execution
if __name__ == '__main__':
   start()
