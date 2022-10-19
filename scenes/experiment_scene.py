from framework import GameManager, Scene, Timer
import random
import pygame

class ExperimentScene(Scene):

    def __init__(self):
        self.name = "experiment scene"
        self.son1 = None
        self.scene = None
        self.speed = random.randint(500, 1000)
        self.frogs_number = 3
        self.scale = 1
        self.pixels = 64
        self.son = None
        self.start_time = GameManager.current_time
        self.changed_position = False
        self.timer = Timer(2)
        self.scale_by = 0
        self.text = None
        self.font = None
        super().__init__()

    def start(self):
        frogs = []
        self.font = pygame.font.SysFont('arial', 60)
        for i in range(self.frogs_number):
            if i == 0:
                frogs.append(GameManager.create_new_entity("frog" + str(i),"Frog"))
            else:
                frogs.append(GameManager.create_new_entity("frog" + str(i), "Frog"))
                frogs[i].set_father("frog" + str(i - 1))
            frogs[i].set_position(60*i+300, 60*i+300)
            frogs[i].animator.current_animation = "happy"
            frogs[i].add_kinematics()
                #frogs[i].set_scale(self.scale, self.scale)
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
        #frogs[0].set_velocity(self.speed, self.speed)

    def update(self):
        if GameManager.delta_time != 0:
            pass
            #print(1/GameManager.delta_time)
        for i in range(self.frogs_number):
            if i == 0:
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
            if not self.timer.time_up:
                self.timer.update()
            else:
                self.entities["frog" + str(0)].set_scale(1.1, 1.1)
                self.entities["frog" + str(0)].set_position(300, 300)
                self.changed_position = True
                self.timer.restart()
                self.scale_by += 1/2

