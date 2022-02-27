import pygame
from game.constants import UOM_LOGO_PATH


class Assets():
    def __init__(self):
        self.uom_logo = pygame.image.load(UOM_LOGO_PATH)
