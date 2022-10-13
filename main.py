from framework import GameManager, PacksLoader
from scenes_importer import ScenesImporter
import pygame


def run_game():
    pygame.init()
    GameManager.win = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    PacksLoader.load_packs()
    ScenesImporter.load_scenes()
    GameManager.start_time()
    while GameManager.run:
        GameManager.scenes[GameManager.current_scene].start()
        while GameManager.run:
            if GameManager.changing_scene:
                GameManager.changing_scene = False
                break
            GameManager.update_time()
            GameManager.notifications = {}
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    GameManager.run = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    GameManager.notifications["mouse clicked"] = None
            GameManager.scenes[GameManager.current_scene].update()
            GameManager.draw_entities()
    pygame.quit()

if __name__ == '__main__':
    run_game()
