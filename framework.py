import pygame
import copy


class Entity:
    def __init__(self, name, animations_pack):
        self.name = name
        self.transform = Transform()
        self.animator = None
        if animations_pack != None:
            self.animator = Animator(animations_pack)
    def copy(self):
        animations_pack = self.animator.animations_pack
        self.animator.animations_pack = None
        new_entity = copy.deepcopy(self)
        new_entity.animator.animations_pack = animations_pack
        return new_entity

class Transform:
    def __init__(self):
        self.position = {'x': 0,'y': 0}
        self.scale = {'x': 1,'y': 1}

    def set_positiono(self, x, y):
        self.position['x'] = x
        self.position['y'] = y

    def set_scale(self, x, y):
        self.scale['x'] = x
        self.scale['y'] = y


class Animator:
    def __init__(self, animations_pack):
        self.animations_pack = animations_pack
        self.current_animation = animations_pack.default_animation
        self.current_frame = 0


class Animation:
    def __init__(self, frames_number, name, file_name, frame_width, frame_height):
        self.speed = 1
        self.frames_number = frames_number
        self.frames = self.generate_frames(file_name, frame_width, frame_height)

    def generate_frames(self, file_name, frame_width, frame_height):
        sprite_sheet = pygame.image.load(file_name).convert()
        sheet_width = sprite_sheet.get_width()
        frames = []
        for frame_index in range(sheet_width//frame_width): # maybe there is a bug here in //
            frame = pygame.Surface((frame_width, frame_height)).convert()
            frame.blit(sprite_sheet, (0 , 0), (frame_index * frame_width, 0, frame_width, frame_height))
            frames.append(frame)
        return frames

# an animation pack is a set of animations for a type of entity , multiple entities from the same type can share
# the same animation pack since it's the same for of all of them, and no need to load
# spritesheets again and again for each one (flyweight design pattern)
class Animations_pack:
    def __init__(self):
        self.idle_animation = None
        self.animations = {}

    def add_animation(self, frames_number, name, file_name, frame_width, frame_height):
        new_animation = Animation(frames_number, name, file_name, frame_width, frame_height)
        if self.idle_animation == None:
            self.default_animation = name
        self.animations[name] = new_animation

    def set_default_animation(self, name):
        self.default_animation = name

class Scene:
    def __init__(self):
        self.initial_entities = {}
        self.entities = {}

    def restart_scene(self):
        entities = copy.deepcopy(self.initial_entities)

    def add_initial_entity(self, entity):
        self.initial_entities[entity.name] = entity
        new_entity = entity.copy()
        self.add_entity(new_entity)

    def add_entity(self, entity):
        self.entities[entity.name] = entity

class GameManager:
    clock = pygame.time.Clock()
    fps = 60
    win = None
    current_scene = None
    scenes = {}
    animations_packs = {}
    run = True

    @classmethod
    def init(cls):
        pygame.init()
        cls.win = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        cls.run_game()

    @classmethod
    def run_game(cls):
        Game.start()
        while cls.run == True:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    cls.run = False
            Game.update()
            cls.draw_entities()
        pygame.quit()

    @classmethod
    def draw_entities(cls):
        entities = cls.scenes[cls.current_scene].entities
        for entity_name in entities:
            entity = entities[entity_name]
            current_animation = entity.animator.animations_pack.animations[entity.animator.current_animation]
            current_frame = current_animation.frames[entity.animator.current_frame]
            x = entity.transform.position['x']
            y = entity.transform.position['y']
            cls.win.blit(current_frame, (x,y))
        pygame.display.update()

    # transition to another scene
    @classmethod
    def change_current_scene(cls, scene):
        cls.current_scene = scene

    # add new scene to the game
    @classmethod
    def create_new_scene(cls, scene):
        cls.scenes[scene] = Scene()

    # adds new animation pack to the game
    @classmethod
    def create_new_type(cls, type):
        cls.animations_packs[type] = Animations_pack()

    # adds animation to a animation pack
    @classmethod
    def create_new_animaton(cls, type, frames_number, name, file_name, frame_width, frame_height):
        cls.animations_packs[type].add_animation(frames_number, name, file_name, frame_width, frame_height)

    # create an entity of the game , this function can be used in 2 ways
    # 1) add an entity to a scene that each time you load the scene , the scene starts with this entity (status = "initial")
    # 2) add an entity in the middle of the game while the game is running (status = "temporary"
    @classmethod
    def create_new_entity(cls, type, name, status="temporary"):
        entity = Entity(name, cls.animations_packs[type])
        if status == "initial":
            cls.scenes[cls.current_scene].add_initial_entity(entity)
        else:
            cls.scenes[cls.current_scene].add_entity(entity)






# framework executable code --------------------------------
class Game:
    name = "new game ($ v $)"

    @classmethod
    def start(cls):
        GameManager.create_new_scene("example scene")
        GameManager.change_current_scene("example scene")
        GameManager.create_new_type("face")
        GameManager.create_new_animaton("face", 5, "talk", "animations/lip syncing.png", 400, 307)
        GameManager.create_new_entity("face", "face1", "initial")

    @classmethod
    def update(cls):
        x = 5
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