import pygame
from game.assets import Assets
from game.constants import *
from game.utils import Location, LocationGraph, Connection
from router import connect_locations
import math
import statistics


class State():
    def __init__(self, config: dict):
        # Game state
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
        self.font = None
        self.big_font = None
        self.window = None
        self.init_window()
        self.load_config()
        # Create the network of connections
        self.graph = LocationGraph(self.locations)
        self.connect_locations()

    def init_window(self):
        # Code from the pygame tutorial to display a window on screen
        pygame.init()
        pygame.display.set_caption('Railway Planner - ' + self.config['name'])
        self.font = pygame.font.Font(pygame.font.get_default_font(), 14)
        self.big_font = pygame.font.Font(pygame.font.get_default_font(), 18)
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.window.fill(pygame.color.Color(255, 255, 255))

    def load_config(self):
        # Load the locations from the config into an array
        self.locations = []
        for loc in self.config['locations']:
            self.locations.append(
                Location(loc['x'], loc['y'] + HEADER_HEIGHT, loc['name'], loc['color']))

    def connect_locations(self):
        # Call the student's function to connect the connections
        connect_locations(self.locations, self.connect_handler)

    def connect_handler(self, a, b):
        # The function called from the student's function

        # We don't want want to connect a location to itself
        if a == b:
            return
        # We don't want to connect stuff twice
        for con in self.connections_buffer:
            if con[0] == a and con[1] == b:
                return
            if con[1] == a and con[0] == b:
                return
        self.connections_buffer.append((a, b))

    def update(self):
        self.handle_events()
        self.update_animations()
        self.draw()
        # Update the window
        pygame.display.update()

    def handle_events(self):
        # Close the program when the window is closed
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.active = False

    def update_animations(self):
        if self.step < len(self.steps):
            self.steps[self.step]()

    def wait_step(self):
        # Wait a 100 frames and do nothing
        # Increment the timer each step
        self.timer += 1
        if self.timer > 100:
            # When we reach 100, go to the next step
            self.timer = 0
            self.step += 1

    def load_connections_step(self):
        self.timer += 1
        if len(self.connections_buffer):
            # Every 20 frames, add a connection to the screen
            if self.timer % 20 == 0:
                # Add a connection to our network.
                # We're adding connections one at a time to animate them.
                self.graph.add_connection(
                    self.connections_buffer[0][0], self.connections_buffer[0][1])
                self.connections_buffer.pop(0)
                ###############
                #### COST #####
                ###############
                self.cost += self.graph.connections[-1].distance() * \
                    RAILWAY_UNIT_COST
                self.cost += CONNECTION_COST
        else:
            # When the connections buffer is empty, we go to the next step
            self.timer = 0
            self.step += 1

    def test_network_step(self):
        self.timer += 1
        # Every 25 frames we test a new itinerary
        # We try going from point A to point B and we see how much time it takes
        if self.timer % SHOW_CONNECTION_DELAY == 0:
            self.test_network_highlight.clear()
            connections = []
            for loc1 in self.locations:
                for loc2 in self.locations:
                    if loc1 != loc2 and Connection(loc1, loc2) not in connections:
                        connections.append(Connection(loc1, loc2))
            if len(self.test_network_done) >= len(connections):
                for conn in self.graph.connections:
                    print(conn)
                self.timer = 0
                self.step += 1
            for loc1 in self.locations:
                for loc2 in self.locations:
                    if loc1 != loc2 and Connection(loc1, loc2) not in self.test_network_done:
                        self.test_network_done.append(Connection(loc1, loc2))
                        # We try to go from loc1 to loc2 using the shortest path.
                        # The function returns each stop to go to our destination.
                        directions = self.graph.pathfind(loc1, loc2)
                        if directions == None:
                            self.network_error = "Some locations aren't connected"
                            return
                        loads = []
                        for con in self.graph.connections:
                            loads.append(con.times_used)
                        if len(loads) > 1:
                            self.traffic_congestion = statistics.variance(
                                loads)
                        else:
                            self.traffic_congestion = 0
                        ##############################
                        #### Average travel time #####
                        ##############################
                        self.num_travels += 1
                        self.total_travel_time_mins += len(
                            directions) * CHANGE_TRAIN_TIME
                        for i in range(len(directions)):
                            self.total_travel_time_mins += directions[i].distance() * \
                                RAILWAY_UNIT_TRAVEL_TIME
                            self.test_network_highlight.append(directions[i])
                        return

####################################################
#### DRAW FUNCTION #################################
####################################################

    def draw(self):
        # Draw everything on screen every frame.

        # Draw a white background
        self.window.fill((255, 255, 255))
        # Draw the game header
        self.draw_header()
        # Draw each connection
        self.draw_connections()
        # Draw each connection
        self.draw_locations()

    def draw_header(self):
        # Pygame code to display the whole header
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
        # Pygame code to display one KPI
        text_surface = self.font.render(title, True, color)
        text_rect = text_surface.get_rect(
            center=(x_offset, HEADER_HEIGHT / 2 - 10))
        self.window.blit(text_surface, text_rect)

        text_surface = self.big_font.render(value, True, color)
        text_rect = text_surface.get_rect(
            center=(x_offset, HEADER_HEIGHT / 2 + 10))
        self.window.blit(text_surface, text_rect)

    def draw_locations(self):
        # Draw each location with a circle and the name.
        for loc in self.locations:
            pygame.draw.circle(
                self.window, COLORS[loc.color], (loc.x, loc.y), 10)
            text_surface = self.font.render(
                loc.name, True, (0, 0, 0), EXTREME_LIGHT_GREY)
            text_rect = text_surface.get_rect(
                center=(loc.x, loc.y + 20))
            self.window.blit(text_surface, text_rect)

    def draw_connections(self):
        # For each connection draw a grey line.
        for con in self.graph.connections:
            pygame.draw.line(self.window, GREEN if con in self.test_network_highlight else LIGHT_GREY,
                             (con.a.x, con.a.y), (con.b.x, con.b.y), 4 if con in self.test_network_highlight else 1)
