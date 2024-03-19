import sys

import pygame
from pygame.locals import K_ESCAPE, K_SPACE, K_UP, KEYDOWN, QUIT

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
                if self.is_tap_event(event):
                    self.bird.flap()
            self.background.draw(self.screen)
            self.bird.next_statuts(self.screen)
            pygame.display.update()
            self.clock.tick(config.FPS)

    def check_quit_event(self, event: pygame.event) -> None:
        """Function that enable the user to quit the game

        Args:
           event(pygame.event): the event of the user
        """
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()

    def is_tap_event(self, event: pygame.event) -> bool:
        """Return True if there is an event

        Args:
           event(pygame.event): the event of the user

        Return:
           bool: ture if the event is a space, up or click left
        """
        m_left, _, _ = pygame.mouse.get_pressed()
        space_or_up = event.type == KEYDOWN and (
            event.key == K_SPACE or event.key == K_UP
        )
        screen_tap = event.type == pygame.FINGERDOWN
        return m_left or space_or_up or screen_tap
