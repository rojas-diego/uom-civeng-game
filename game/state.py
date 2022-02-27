import pygame
from game.assets import Assets
from game.constants import WINDOW_WIDTH, WINDOW_HEIGHT
from game.utils import Location
from router import connect_locations


class State():
    def __init__(self, config: dict):
        self.config = config
        self.init_window()
        self.load_config()
        self.connect_locations()
        self.active = True
        self.assets = Assets()

    def init_window(self):
        pygame.init()
        pygame.display.set_caption('Railway Planner - ' + self.config['name'])
        self.font = pygame.font.Font(pygame.font.get_default_font(), 14)
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.window.fill(pygame.color.Color(255, 255, 255))

    def load_config(self):
        self.locations = []
        for loc in self.config['locations']:
            self.locations.append(
                Location(loc['x'], loc['y'], loc['name'], loc['icon_path']))

    def connect_locations(self):
        connect_locations(self.locations, self.connect_handler,
                          self.need_bridge_to_connect_handler)

    def connect_handler(self, a, b):
        pass

    def need_bridge_to_connect_handler(self, a, b):
        pass

    def update(self):
        self.handle_events()
        self.draw()
        pygame.display.update()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.active = False

    def draw(self):
        self.window.fill((255, 255, 255))
        self.draw_locations()

    def draw_locations(self):
        for loc in self.locations:
            pygame.draw.circle(
                self.window, pygame.color.Color(100, 100, 100), (loc.x, loc.y), 10)
            text_surface = self.font.render(
                loc.name, True, (0, 0, 0))
            text_rect = text_surface.get_rect(
                center=(loc.x, loc.y + 20))
            self.window.blit(text_surface, text_rect)
