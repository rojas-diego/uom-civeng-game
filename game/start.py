from game.state import State
import pygame


def start(config: dict):
    state = State(config)

    while state.active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                state.active = False
        pygame.display.update()
