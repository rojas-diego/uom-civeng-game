import pygame
from game.assets import Assets
from game.constants import WINDOW_WIDTH, WINDOW_HEIGHT, HEADER_HEIGHT, HEADER_LINE_WIDTH, COLORS, GREY, UOM_MAIN_COLOR
from game.utils import Location, LocationGraph, Connection
from router import connect_locations


class State():
    def __init__(self, config: dict):
        self.config = config
        self.connections_buffer = []
        self.active = True
        self.assets = Assets()
        self.cost = 0
        self.max_cost = 0
        self.efficiency = 0
        self.num_travels = 0
        self.total_travel_time_mins = 0
        self.init_window()
        self.load_config()
        self.graph = LocationGraph(self.locations)
        self.connect_locations()

    def init_window(self):
        pygame.init()
        pygame.display.set_caption('Railway Planner - ' + self.config['name'])
        self.font = pygame.font.Font(pygame.font.get_default_font(), 14)
        self.big_font = pygame.font.Font(pygame.font.get_default_font(), 18)
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.window.fill(pygame.color.Color(255, 255, 255))

    def load_config(self):
        self.locations = []
        for loc in self.config['locations']:
            self.locations.append(
                Location(loc['x'], loc['y'] + HEADER_HEIGHT, loc['name'], loc['icon_path'], loc['color']))

    def connect_locations(self):
        connect_locations(self.locations, self.connect_handler,
                          self.need_bridge_to_connect_handler)
        for conn in self.connections_buffer:
            self.graph.add_connection(conn[0], conn[1])
        self.graph.pathfind(self.locations[0], self.locations[1])

    def connect_handler(self, a, b):
        for con in self.connections_buffer:
            if con[0] == a and con[1] == b:
                return
            if con[1] == a and con[0] == b:
                return
        self.connections_buffer.append((a, b))

    def need_bridge_to_connect_handler(self, a, b) -> bool:
        return True

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
        self.draw_header()
        self.draw_connections()
        self.draw_locations()

    def draw_header(self):
        self.window.blit(self.assets.uom_logo, (0, 0))
        self.draw_header_value('Average Travel Time',
                               str(self.total_travel_time_mins / self.num_travels) + 'min' if self.num_travels else '0min', 500, GREY)
        self.draw_header_value('Cost', str(self.cost) + 'mi$', 670, GREY)
        self.draw_header_value('Efficiency', '0%', 820, GREY)
        pygame.draw.line(self.window, UOM_MAIN_COLOR, (0, HEADER_HEIGHT -
                         HEADER_LINE_WIDTH), (WINDOW_WIDTH, HEADER_HEIGHT - HEADER_LINE_WIDTH), HEADER_LINE_WIDTH)

    def draw_header_value(self, title: str, value: str, x_offset: int, color: tuple):
        text_surface = self.font.render(title, True, color)
        text_rect = text_surface.get_rect(
            center=(x_offset, HEADER_HEIGHT / 2 - 10))
        self.window.blit(text_surface, text_rect)

        text_surface = self.big_font.render(value, True, color)
        text_rect = text_surface.get_rect(
            center=(x_offset, HEADER_HEIGHT / 2 + 10))
        self.window.blit(text_surface, text_rect)

    def draw_locations(self):
        for loc in self.locations:
            pygame.draw.circle(
                self.window, COLORS[loc.color], (loc.x, loc.y), 10)
            text_surface = self.font.render(
                loc.name, True, (0, 0, 0))
            text_rect = text_surface.get_rect(
                center=(loc.x, loc.y + 20))
            self.window.blit(text_surface, text_rect)

    def draw_connections(self):
        for con in self.graph.connections:
            pygame.draw.line(self.window, GREY,
                             (con.a.x, con.a.y), (con.b.x, con.b.y))
