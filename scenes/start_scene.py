import pygame
from framework import GameManager, Scene

class StartScene(Scene):

    def __init__(self):
        self.name = "start scene"
        self.space_between_buttons = 50
        self.buttons = None
        super().__init__()

    def start(self):
        self.buttons = {"game": Button("game button"), "tutorial": Button("tutoiral button")}
        screen_width, screen_height = pygame.display.get_surface().get_size()
        button_width, button_height = self.buttons["game"].entity.get_size()
        buttons_x_position = (screen_width - button_width)/2
        buttons_y_position = (screen_height - button_height * len(self.buttons) - self.space_between_buttons * (len(self.buttons) - 1))/2
        self.buttons["game"].entity.set_position(buttons_x_position, buttons_y_position)
        self.buttons["tutorial"].entity.set_position(buttons_x_position, buttons_y_position + button_height + self.space_between_buttons)

    def update(self):
        for button_name in self.buttons:
            self.buttons[button_name].scale_when_hover()
        if self.buttons["game"].entity.check_clicked():
            GameManager.change_current_scene("game scene")
            return
        elif self.buttons["tutorial"].entity.check_clicked():
            GameManager.change_current_scene("experiment scene")
            return
        if "escape" in GameManager.notifications:
            pygame.quit()


class Button:
    max_scale = 1
    min_scale = 0.5
    scaling_speed = 5

    def __init__(self, name):
        self.entity = GameManager.create_new_entity(name, "Start menu button")
        self.entity.set_scale(self.min_scale, self.min_scale)

    def scale_when_hover(self):
        if self.entity.check_triggered():
            self.entity.set_scale(min(self.max_scale, self.entity.transform.scale['x'] + self.scaling_speed * GameManager.delta_time), min(self.max_scale, self.entity.transform.scale['y'] + self.scaling_speed * GameManager.delta_time))
        else:
            self.entity.set_scale(max(self.min_scale, self.entity.transform.scale['x'] - self.scaling_speed * GameManager.delta_time), max(self.min_scale, self.entity.transform.scale['y'] - self.scaling_speed * GameManager.delta_time))

