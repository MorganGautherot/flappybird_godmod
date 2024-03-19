import sys

import pygame
from pygame.locals import K_ESCAPE, KEYDOWN, QUIT

import src.config as config
from src.bird import Bird
from src.windows import Background


class Game:
    def __init__(self) -> None:
        """Initialization of the game class"""
        pygame.init()
        pygame.display.set_caption("Flappy Bird")
        self.screen = pygame.display.set_mode(
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        )
        self.background = Background()
        self.bird = Bird()
        self.clock = pygame.time.Clock()

    def start(self) -> None:
        """Function that start the game"""

        while True:
            for event in pygame.event.get():
                self.check_quit_event(event)
            self.background.draw(self.screen)
            self.bird.next_statuts(self.screen)
            pygame.display.update()
            self.clock.tick(config.FPS)

    def check_quit_event(self, event: pygame.event) -> None:
        """Function that enable the user to quit the game"""
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()
