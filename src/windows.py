import pygame
import src.config as config

class Background:
    def __init__(self)->None:
        """Initialization og the background class"""
        self.image = pygame.image.load(config.BACKGROUND).convert()

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(0, 0, config.WIDTH, config.HEIGHT)

    def draw(self, screen) -> None:
        screen.blit(self.image, self.rect)
