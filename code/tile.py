import lib.stddraw as stddraw  # used for drawing the tiles to display them
from lib.color import Color, COLOR_DICT   # used for coloring the tiles
from random import randint

# A class for modeling numbered tiles as in 2048
class Tile:
   # Class variables shared among all Tile objects
   # ---------------------------------------------------------------------------
   # font family and font size used for displaying the tile number
   font_family, font_size = "Sans Serif", 23

   # A constructor that creates a tile with 2 as the number on it
   def __init__(self):
      # set the number on this tile
      self.number = (randint(1, 2)*2)
      
      # set the colors of this tile
      if self.number == 2:
         self.background_color = COLOR_DICT[2][0]  # background (tile) color
         self.foreground_color = COLOR_DICT[2][1]  # foreground (number) color
      else:
         self.background_color = COLOR_DICT[4][0]  # background (tile) color
         self.foreground_color = COLOR_DICT[4][1]  # foreground (number) color

      self.box_color = Color(187, 173, 159)  # box (boundary) color

   # A method for drawing this tile at a given position with a given length
   def draw(self, position, length=1):  # length defaults to 1
      # draw the tile as a filled square
      stddraw.setPenColor(self.background_color)
      stddraw.filledSquare(position.x+0.04, position.y-0.03, length / 2)
      
      stddraw.setPenRadius()  # reset the pen radius to its default value
      # draw the number on the tile
      stddraw.setPenColor(self.foreground_color)
      stddraw.setFontFamily(Tile.font_family)
      stddraw.setFontSize(Tile.font_size)
      stddraw.text(position.x, position.y, str(self.number))
