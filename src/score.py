import pygame

import src.config as config


class Score:
    def __init__(self) -> None:
        """Initialization of the score class"""
        self.y = config.SCREEN_HEIGHT * 0.1
        self.score = 0
        self.digits = list(
            (
                pygame.image.load(f"assets/sprites/{num}.png").convert_alpha()
                for num in range(10)
            )
        )

    def add(self) -> None:
        """Add one to the score"""
        self.score += 1

    def draw(self, screen) -> None:
        """displays score in center of screen"""
        score_digits = [int(x) for x in list(str(self.score))]
        images = [self.digits[digit] for digit in score_digits]
        digits_width = sum(image.get_width() for image in images)
        x_offset = (config.SCREEN_WIDTH - digits_width) / 2

        for image in images:
            screen.blit(image, (x_offset, self.y))
            x_offset += image.get_width()