import pygame

import src.config as config
from src.utils import clamp, get_hit_mask


class Bird:
    def __init__(self) -> None:
        """Initialization of the class"""

        self.image = pygame.image.load(config.BIRD).convert()
        self.x = int(config.SCREEN_WIDTH * 0.2)
        self.y = int((config.SCREEN_HEIGHT - self.image.get_height()) / 2)
        self.w = self.image.get_width() if self.image else 0
        self.h = self.image.get_height() if self.image else 0

        self.min_y = -2 * self.h
        self.max_y = config.SCREEN_HEIGHT - self.h * 0.75

        self.velocity_y = -9
        self.maximum_velocity_y = 10
        self.minimum_velocity_y = -8
        self.downward_acceleration_y = 1

        self.current_rotation = 80
        self.velocity_rotation = -3
        self.rotation_minimum = -90
        self.rotation_maximum = 20

        self.flap_acceleration = -9
        self.bird_has_flapped = False

        self.hit_mask = get_hit_mask(self.image) if self.image else None

    @property
    def center(self) -> float:
        """Center of the image"""
        return self.x + self.w / 2

    @property
    def rect(self) -> pygame.Rect:
        """Store bird coordonates

        Return:
           pygame.Rect: return the pygame object containing the coordonate of the bird
        """
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def rotate(self) -> None:
        """Change rotation of the bird"""
        self.current_rotation = clamp(
            self.current_rotation + self.velocity_rotation,
            self.rotation_minimum,
            self.rotation_maximum,
        )

    def next_statuts(self, screen: pygame.Surface) -> None:
        """Compute the next bird status

        Args:
            screen(pygame.Surface): object contaning the information of the screen of the game
        """
        if self.velocity_y < self.maximum_velocity_y and not self.bird_has_flapped:
            self.velocity_y += self.downward_acceleration_y
        if self.bird_has_flapped:
            self.bird_has_flapped = False

        self.y = clamp(self.y + self.velocity_y, self.min_y, self.max_y)
        self.rotate()
        self.draw(screen)

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the bird of the game

        Args:
            screen(pygame.Surface): object contaning the information of the screen of the game
        """
        rotated_image = pygame.transform.rotate(self.image, self.current_rotation)
        rotated_rect = rotated_image.get_rect(center=self.rect.center)
        screen.blit(rotated_image, rotated_rect)

    def flap(self) -> None:
        """Changes the bird's coordinates for a wingbeat if the bird is still
        visible on the screen"""
        if self.y > self.min_y:
            self.velocity_y = self.flap_acceleration
            self.bird_has_flapped = True
            self.current_rotation = 80
