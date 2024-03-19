import pygame

import src.config as config


class Background:
    def __init__(self) -> None:
        """Initialization of the background class"""
        self.image = pygame.image.load(config.BACKGROUND).convert()
        self.image = pygame.transform.scale(
            self.image, (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        )

    @property
    def rect(self) -> pygame.Rect:
        """Store background coordonates"""
        return pygame.Rect(0, 0, config.SCREEN_WIDTH, config.SCREEN_HEIGHT)

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the background of the game"""
        screen.blit(self.image, self.rect)
