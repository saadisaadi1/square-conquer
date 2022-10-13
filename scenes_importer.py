from framework import GameManager
from scenes.game import GameScene
from scenes.start_scene import StartScene
from scenes.experiment_scene import ExperimentScene


class ScenesImporter(object):

    @classmethod
    def load_scenes(cls):
        GameManager.load_scenes([StartScene, GameScene, ExperimentScene])