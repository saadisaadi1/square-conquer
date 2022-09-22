from framework import GameManager
from random import Random

class character:
    pass


class board:
    def __init__(self, board_size): # think about proper data structures before implementing maybe you should change some stuff that you have already written
        self.board_size = board_size
        self.entity = GameManager.create_new_entity() # fill the details
        # make the animations packs of the dots squares and lines
        self.dots = None
        self.squares = None # red and blue squares
        self.lines = None
        for i in range(board_size[1]):
            for j in range(board_size[2]): # make the dots here and lines here
                pass
    def choose_characters(self): #of course you have to use random here in a smart way
        pass

    def highlight_line(self):
        pass

    def unhighlight_line(self):
        pass

    def add_new_line(self):
        pass

    def add_new_square(self, row, column):
        pass

    def deal_with_affected_characters(self):
        pass

    def check_game_ended(self):
        pass
