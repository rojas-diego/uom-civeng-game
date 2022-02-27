from game.state import State
import pygame


def start(config: dict):
    state = State(config)

    while state.active:
        state.update()
