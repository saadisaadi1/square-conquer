from framework import GameManager
from game import Game_Scene


class ScenesImporter(object):

    @classmethod
    def load_scenes(cls):
        GameManager.load_scenes([Game_Scene])
        GameManager.change_current_scene("example scene")