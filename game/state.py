import pygame
from game.assets import Assets
from game.constants import WINDOW_WIDTH, WINDOW_HEIGHT


class State():
    def __init__(self, config: dict):
        self.config = config
        self.init_window()
        self.translate_config()
        self.active = True
        self.assets = Assets()

    def init_window(self):
        pygame.display.set_caption('Railway Planner - ' + self.config['name'])
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.window.fill(pygame.color.Color(255, 255, 255))

    def translate_config(self):
        self.locations = []
        for loc in self.config['locations']:
            self.locations.append((loc['x'], loc['y']))

    def draw_locations(self):
        pass
