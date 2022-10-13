import time

import pandas
import pygame
import copy
import random
import bisect
import pandas as pd
from enum import Enum

class Entity:
    def __init__(self, name, animations_pack, layer = 0):
        self.children = []
        self.father = None
        self.name = name
        self.transform = self.Transform()
        self.animator = None
        self.kinematics = None
        self.renderer = None
        if animations_pack is not None:
            self.animator = self.Animator(animations_pack)
            self.add_renderer(layer)

    def copy(self):
        animations_pack = self.animator.animations_pack
        self.animator.animations_pack = None
        new_entity = copy.deepcopy(self)
        new_entity.animator.animations_pack = animations_pack
        return new_entity

    def set_father(self, father):
        if self.father is not None:
            GameManager.current_change_entities[self.father].children.remove(self.name)
        self.father = father
        GameManager.current_change_entities[father].children.append(self.name)

    def add_kinematics(self, x_velocity=0, y_velocity=0, x_acceleration=0, y_acceleration=0):
        self.kinematics = self.Kinematics(x_velocity, y_velocity, x_acceleration, y_acceleration)

    def add_renderer(self, layer):
        self.renderer = self.Renderer(layer)

    def set_velocity(self, x, y):
        for child_name in self.children:
            child = GameManager.current_change_entities[child_name]
            child.set_velocity(x + child.kinematics.velocity['x'] - self.kinematics.velocity['x'],
                               y + child.kinematics.velocity['y'] - self.kinematics.velocity['y'])
        if self.kinematics is not None:
            self.kinematics.velocity['x'] = x
            self.kinematics.velocity['y'] = y

    def set_acceleration(self, x, y):
        for child_name in self.children:
            child = GameManager.current_change_entities[child_name]
            child.set_acceleration(x + child.kinematics.acceleration['x'] - self.kinematics.acceleration['x'],
                                   y + child.kinematics.acceleration['y'] - self.kinematics.acceleration['y'])
        if self.kinematics is not None:
            self.kinematics.acceleration['x'] = x
            self.kinematics.acceleration['y'] = y

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
            child = GameManager.current_change_entities[child_name]
            child.set_position(x + child.transform.position['x'] - self.transform.position['x'],
                               y + child.transform.position['y'] - self.transform.position['y'])
        self.transform.position['x'] = x
        self.transform.position['y'] = y

    def set_scale(self, x, y):
        for child_name in self.children:
            child = GameManager.current_change_entities[child_name]
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
            if GameManager.current_time > self.last_updated + animation.time /animation.frames_number:
                self.last_updated = GameManager.current_time
                if animation.frames_number > 1:
                    if self.current_frame < animation.frames_number - 1:
                        self.current_frame += 1
                    elif animation.loop:
                        self.current_frame = 0

        def change_animation(self, animation):
            self.current_animation = animation


    class Renderer():
        def __init__(self, layer):
            self.layer = layer


class Animation:
    def __init__(self, frames_number, file_name, frame_width, frame_height, loop, time):
        self.time = time
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
# sprite sheets again and again for each one (flyweight design pattern)


class AnimationsPack:
    def __init__(self):
        self.default_animation = None
        self.animations = {}

    def add_animation(self, name, file_name, frames_number, frame_width, frame_height, speed, loop):
        new_animation = Animation(frames_number, file_name, frame_width, frame_height, loop, speed)
        if self.default_animation is None:
            self.default_animation = name
        self.animations[name] = new_animation

    def set_default_animation(self, name):
        self.default_animation = name

class PacksLoader:
    packs_file = "packs_file.xlsx"
    packs_df = pandas.read_excel(packs_file)
    xl = pandas.ExcelFile(packs_file)

    @classmethod
    def load_packs(cls):
        for name in cls.xl.sheet_names:
            pack_sheet = cls.xl.parse(name)
            GameManager.create_new_animations_pack(name)
            animations_list = list(pack_sheet.to_records(index=False))
            for animation in animations_list:
                GameManager.create_new_animation(name, *animation)


class Scene:
    def __init__(self):
        self.root_entity = Entity("root", None)
        self.entities = {"root": self.root_entity}
        self.layers_list = []
        self.layers_dict = {}

    def add_new_layer(self, entity):
        if entity.renderer.layer not in self.layers_dict:
            bisect.insort(self.layers_list, entity.renderer.layer)
            self.layers_dict[entity.renderer.layer] = {}
        self.layers_dict[entity.renderer.layer][entity.name] = entity


    def add_entity(self, entity):
        self.entities[entity.name] = entity
        if entity.renderer is not None:
            self.add_new_layer(entity)

    def start(self):
        raise NotImplementedError

    def end(self):
        self.entities = {"root": self.root_entity}
        self.layers_dict = {}
        self.layers_list = {}


class Timer:
    def __init__(self, time_limit):
        self.limit = time_limit
        self.time_up = True
        self.time = time_limit

    def update(self):
        if not self.time_up:
            self.time -= GameManager.delta_time
            if self.time <= 0:
                time_up = True

    def restart(self):
        self.time = self.limit
        self.time_up = False

    def change_time_limit(self, new_time_limit):
        self.time += new_time_limit - self.limit
        self.limit = new_time_limit


class GameManager:
    current_change_entities = None
    current_scene = None
    changing_scene = False
    scenes = {}
    current_animations_pack = None
    notifications = {}
    fps = 60
    clock = pygame.time.Clock()
    current_time = 0
    last_time = 0
    delta_time = 0
    win = None
    animations_packs = {}
    run = True

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
    def draw_entities(cls):
        white = (255, 255, 255)
        cls.win.fill(white)
        for layer in cls.scenes[cls.current_scene].layers_list:
            entities = cls.scenes[cls.current_scene].layers_dict[layer]
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
        cls.current_change_entities = cls.scenes[cls.current_scene].entities

    # add new scene to the game
    @classmethod
    def load_scenes(cls, scenes):
        for scene in scenes:
            scene = scene()
            cls.scenes[scene.name] = scene
            return cls.scenes[scene.name]

    # adds new animation pack to the game
    @classmethod
    def create_new_animations_pack(cls, kind):
        cls.animations_packs[kind] = AnimationsPack()

    # adds animation to a animation pack
    @classmethod
    def create_new_animation(cls, kind, name, file_name, frames_number, frame_width, frame_height, speed, loop):
        cls.animations_packs[kind].add_animation(name, file_name, frames_number, frame_width, frame_height, speed, loop)

    # create an entity of the game , this function can be used in 2 ways
    @classmethod
    def create_new_entity(cls, kind, name, father = None):
        entity = Entity(name, cls.animations_packs[kind])
        if father is not None:
            entity.set_father(father)
        else:
            entity.set_father("root")
            cls.scenes[cls.current_scene].add_entity(entity)
        return entity

