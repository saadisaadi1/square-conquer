from framework import *


class Game:
    def __init__(self):
        self.name = "new game"

    def start(self):
        create_new_scene("example scene")
        change_current_scene("example scene")
        create_new_type("face")
        create_new_animaton("face", 5, "animations/lip syncing.png","talk", 400, 307)
        create_new_entity("face", "face1", "initial")

    def update(self):
        x = 5