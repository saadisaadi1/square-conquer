from framework import GameManager, Scene
import random
import pygame

class ExperimentScene(Scene):

    def __init__(self):
        self.name = "experiment scene"
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
            trunks.append(GameManager.create_new_entity("frog" + str(i), "frog"))
            trunks[i].add_kinematics()
            trunks[i].set_velocity(self.speed, self.speed)
            trunks[i].set_scale(self.scale, self.scale)
            """cls.son = GameManager.create_new_entity("son", "frog")
            cls.son.add_kinematics(0, 0)
            cls.son.set_father("trunk0")
            cls.son.set_position(100, 100)
            cls.start_time = time.time()
            cls.son1 = GameManager.create_new_entity("son1", "frog")
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