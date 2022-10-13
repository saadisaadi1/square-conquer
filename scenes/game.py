from framework import GameManager, Scene
import random
import pygame

class Character:
    pass


class Board:
    def __init__(self, board_size): # think about proper data structures before implementing maybe you should change some stuff that you have already written
        self.board_size = {}
        self.board_size['x'], self.board_size['y'] = board_size
        self.entity = GameManager.create_new_entity("board", None)
        # make the animations packs of the dots squares and lines
        self.dots = {}
        self.squares = None # red and blue squares
        self.lines = {}
        for i in range(self.board_size['x'] + 1):
            for j in range(self.board_size['y'] + 1): # make the dots here and lines here
                self.dots[(i,j)] = GameManager.create_new_entity("dot" + str(i) + str(j), "Dot", "board")
                self.dots[(i,j)].set_center_position(self.entity.transform.position['x'] + i * 50, self.entity.transform.position['y'] + j * 50)

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

#--------------------------------------------------------------------------------------------
class GameScene(Scene):

    def __init__(self):
        self.name = "game scene"
        self.board = None
        super().__init__()

    def start(self):
        self.board = Board((10, 5))
        self.board.entity.set_position(200, 200)

    def update(self):
        print("coco")
