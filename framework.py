import time
import pygame
import copy
import random


class Entity:
    def __init__(self, name, animations_pack):
        self.children = []
        self.scene = GameManager.current_scene
        self.switch = False
        self.father = None
        self.name = name
        self.transform = self.Transform()
        self.animator = None
        self.kinematics = None
        if animations_pack is not None:
            self.animator = self.Animator(animations_pack)

    def copy(self):
        animations_pack = self.animator.animations_pack
        self.animator.animations_pack = None
        new_entity = copy.deepcopy(self)
        new_entity.animator.animations_pack = animations_pack
        return new_entity

    def set_father(self, father):
        self.father = father
        GameManager.scenes[self.scene].initial_entities[father].children.append(self.name)

    def add_kinematics(self, x_velocity=0, y_velocity=0, x_acceleration=0, y_acceleration=0):
        self.kinematics = self.Kinematics(x_velocity, y_velocity, x_acceleration, y_acceleration)

    def set_velocity(self, x, y):
        for child_name in self.children:
            child = GameManager.scenes[self.scene].active_entities[child_name]
            child.set_velocity(x + child.kinematics.velocity['x'] - self.kinematics.velocity['x'],
                                  y + child.kinematics.velocity['y'] - self.kinematics.velocity['y'])
        if self.kinematics is not None:
            self.kinematics.velocity['x'] = x
            self.kinematics.velocity['y'] = y

    def set_acceleration(self, x, y):
        for child_name in self.children:
            child = GameManager.scenes[self.scene].active_entities[child_name]
            child.set_acceleration(x + child.kinematics.acceleration['x'] - self.kinematics.acceleration['x'],
                                  y + child.kinematics.acceleration['y'] - self.kinematics.acceleration['y'])
        if self.kinematics is not None:
            self.kinematics.acceleration['x'] = x
            self.kinematics.acceleration['y'] = y

    def updated(self):
        return self.switch == GameManager.entity_update_switch

    def flip_switch(self):
        self.switch = not self.switch

    def update(self):
        if self.animator is not None:
            self.animator.update()
        if self.kinematics is not None:
            self.kinematics.velocity['x'] += self.kinematics.acceleration['x'] * GameManager.delta_time
            self.kinematics.velocity['y'] += self.kinematics.acceleration['y'] * GameManager.delta_time
            self.transform.position['x'] += self.kinematics.velocity['x'] * GameManager.delta_time
            self.transform.position['y'] += self.kinematics.velocity['y'] * GameManager.delta_time

    def set_position(self, x, y):
        for child_name in self.children:
            child = GameManager.scenes[self.scene].active_entities[child_name]
            child.set_position(x + child.transform.position['x'] - self.transform.position['x'],
                                  y + child.transform.position['y'] - self.transform.position['y'])
        self.transform.position['x'] = x
        self.transform.position['y'] = y

    def set_scale(self, x, y):
        for child_name in self.children:
            child = GameManager.scenes[self.scene].active_entities[child_name]
            child.set_scale(x * child.transform.scale['x'] / self.transform.scale['x'],
                                  y * child.transform.scale['y'] / self.transform.scale['y'])
        self.transform.scale['x'] = x
        self.transform.scale['y'] = y

    class Transform:
        def __init__(self):
            self.position = {'x': 0, 'y': 0}
            self.scale = {'x': 1, 'y': 1}

    class Kinematics:
        def __init__(self, x_velocity, y_velocity, x_acceleration, y_acceleration):
            self.velocity = {'x': x_velocity, 'y': y_velocity}
            self.acceleration = {'x': x_acceleration, 'y': y_acceleration}

    class Animator:
        def __init__(self, animations_pack):
            self.animations_pack = animations_pack
            self.current_animation = animations_pack.default_animation
            self.current_frame = 0
            self.last_updated = 0

        def update(self):
            animation = self.animations_pack.animations[self.current_animation]
            if GameManager.current_time > self.last_updated + 0.1 / animation.speed:
                self.last_updated = GameManager.current_time
                if animation.frames_number > 1:
                    if self.current_frame < animation.frames_number - 1:
                        self.current_frame += 1
                    elif animation.loop:
                        self.current_frame = 0

        def change_animation(self, animation):
            self.current_animation = animation

class Animation:
    def __init__(self, frames_number, file_name, frame_width, frame_height, loop, speed):
        self.speed = speed
        self.frames_number = frames_number
        self.frames = self.generate_frames(file_name, frame_width, frame_height)
        self.loop = loop
        self.frame_size = {'x': frame_width, 'y': frame_height}

    def generate_frames(self, file_name, frame_width, frame_height):
        sprite_sheet = pygame.image.load(file_name).convert_alpha()
        sheet_width = sprite_sheet.get_width()
        frames = []
        for frame_index in range(sheet_width//frame_width):  # maybe there is a bug here in //
            frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA).convert_alpha()
            frame.blit(sprite_sheet, (0, 0), (frame_index * frame_width, 0, frame_width, frame_height))
            frames.append(frame)
        return frames

# an animation pack is a set of animations for a type of entity , multiple entities from the same type can share
# the same animation pack since it's the same for of all of them, and no need to load
# spritesheets again and again for each one (flyweight design pattern)


class AnimationsPack:
    def __init__(self):
        self.default_animation = None
        self.animations = {}

    def add_animation(self, frames_number, name, file_name, frame_width, frame_height, loop, speed):
        new_animation = Animation(frames_number, file_name, frame_width, frame_height, loop, speed)
        if self.default_animation is None:
            self.default_animation = name
        self.animations[name] = new_animation

    def set_default_animation(self, name):
        self.default_animation = name


class Scene:
    def __init__(self):
        self.initial_entities = {}
        self.active_entities = {}

    def add_initial_entity(self, entity):
        self.initial_entities[entity.name] = entity

    def add_active_entity(self, entity):
        self.active_entities[entity.name] = entity

    def start(self):
        for entity_name in self.initial_entities:
            new_entity = self.initial_entities[entity_name]
            self.add_active_entity(new_entity)

    def end(self):
        self.active_entities = {}


class GameManager:
    entity_update_switch = True
    current_scene = None
    scenes = {}
    fps = 60
    clock = pygame.time.Clock()
    current_time = 0
    last_time = 0
    delta_time = 0
    win = None
    animations_packs = {}
    run = True

    @classmethod
    def init(cls):
        pygame.init()
        cls.win = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        cls.run_game()
    @classmethod
    def flip_switch(cls):
        cls.entity_update_switch = not cls.entity_update_switch

    @classmethod
    def update_time(cls):
        cls.clock.tick(cls.fps)
        cls.current_time = time.time()
        cls.delta_time = cls.current_time - cls.last_time
        cls.last_time = cls.current_time

    @classmethod
    def start_time(cls):
        cls.last_time = cls.current_time = time.time()

    @classmethod
    def run_game(cls):
        Game.start()
        cls.scenes[cls.current_scene].start()
        cls.start_time()
        while cls.run:
            cls.update_time()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    cls.run = False
            Game.update()
            cls.draw_entities()
        pygame.quit()

    @classmethod
    def draw_entities(cls):
        white = (255, 255, 255)
        cls.win.fill(white)
        entities = cls.scenes[cls.current_scene].active_entities
        for entity_name in entities:
            entity = entities[entity_name]
            entity.update()
            if entity.animator is not None:
                current_animation = entity.animator.animations_pack.animations[entity.animator.current_animation]
                current_frame = current_animation.frames[entity.animator.current_frame]
                x = entity.transform.position['x']
                y = entity.transform.position['y']
                width = current_frame.get_width() * entity.transform.scale['x']
                height = current_frame.get_height() * entity.transform.scale['y']
                scaled_frame = pygame.transform.scale(current_frame, (width, height))
                cls.win.blit(scaled_frame, (x, y))
        pygame.display.update()
    # transition to another scene
    @classmethod
    def change_current_scene(cls, scene):
        cls.current_scene = scene

    # add new scene to the game
    @classmethod
    def create_new_scene(cls, scene):
        cls.scenes[scene] = Scene()
        return cls.scenes[scene]

    # adds new animation pack to the game
    @classmethod
    def create_new_type(cls, kind):
        cls.animations_packs[kind] = AnimationsPack()

    # adds animation to a animation pack
    @classmethod
    def create_new_animaton(cls, kind, frames_number, name, file_name, frame_width, frame_height, loop, speed):
        cls.animations_packs[kind].add_animation(frames_number, name, file_name, frame_width, frame_height, loop, speed)

    # create an entity of the game , this function can be used in 2 ways
    # 1) add an entity to a scene that each time you load the scene , the scene starts with this entity
    #   (status = "initial")
    # 2) add an entity in the middle of the game while the game is running (status = "temporary"
    @classmethod
    def create_new_entity(cls, kind, name, status="temporary"):
        entity = Entity(name, cls.animations_packs[kind])
        if status == "initial":
            cls.scenes[cls.current_scene].add_initial_entity(entity)
        else:
            cls.scenes[cls.current_scene].add_entity(entity)
        return entity


# framework executable code --------------------------------
class Game:
    son1 = None
    name = "new game ($ v $)"
    scene = None
    speed = 100
    trunks_number = 1
    scale = 1
    pixels = 64
    son = None
    start_time = None
    changed_position = False
    @classmethod
    def start(cls):
        cls.scene = GameManager.create_new_scene("example scene")
        GameManager.change_current_scene("example scene")
        GameManager.create_new_type("trunk")
        GameManager.create_new_animaton("trunk", 5, "happy", "animations/human idle.png", cls.pixels, cls.pixels, True, 2)
        trunks = []
        for i in range(cls.trunks_number):
            cls.speed = random.randint(100, 500)
            trunks.append(GameManager.create_new_entity("trunk", "trunk" + str(i), "initial"))
            trunks[i].add_kinematics(cls.speed, cls.speed)
            trunks[i].set_scale(cls.scale, cls.scale)
        cls.son = GameManager.create_new_entity("trunk", "son", "initial")
        cls.son.add_kinematics(cls.speed, cls.speed)
        cls.son.set_father("trunk0")
        cls.son.set_position(100, 100)
        cls.start_time = time.time()
        cls.son1 = GameManager.create_new_entity("trunk", "son1", "initial")
        cls.son1.add_kinematics(cls.speed, cls.speed)
        cls.son1.set_father("son")
        cls.son1.set_position(200, 200)
        cls.start_time = time.time()
    @classmethod
    def update(cls):
        for i in range(cls.trunks_number):
            cls.speed = random.randint(100, 500)
            t = cls.scene.active_entities["trunk" + str(i)]
            w, h = pygame.display.get_surface().get_size()
            if t.transform.position['x'] > w - cls.pixels * cls.scale:
                t.set_velocity(-cls.speed, t.kinematics.velocity['y'])
                #t.set_acceleration(-10000, t.kinematics.acceleration['y'])
            elif t.transform.position['x'] < 0:
                t.set_velocity(cls.speed, t.kinematics.velocity['y'])
                #t.set_acceleration(10000, t.kinematics.acceleration['y'])

            if t.transform.position['y'] > h - cls.pixels * cls.scale:
                t.set_velocity(t.kinematics.velocity['x'], -cls.speed)
                #t.set_acceleration(t.kinematics.acceleration['x'], -10000)
            elif t.transform.position['y'] < 0:
                t.set_velocity(t.kinematics.velocity['x'], cls.speed)
                #t.set_acceleration(t.kinematics.acceleration['x'], 10000)
        if not cls.changed_position and GameManager.current_time - cls.start_time > 2:
            print(GameManager.current_time - cls.start_time)
            t = cls.scene.active_entities["trunk" + str(0)]
            t.set_scale(2, 2)
            cls.changed_position = True

GameManager.init()


"""
pygame.init()
win = pygame.display.set_mode((2000, 1080/2))
picture = pygame.image.load("animations/lip syncing.png")
#win.blit(picture, (0,0))
pygame.display.update()
clock = pygame.time.Clock()
fps = 60
run = True
animations_pack = Animations_pack()
animations_pack.add_animation(5,"face change", "animations/lip syncing.png", 400, 307)
print(picture.get_width())
print(picture.get_height())
timer = 0
index = 0
face_change = animations_pack.animations["face change"]
while (run):
    timer += 1
    for event in pygame.event.get():
        clock.tick(fps)
        if event.type == pygame.QUIT:
            run = False
    if timer > 100000/2:
        win.blit(face_change.frames[index], (0,0))
        pygame.display.update()
        timer = 0
        if index < face_change.frames_number-1:
            index += 1
        else:
            index = 0
pygame.quit()
"""