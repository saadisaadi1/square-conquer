import time

import pandas
import pygame
import copy
import random
import bisect
import pandas as pd
from enum import Enum

class Entity:
    def __init__(self, name, animations_pack, layer = 0, text_pack = None):
        self.children = []
        self.father = None
        self.name = name
        self.transform = self.Transform()
        self.animator = None
        self.text_pack = None
        self.kinematics = None
        self.renderer = None
        if animations_pack is not None:
            self.animator = self.Animator(animations_pack)
            self.add_renderer(layer)
        elif text_pack is not None:
            self.add_text_pack(text_pack)
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

    def add_text_pack(self, text_pack):
        self.text_pack = self.Text(text_pack)

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

    def align(self, x, y, alignment = "center"):
        width, height = self.get_size()
        x -= alignment[0] / 100 * width
        y -= alignment[1] / 100 * height
        self.set_position(x, y)

    def align_to_other_entity(self, other_entity, other_alignment = (50, 50), alignment = (50, 50)):
        x = other_entity.transform.position['x']
        y = other_entity.transform.position['y']
        width, height = other_entity.get_size()
        x += width * other_alignment[0] / 100
        y += height * other_alignment[1] / 100
        self.align(x, y, alignment)

    def set_scale(self, x, y):
        if x == 0 or y == 0:
            raise Exception("can't set scale to 0")
        x, y = self.__calculate_the_multiplicative_factor(x, y)
        self.__set_position_when_scaling(self.transform.position, x, y)
        self.__scale_with_multiplicative_factor(x, y)

    def __calculate_the_multiplicative_factor(self, x, y):
        x = x / self.transform.scale['x']
        y = y / self.transform.scale['y']
        return (x, y)

    def __scale_with_multiplicative_factor(self, x, y):
        for child_name in self.children:
            child = GameManager.current_change_entities[child_name]
            child.__scale_with_multiplicative_factor(x, y)
        #print("old_scale = ", self.transform.scale, "name = ", self.name)
        self.transform.scale['x'] *= x
        self.transform.scale['y'] *= y
        #print("new_scale = ", self.transform.scale, "name = ", self.name)

    def __set_position_when_scaling(self, scaled_ancestor_position, x, y):
        for child_name in self.children:
            child = GameManager.current_change_entities[child_name]
            child_position = child.transform.position
            child_old_scale = child.transform.scale
            distance = {'x': child_position['x'] - scaled_ancestor_position['x'], 'y': child_position['y'] - scaled_ancestor_position['y']}
            child.transform.position['x'] = scaled_ancestor_position['x'] + distance['x'] * x
            child.transform.position['y'] = scaled_ancestor_position['y'] + distance['y'] * y
            child.__set_position_when_scaling(scaled_ancestor_position, x, y)

    def get_size(self):
        width = self.animator.animations_pack.animations[self.animator.current_animation].frame_size['x'] * self.transform.scale['x']
        height = self.animator.animations_pack.animations[self.animator.current_animation].frame_size['y'] * self.transform.scale['y']
        return (width, height)


    def check_triggered(self):
        if self.animator is not None:
            point = pygame.mouse.get_pos()
            current_animation = self.animator.animations_pack.animations[self.animator.current_animation]
            current_frame = current_animation.frames[self.animator.current_frame]
            frame_width = current_animation.frame_size['x']
            frame_height = current_animation.frame_size['y']
            rect = current_frame.get_rect()
            rect.update( self.transform.position['x'], self.transform.position['y'], frame_width * self.transform.scale['x'], frame_height * self.transform.scale['y'])
            return rect.collidepoint(point)
        else:
            return False


    def check_clicked(self):
        if "mouse clicked" in GameManager.notifications:
            return self.check_triggered()
        else:
            return False

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
            self.time_remained = 0

        def update(self):
            animation = self.animations_pack.animations[self.current_animation]
            if animation.frames_number > 1:
                if animation.loop:
                    #print("delta", GameManager.delta_time + self.time_remained)
                    #print("time per frame", animation.time_per_frame)
                    #print("delta/time", (GameManager.delta_time + self.time_remained) / animation.time_per_frame)
                    #print(int(self.current_frame + (GameManager.delta_time + self.time_remained) // animation.time_per_frame) % animation.frames_number)
                    self.current_frame = int(self.current_frame + (GameManager.delta_time + self.time_remained) // animation.time_per_frame) % animation.frames_number
                else:

                    self.current_frame = int(min(self.current_frame + (GameManager.delta_time + self.time_remained) // animation.time_per_frame, animation.frames_number - 1)) % animation.frames_number

                self.time_remained = (GameManager.delta_time + self.time_remained) % animation.time_per_frame

        def change_animation(self, animation):
            self.current_animation = animation
            self.time_remained = 0

    class Text:
        def __init__(self, text_pack):
            self.font, self.text, self.antialiasing, self.color = text_pack
            self.surface = self.font.render(self.text, False, self.color).convert_alpha()

        def change_text(self, new_text):
            self.text = new_text
            self.surface = self.font.render(self.text, False, self.color).convert_alpha()

        def change_font(self, new_font):
            self.font = new_font
            self.surface = self.font.render(self.text, False, self.color).convert_alpha()

        def change_color(self, new_color):
            self.color = new_color
            self.surface = self.font.render(self.text, False, self.color).convert_alpha()

        def antialiasing(self):
            self.antialiasing = not self.antialiasing()
            self.surface = self.font.render(self.text, False, self.color).convert_alpha()

    class Renderer():
        def __init__(self, layer):
            self.layer = layer


class Animation:
    def __init__(self, frames_number, file_name, frame_width, frame_height, loop, time):
        self.time = time
        self.frames_number = frames_number
        self.time_per_frame = self.time / self.frames_number
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
        if entity.renderer.layer not in self.layers_list:
            bisect.insort(self.layers_list, entity.renderer.layer)
            self.layers_dict[entity.renderer.layer] = {}
        current_layer_dict = self.layers_dict[entity.renderer.layer]
        current_layer_dict[entity.name] = entity


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
        self.time_up = False
        self.time = time_limit

    def update(self):
        if not self.time_up:
            self.time -= GameManager.delta_time
            if self.time <= 0:
                self.time_up = True

    def restart(self):
        self.time = self.limit
        self.time_up = False

    def change_time_limit(self, new_time_limit):
        self.time += new_time_limit - self.limit
        self.limit = new_time_limit


class GameManager:
    background_color = (255, 255, 255)
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
        cls.win.fill(cls.background_color)
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
                elif entity.text_pack is not None:
                    x = entity.transform.position['x']
                    y = entity.transform.position['y']
                    width, height = entity.text_pack.surface.get_size()
                    width *= entity.transform.scale['x']
                    height *= entity.transform.scale['y']
                    scaled_text = pygame.transform.smoothscale(entity.text_pack.surface, (width, height))
                    cls.win.blit(scaled_text, (x, y))
        pygame.display.update()

    # transition to another scene
    @classmethod
    def change_current_scene(cls, scene):
        cls.current_scene = scene
        cls.current_change_entities = cls.scenes[cls.current_scene].entities
        GameManager.changing_scene = True

    # loads all the scenes in the given list into the game, the first scene in the list is set to the current scene
    @classmethod
    def load_scenes(cls, scenes):
        for i, scene in enumerate(scenes):
            new_scene = scene()
            cls.scenes[new_scene.name] = new_scene
            if i == 0:
                cls.change_current_scene(new_scene.name)

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
    def create_new_entity(cls, name, kind = None, father = None, layer = 0, text_pack = None):
        animations_pack = None
        if kind in cls.animations_packs:
            animations_pack = cls.animations_packs[kind]

        entity = Entity(name = name, animations_pack = animations_pack, layer = layer, text_pack = text_pack)
        if father is not None:
            entity.set_father(father)
        else:
            entity.set_father("root")
        cls.scenes[cls.current_scene].add_entity(entity)
        return entity

