import pygame

import src.config as config
from src.utils import clamp


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

        self.vel_y = -9  # bird velocity along Y axis
        self.max_vel_y = 10  # max vel along Y, max descend speed
        self.min_vel_y = -8  # min vel along Y, max ascend speed
        self.acc_y = 1  # bird downward acceleration

        self.rot = 80  # bird current rotation
        self.vel_rot = -3  # bird rotation speed
        self.rot_min = -90  # bird min rotation angle
        self.rot_max = 20  # bird max rotation angle

        self.flap_acc = -9  # bird speed on flapping
        self.flapped = False  # True when player flaps

    @property
    def rect(self) -> pygame.Rect:
        """Store background coordonates"""
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def rotate(self) -> None:
        """change rotation of the bird"""
        self.rot = clamp(self.rot + self.vel_rot, self.rot_min, self.rot_max)

    def next_statuts(self, screen: pygame.Surface) -> None:
        """compute the next bird status"""
        if self.vel_y < self.max_vel_y and not self.flapped:
            self.vel_y += self.acc_y
        if self.flapped:
            self.flapped = False

        self.y = clamp(self.y + self.vel_y, self.min_y, self.max_y)
        self.rotate()

        self.draw(screen)

    def draw(self, screen) -> None:
        """Draw the bird of the game"""
        rotated_image = pygame.transform.rotate(self.image, self.rot)
        rotated_rect = rotated_image.get_rect(center=self.rect.center)
        screen.blit(rotated_image, rotated_rect)
