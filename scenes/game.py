from framework import GameManager, Scene
import random
import pygame


class Board:
    def __init__(self, board_size):
        self.statistics = {"score": [0, 0],
                           "square": [0, 0],
                           "frog": [0, 0],
                           "snowy": [0, 0],
                           "chick": [0, 0]
                           }
        self.turn = 1
        self.font_size = 120
        self.font = pygame.font.SysFont('arialblack', self.font_size)
        self.players_text = [GameManager.create_new_entity(name = "player1 score", text_pack = (self.font, "0", False, (0, 0, 0)), layer = 10)
                            ,GameManager.create_new_entity(name = "player2 score", text_pack = (self.font, "0", False, (0, 0, 0)), layer = 10)]
        self.palyer1_score = 0
        self.palyer2_score = 0
        self.board_size = {}
        self.board_size['x'], self.board_size['y'] = board_size
        self.max_scale = None
        self.min_scale = 1
        self.scroll_rate = 10
        self.entity = GameManager.create_new_entity("board", None)
        self.card = GameManager.create_new_entity(name = "dad", kind = "Card", layer = 1)
        self.dots = {}
        self.squares = {}
        self.lines = {}
        self.characters = {}
        self.highlighted_lines = []
        self.square_side_length = GameManager.animations_packs["Square"].animations["empty"].frame_size['x']
        self.width = None
        self.height = None
        for i in range(self.board_size['x'] + 1):
            for j in range(self.board_size['y'] + 1):
                self.dots[(i, j)] = GameManager.create_new_entity(name = "dot" + str(i) + str(j), kind = "Dot", father = "board", layer = 3)
                self.dots[(i,j)].set_scale(0.5, 0.5)
                self.dots[(i, j)].align(self.entity.transform.position['x'] + j * self.square_side_length, self.entity.transform.position['y'] + i * self.square_side_length, (50, 50))

        for i in range(self.board_size['x']):
            for j in range(self.board_size['y'] + 1):
                self.lines[("v", i, j)] = VerticalLine("vertical line" + str(i) + str(j))
                self.lines[("v", i, j)].entity.align_to_other_entity(other_entity=self.dots[(i, j)],other_alignment = (50, 70), alignment = (50, 0))

        for i in range(self.board_size['x'] + 1):
            for j in range(self.board_size['y']):
                self.lines[("h", i, j)] = HorizontalLine("horizontal line" + str(i) + str(j))
                self.lines[("h", i, j)].entity.align_to_other_entity(other_entity = self.dots[(i, j)],other_alignment = (70, 50), alignment = (0, 50))

        for i in range(self.board_size['x']):
            for j in range(self.board_size['y']):
                self.squares[(i, j)] = Square("square" + str(i) + str(j))
                self.squares[(i, j)].entity.align_to_other_entity(other_entity = self.dots[(i, j)], alignment = (0, 0))

        self.fill_with_characters()
        self.calculate_max_scale()


    def fill_with_characters(self): #of course you have to use random here in a smart way
        for i in range(self.board_size['x']):
            for j in range(self.board_size['y']):
                character = random.choice([Frog, Snowy, Chick])

                self.characters[(i, j)] = character((i, j), self) #random.choice([Snowy((i, j), self), Frog((i, j), self)])
                self.characters[(i, j)].entity.align_to_other_entity(other_entity = self.squares[(i, j)].entity, other_alignment = (50, 50), alignment = (50, 50))
        for key in self.characters:
            self.characters[key].add_character_to_effective_squares()

    def deal_with_affected_characters(self,i, j):
        square = self.squares[(i, j)]
        for key in square.characters:
            character = square.characters[key]
            if character.player != 0:
                character.update_status_and_score(i, j)

    def calculate_max_scale(self):
        self.width =  self.board_size['y'] * self.square_side_length + (self.dots[0,0].get_size())[0]
        self.height = self.board_size['x'] * self.square_side_length + (self.dots[0,0].get_size())[0]
        win_x, win_y = GameManager.win.get_size()
        self.max_scale = min(win_x * (2/3) / self.width, win_y * (2/3) / self.height)
        self.min_scale = min(self.min_scale, self.max_scale/2)
        initial_scale = (self.max_scale + self.min_scale)/2
        self.width *= initial_scale
        self.height *= initial_scale
        self.entity.set_scale(initial_scale, initial_scale)

    def scroll_and_scale(self):
        if "mouse wheel" in GameManager.notifications:
            scroll_power = GameManager.notifications["mouse wheel"]
            old_scale = self.entity.transform.scale['x']
            new_scale = old_scale + scroll_power * self.scroll_rate * GameManager.delta_time
            if new_scale < self.min_scale:
                new_scale = self.min_scale
            elif new_scale > self.max_scale:
                new_scale = self.max_scale
            self.width *= new_scale/old_scale
            self.height *= new_scale/old_scale
            self.entity.set_scale(new_scale, new_scale)

    def check_game_ended(self):
        if sum(self.statistics["square"]) == self.board_size['x'] * self.board_size['y']:
            return True
        else:
            return False

    def update(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        square_size = (self.squares[(0, 0)].entity.get_size())[0]
        i = (mouse_y - self.entity.transform.position['y'])//square_size
        j = (mouse_x - self.entity.transform.position['x'])//square_size

        for key in self.highlighted_lines:
           self.update_line(key)
        if self.check_valid_square_coordinates(i, j):
            self.card.animator.change_animation(self.characters[(i, j)].character)
            self.update_line(("v", i, j))
            self.update_line(("v", i, j + 1))
            self.update_line(("h", i, j))
            self.update_line(("h", i + 1, j))

        elif i == -1 and j >= 0 and j < self.board_size['y']:
            self.update_line(("h", i + 1, j))
        elif i == self.board_size['x'] and j >= 0 and j < self.board_size['y']:
            self.update_line(("h", i, j))
        elif i >= 0 and i < self.board_size['x'] and j == -1:
            self.update_line(("v", i, j + 1))
        elif i >= 0 and i < self.board_size['x'] and j == self.board_size['y']:
            self.update_line(("v", i, j))
        else:
            return None

    def update_line(self, key):
        color = self.lines[key].update()
        i = key[1]
        j = key[2]
        first_square = "empty"
        second_square = "empty"

        if color == "gray":
            if key not in self.highlighted_lines:
                self.highlighted_lines.append(key)
        elif color == "transparent" or color == "black":
            if key in self.highlighted_lines:
                self.highlighted_lines.remove(key)
        elif color == "new black":
            if key[0] == 'v':
                first_square = self.check_full_square(i, j)
                second_square = self.check_full_square(i, j - 1)
            elif key[0] == 'h':
                first_square = self.check_full_square(i, j)
                second_square = self.check_full_square(i - 1, j)

            if first_square == "empty" and second_square == "empty":
                if self.turn == 1:
                    self.turn = 2
                elif self.turn == 2:
                    self.turn = 1
            else:
                if first_square == "full":
                    if self.squares[(i, j)].player == 0:
                        self.characters[(i, j)].appear(self.turn)
                        self.squares[(i, j)].player = self.turn
                    self.deal_with_affected_characters(i, j)
                if second_square == "full" :
                    if key[0] == 'v':
                        if self.squares[(i, j - 1)].player == 0:
                            self.characters[(i, j - 1)].appear(self.turn)
                            self.squares[(i, j - 1)].player = self.turn
                        self.deal_with_affected_characters(i, j - 1)
                    elif key[0] == 'h':
                        if self.squares[(i - 1, j)].player == 0:
                            self.characters[(i - 1, j)].appear(self.turn)
                            self.squares[(i - 1, j)].player = self.turn
                        self.deal_with_affected_characters(i - 1, j)


    def check_full_square(self, i, j):
        if self.check_valid_square_coordinates(i, j):
            if self.lines[("v", i, j)].clicked and self.lines[("v", i, j + 1)].clicked and  self.lines[("h", i, j)].clicked and self.lines[("h", i + 1, j)].clicked:
                self.squares[(i, j)].entity.animator.change_animation("color " + str(self.turn))
                return "full"
        return "empty"

    def check_valid_square_coordinates(self, i, j):
        return i >= 0 and i < self.board_size['x'] and j >= 0 and j < self.board_size['y']


class Line():

    def __init__(self, name):
        self.type_string = None
        self.clicked = False
        self.entity = GameManager.create_new_entity(name = name, kind = "Line", father = "board", layer = 2)

    def update(self):
        color = "black"
        if not self.clicked:
            if self.entity.check_triggered():
                self.entity.animator.change_animation("gray" + self.type_string)
                color = "gray"
            else:
                self.entity.animator.change_animation("empty" + self.type_string)
                color = "transparent"

            if self.entity.check_clicked():
                self.clicked = True
                self.entity.animator.change_animation("black" + self.type_string)
                color = "new black"
        return color



class VerticalLine(Line):
    def __init__(self, name):
        super().__init__(name)
        self.type_string = " vl"
        self.entity.animator.change_animation("empty" + self.type_string)


class HorizontalLine(Line):
    def __init__(self, name):
        super().__init__(name)
        self.type_string = " hl"
        self.entity.animator.change_animation("empty" + self.type_string)


class Square():
    def __init__(self, name):
        self.entity = GameManager.create_new_entity(name, "Square", "board", 1)
        self.player = 0
        self.characters = {}


class Character():
    def __init__(self, coordinates, board):
        self.character = None
        self.entity = None
        self.board = board
        self.coordinates = coordinates
        self.score = 0
        self.player = 0

    def add_character_to_effective_squares(self):
        raise NotImplementedError

    def appear(self, player):
        self.player = player
        if self.player == 1:
            (self.board.statistics[self.character])[0] += 1
            (self.board.statistics["square"])[0] += 1
        elif self.player == 2:
            (self.board.statistics[self.character])[1] += 1
            (self.board.statistics["square"])[1] += 1
            #print(self.board.statistics["score"])

    def update_status_and_score(self, i, j):
        raise NotImplementedError

    def set_score(self, points):
        old_score = self.score
        self.score = points
        (self.board.statistics["score"])[self.player - 1] += self.score - old_score
        self.board.players_text[self.player - 1].text_pack.change_text(str((self.board.statistics["score"])[self.player - 1]))


class Frog(Character):
    def __init__(self, coordinates, board):
        super().__init__(coordinates, board)
        self.character = "frog"
        self.entity = GameManager.create_new_entity("character" + str(coordinates[0]) + str(coordinates[1]), "Frog", "board", 5)
        self.entity.set_scale(0.5, 0.5)

    def add_character_to_effective_squares(self):
        for i in range(self.board.board_size['x']):
            for j in range(self.board.board_size['y']):
                if isinstance(self.board.characters[(i, j)], Frog):
                    self.board.squares[(i, j)].characters[(self.coordinates[0], self.coordinates[1])] = self

    def appear(self, player):
        super().appear(player)
        self.entity.animator.change_animation("regular")
        self.set_score(1)

    def update_status_and_score(self, i, j):
        amount_of_frogs = None
        if self.player == 1:
            amount_of_frogs = (self.board.statistics["frog"])[0]
        elif self.player == 2:
            amount_of_frogs = (self.board.statistics["frog"])[1]
        if amount_of_frogs >= 2:
            self.entity.animator.change_animation("happy")
            self.set_score(2)

class Snowy(Character):
    def __init__(self, coordinates, board):
        super().__init__(coordinates, board)
        self.character = "snowy"
        self.entity = GameManager.create_new_entity("character" + str(coordinates[0]) + str(coordinates[1]), "Snowy", "board", 5)
        self.entity.set_scale(0.5, 0.5)

    def add_character_to_effective_squares(self):
        for i in range(self.board.board_size['x']):
            for j in range(self.board.board_size['y']):
                if isinstance(self.board.characters[(i, j)], Snowy):
                    self.board.squares[(i, j)].characters[(self.coordinates[0], self.coordinates[1])] = self

    def appear(self, player):
        super().appear(player)
        self.entity.animator.change_animation("sad")
        self.set_score(1)

    def update_status_and_score(self, i, j):
        amount_of_frogs = None
        if self.player == 1:
            amount_of_frogs = (self.board.statistics["snowy"])[0]
        elif self.player == 2:
            amount_of_frogs = (self.board.statistics["snowy"])[1]
        if amount_of_frogs >= 2:
            self.entity.animator.change_animation("happy")
            self.set_score(-20)

class Chick(Character):
    def __init__(self, coordinates, board):
        super().__init__(coordinates, board)
        self.character = "chick"
        self.entity = GameManager.create_new_entity("character" + str(coordinates[0]) + str(coordinates[1]), "Chick", "board", 5)
        self.entity.set_scale(0.5, 0.5)

    def add_character_to_effective_squares(self):
        for i in range(self.board.board_size['x']):
            for j in range(self.board.board_size['y']):
                if isinstance(self.board.characters[(i, j)], Chick):
                    self.board.squares[(i, j)].characters[(self.coordinates[0], self.coordinates[1])] = self

    def appear(self, player):
        super().appear(player)
        self.entity.animator.change_animation("regular")
        self.set_score(1)

    def update_status_and_score(self, i, j):
        amount_of_frogs = None
        if self.player == 1:
            amount_of_frogs = (self.board.statistics["chick"])[0]
        elif self.player == 2:
            amount_of_frogs = (self.board.statistics["chick"])[1]
        if amount_of_frogs >= 2:
            self.entity.animator.change_animation("happy")
            self.set_score(-20)



#game scene--------------------------------------------------------------------------------------------
class GameScene(Scene):

    def __init__(self):
        self.name = "game scene"
        self.board = None
        self.layout = None
        super().__init__()

    def start(self):
        self.board = Board((7, 9))
        self.put_board_in_place()
        self.layout = GameManager.create_new_entity(name = "layout", kind = "Layout", layer = 0)
        self.put_card_in_place()
        self.put_board_in_place()
        self.put_scores_in_place((30, -20))

    def update(self):
        self.board.update()
        self.board.scroll_and_scale()
        self.put_board_in_place()
        if GameManager.delta_time != 0:
            print("fps = ", 1/ GameManager.delta_time)
        if "escape" in GameManager.notifications:
            GameManager.change_current_scene("start scene")
        elif "r" in GameManager.notifications:
            GameManager.change_current_scene("game scene")

    def put_board_in_place(self):
        win_width, win_height = GameManager.win.get_size()
        x = (1/3) * win_width + ((2/3) * win_width - self.board.width)/2
        y = (1/6) * win_height + ((2/3) * win_height - self.board.height)/2
        self.board.entity.set_position(x, y)

    def put_card_in_place(self):
        self.board.card.align(620/2, GameManager.win.get_size()[1] / 2, (50, 60))

    def put_scores_in_place(self, offset):
        x, y = offset
        size = self.board.font_size
        self.board.players_text[0].set_position(GameManager.win.get_size()[0] - x - 2.4 * size, GameManager.win.get_size()[1] - y - size * 1.4)
        self.board.players_text[1].set_position(1/3 * GameManager.win.get_size()[0] + x, y)
        #self.board.players_text[0].set_position(1790, 970)
        #self.board.players_text[1].set_position(710, 0)