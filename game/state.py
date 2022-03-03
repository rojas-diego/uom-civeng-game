import pygame
from game.assets import Assets
from game.constants import *
from game.utils import Location, LocationGraph, Connection
from router import connect_locations
import math
import statistics


class State():
    def __init__(self, config: dict):
        self.config = config
        self.connections_buffer = []
        self.active = True
        self.assets = Assets()
        self.cost = 0
        self.max_cost = 0
        self.timer = 0
        self.step = 0
        self.network_error = ''
        self.steps = [
            self.wait_step,
            self.load_connections_step,
            self.test_network_step,
        ]
        self.test_network_highlight = []
        self.test_network_idx = 0
        self.test_network_done = []
        self.traffic_congestion = 0
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
        self.update_animations()
        self.draw()
        pygame.display.update()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.active = False

    def update_animations(self):
        if self.step < len(self.steps):
            self.steps[self.step]()

    def wait_step(self):
        self.timer += 1
        if self.timer > 100:
            self.timer = 0
            self.step += 1

    def load_connections_step(self):
        self.timer += 1
        if len(self.connections_buffer):
            if self.timer % 20 == 0:
                self.graph.add_connection(
                    self.connections_buffer[0][0], self.connections_buffer[0][1])
                self.connections_buffer.pop(0)
                self.cost += self.graph.connections[-1].distance() * \
                    RAILWAY_UNIT_COST
                self.cost += STOP_COST
        else:
            self.timer = 0
            self.step += 1

    def test_network_step(self):
        self.timer += 1
        if self.timer % SHOW_CONNECTION_DELAY == 0:
            self.test_network_highlight.clear()
            connections = []
            for loc1 in self.locations:
                for loc2 in self.locations:
                    if loc1 != loc2 and Connection(loc1, loc2) not in connections:
                        connections.append(Connection(loc1, loc2))
            if len(self.test_network_done) >= len(connections):
                self.timer = 0
                self.step += 1
            for loc1 in self.locations:
                for loc2 in self.locations:
                    if loc1 != loc2 and Connection(loc1, loc2) not in self.test_network_done:
                        self.test_network_done.append(Connection(loc1, loc2))
                        directions = self.graph.pathfind(loc1, loc2)
                        if directions == None:
                            self.network_error = "Some locations aren't connected"
                            return
                        loads = []
                        for con in self.graph.connections:
                            loads.append(con.times_used)
                        self.traffic_congestion = statistics.variance(loads)
                        self.num_travels += 1
                        self.total_travel_time_mins += len(
                            directions) * CHANGE_TRAIN_TIME
                        for i in range(len(directions)):
                            directions[i].times_used += 1
                            self.total_travel_time_mins += directions[i].distance() * \
                                RAILWAY_UNIT_TRAVEL_TIME
                            self.test_network_highlight.append(directions[i])
                        return

    def draw(self):
        self.window.fill((255, 255, 255))
        self.draw_header()
        self.draw_connections()
        self.draw_locations()

    def draw_header(self):
        warning_text_sf = self.font.render(self.network_error, True, RED)
        text_rect = warning_text_sf.get_rect(
            center=(self.window.get_rect().center[0], HEADER_HEIGHT + 10))
        self.window.blit(warning_text_sf, text_rect)
        self.window.blit(self.assets.uom_logo, (0, 0))
        self.draw_header_value('Average Travel Time',
                               str(math.floor(self.total_travel_time_mins / self.num_travels)) + 'min' if self.num_travels else '0min', 500, GREY)
        self.draw_header_value('Cost', str(
            math.floor(self.cost)) + 'mi$', 670, GREY)
        self.draw_header_value('Traffic congestion',
                               f'{self.traffic_congestion:.2f}', 820, GREY)
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
                loc.name, True, (0, 0, 0), EXTREME_LIGHT_GREY)
            text_rect = text_surface.get_rect(
                center=(loc.x, loc.y + 20))
            self.window.blit(text_surface, text_rect)

    def draw_connections(self):
        for con in self.graph.connections:
            pygame.draw.line(self.window, GREEN if con in self.test_network_highlight else LIGHT_GREY,
                             (con.a.x, con.a.y), (con.b.x, con.b.y), 4 if con in self.test_network_highlight else 1)
