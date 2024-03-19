import pygame

import src.config as config
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

    def start(self):
        """Function that start the game"""

        while True:
            self.background.draw(self.screen)
            self.bird.draw(self.screen)
            pygame.display.update()


class Bird:
    def __init__(self) -> None:
        """Initialization of the class"""
        self.image = pygame.image.load(config.BIRD).convert()
        self.x = int(config.SCREEN_WIDTH * 0.2)
        self.y = int((config.SCREEN_HEIGHT - self.image.get_height()) / 2)
        self.w = self.image.get_width() if self.image else 0
        self.h = self.image.get_height() if self.image else 0

    @property
    def rect(self) -> pygame.Rect:
        """Store background coordonates"""
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the background of the game"""
        screen.blit(self.image, self.rect)
