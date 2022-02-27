from game.state import State


def start(config: dict):
    state = State(config)

    while state.active:
        state.update()
