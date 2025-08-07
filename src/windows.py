import pygame

import src.config as config
from src.utils import get_hit_mask


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
        """Draw the background of the game

        Args:
            screen(pygame.Surface): object contaning the information of the screen of the game
        """
        screen.blit(self.image, self.rect)


class Pipe:
    def __init__(self, x: int, y: int, path_image: str) -> None:
        """Initialization of the pipe
        Args:
            x(int): x coordinate of the pipe
            y(int): y coordinate of the pipe
            path_image(str): image of the pipe
        """
        self.image = pygame.image.load(path_image).convert()
        self.x = x
        self.y = y
        self.w = self.image.get_width()
        self.h = self.image.get_height()
        self.velocity_x = -5
        self.image = pygame.image.load(path_image).convert()
        self.hit_mask = get_hit_mask(self.image) if self.image else None

    @property
    def center(self) -> float:
        """Center of the image"""
        return self.x + self.w / 2

    @property
    def rect(self) -> pygame.Rect:
        """Store background coordonates"""
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def newt_statuts(self, screen: pygame.Surface, draw: bool) -> None:
        """Draw the background of the game

        Args:
           screen(pygame.Surface): object contaning the information of the screen of the game
           draw(bool): if the pipe as to be drawn to the screen
        """
        self.x += self.velocity_x
        if draw:
            screen.blit(self.image, self.rect)
