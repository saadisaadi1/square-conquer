from framework import GameManager, Scene
import random
import pygame

class Character:
    pass


class Board:
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

#--------------------------------------------------------------------------------------------
class Game_Scene(Scene):

    def __init__(self):
        self.name = "example scene"
        self.son1 = None
        self.scene = None
        self.speed = random.randint(500, 1000)
        self.trunks_number = 300
        self.scale = 1.5
        self.pixels = 64
        self.son = None
        self.start_time = None
        self.changed_position = False
        super().__init__()

    def start(self):
        trunks = []
        for i in range(self.trunks_number):
            trunks.append(GameManager.create_new_entity("frog", "frog" + str(i)))
            trunks[i].add_kinematics()
            #if i != 0:
            trunks[i].set_velocity(self.speed, self.speed)
            trunks[i].set_scale(self.scale, self.scale)
            """cls.son = GameManager.create_new_entity("frog", "son")
            cls.son.add_kinematics(0, 0)
            cls.son.set_father("trunk0")
            cls.son.set_position(100, 100)
            cls.start_time = time.time()
            cls.son1 = GameManager.create_new_entity("frog", "son1")
            cls.son1.add_kinematics(0, 0)
            cls.son1.set_father("son")
            cls.son1.set_position(200, 200)
            cls.start_time = time.time()
            trunks[0].set_velocity(100, 100)
            """

    def update(self):
        if GameManager.delta_time != 0:
            # pass
            print(1/GameManager.delta_time)
        for i in range(self.trunks_number):
            self.speed = random.randint(100, 500)
            t = self.entities["frog" + str(i)]
            w, h = pygame.display.get_surface().get_size()
            if t.transform.position['x'] > w - self.pixels * self.scale:
                t.set_velocity(-self.speed, t.kinematics.velocity['y'])
                # t.set_acceleration(-10000, t.kinematics.acceleration['y'])
            elif t.transform.position['x'] < 0:
                t.set_velocity(self.speed, t.kinematics.velocity['y'])
                # t.set_acceleration(10000, t.kinematics.acceleration['y'])

            if t.transform.position['y'] > h - self.pixels * self.scale:
                t.set_velocity(t.kinematics.velocity['x'], -self.speed)
                # t.set_acceleration(t.kinematics.acceleration['x'], -10000)
            elif t.transform.position['y'] < 0:
                t.set_velocity(t.kinematics.velocity['x'], self.speed)
                # t.set_acceleration(t.kinematics.acceleration['x'], 10000)
        """if not cls.changed_position and GameManager.current_time - cls.start_time > 2:
            t = cls.scene.active_entities["trunk" + str(0)]
            t.set_scale(2, 2)
            cls.changed_position = True"""


