import pygame

import src.config as config
from src.windows import Background


class Game:
    def __init__(self) -> None:
        """Initialization of the game class"""
        pygame.init()
        pygame.display.set_caption("Flappy Bird")
        self.screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
        self.background = Background()

    def start(self):
        """Function that start the game"""

        while True:
            self.background.draw(self.screen)
            pygame.display.update()
