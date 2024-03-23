import random
import sys

import numpy as np
import pygame
from pygame.locals import K_ESCAPE, K_SPACE, K_UP, KEYDOWN, QUIT

import src.config as config
from src.bird import Bird
from src.score import Score
from src.utils import pixel_collision
from src.windows import Background, Pipe


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
        self.bird_lowest_height = config.SCREEN_HEIGHT - self.bird.h
        self.clock = pygame.time.Clock()
        self.upper_pipes = []
        self.lower_pipes = []
        self.score = Score()

    def init_pipe(self) -> None:
        """Initialization of the pipe"""
        for i in np.arange(3, 9, 4):
            pipe_up, pipe_bot = self.generate_pipes()
            pipe_up.x = config.SCREEN_WIDTH + pipe_up.w * i
            pipe_bot.x = config.SCREEN_WIDTH + pipe_bot.w * i
            self.upper_pipes.append(pipe_up)
            self.lower_pipes.append(pipe_bot)

    def can_spawn_pipes(self) -> bool:
        """Tell if a new pipe can be spawn

        Returns:
           bool: True if a pip can be spawn false otherwise
        """
        last = self.upper_pipes[-1]
        if not last:
            return True

        return config.SCREEN_WIDTH - (last.x + last.w) > last.w * 2.5

    def spawn_new_pipes(self) -> None:
        """Add new pipes when the first pipe is about to be out of the screen"""
        upper, lower = self.generate_pipes()
        self.upper_pipes.append(upper)
        self.lower_pipes.append(lower)

    def remove_old_pipes(self) -> None:
        """Remove old pipes when they are out of the screen"""
        for pipe in self.upper_pipes:
            if pipe.x < -pipe.w:
                self.upper_pipes.remove(pipe)

        for pipe in self.lower_pipes:
            if pipe.x < -pipe.w:
                self.lower_pipes.remove(pipe)

    def play_game(self) -> None:
        """Function that play the game the game"""

        self.init_pipe()

        while True:
            for event in pygame.event.get():
                if self.check_quit_event(event):
                    pygame.quit()
                    sys.exit()
                if self.is_tap_event(event):
                    self.bird.flap()

            for i, pipe in enumerate(self.upper_pipes):
                if self.crossed(pipe):
                    self.score.add()

            self.background.draw(self.screen)
            self.score.draw(self.screen)

            if self.collided(self.upper_pipes) or self.collided(self.lower_pipes):
                break

            if self.can_spawn_pipes():
                self.spawn_new_pipes()
            self.remove_old_pipes()

            for up, low in zip(self.upper_pipes, self.lower_pipes):
                up.draw(self.screen)
                low.draw(self.screen)

            self.bird.next_statuts(self.screen)
            pygame.display.update()
            self.clock.tick(config.FPS)
            if self.bird.y > self.bird_lowest_height:
                break

        while True:
            for event in pygame.event.get():
                if self.check_quit_event(event):
                    pygame.quit()
                    sys.exit()

    def collided(self, pipes: list) -> bool:
        """Check the collision between bird and pipes

        Args:
           pipes(list): list of the pipes to the checked

        Returns:
           bool: Return true if the bird collides with pipes
        """

        for pipe in pipes:
            if pixel_collision(
                self.bird.rect, pipe.rect, self.bird.hit_mask, pipe.hit_mask
            ):
                return True
        return False

    def generate_pipes(self) -> tuple:
        """Generate pipes randomly

        Returns:
            tuple: contain pipe up and pipe down
        """

        base_y = config.SCREEN_HEIGHT

        gap_y = random.randrange(0, int(base_y * 0.6 - config.PIPE_GAP))
        gap_y += int(base_y * 0.2)
        pipe_x = config.SCREEN_WIDTH + 10

        pipetop = Pipe(pipe_x, gap_y - config.PIPE_HEIGHT, config.PIPETOP)

        pipebottom = Pipe(pipe_x, gap_y + config.PIPE_GAP, config.PIPEBOTTOM)

        return pipetop, pipebottom

    def check_quit_event(self, event: pygame.event) -> None:
        """Function that enable the user to quit the game

        Args:
           event(pygame.event): the event of the user
        """
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            return True
        return False

    def is_tap_event(self, event: pygame.event) -> bool:
        """Return True if there is an event

        Args:
           event(pygame.event): the event of the user

        Returns:
           bool: ture if the event is a space, up or click left
        """
        m_left, _, _ = pygame.mouse.get_pressed()
        space_or_up = event.type == KEYDOWN and (
            event.key == K_SPACE or event.key == K_UP
        )
        screen_tap = event.type == pygame.FINGERDOWN
        return m_left or space_or_up or screen_tap

    def crossed(self, pipe: Pipe) -> bool:
        """Tell if the bird cross a pipe

        Args:
           pipe(Pipe): pipe that we have to analyse

        Returns:
           bool: True if the bird cross a pipe false otherwise
        """
        return pipe.center <= self.bird.center < pipe.center - pipe.velocity_x
