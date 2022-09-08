import pygame
class Entity:
    def __init__(self,animations_pack):
        self.transform = self.transform
        self.animator = None
        if(animations_pack != None):
            self.animator = Animator(animations_pack)
class Transform:
    def __init__(self):
        self.position = {'x': 0,'y': 0}
        self.scale = {'x': 1,'y': 1}
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
class coco:
    def __init__(self):
        self.a = 5

a1 = [2]
b1 = a1
b1 = [234342,234,234]
print(a1)