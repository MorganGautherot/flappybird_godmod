import random
import sys

import numpy as np
import pygame
from pygame.locals import K_ESCAPE, K_SPACE, K_UP, KEYDOWN, QUIT

import src.config as config
from src.bird import Bird
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

    def init_pipe(self) -> None:
        """Initialization of the pipe"""
        for i in np.arange(3, 8, 3.5):
            pipe_up, pipe_bot = self.generate_pipes()
            pipe_up.x = config.SCREEN_WIDTH + pipe_up.w * i
            pipe_bot.x = config.SCREEN_WIDTH + pipe_bot.w * i
            self.upper_pipes.append(pipe_up)
            self.lower_pipes.append(pipe_bot)

    def can_spawn_pipes(self) -> bool:
        last = self.upper_pipes[-1]
        if not last:
            return True

        return config.SCREEN_WIDTH - (last.x + last.w) > last.w * 2.5

    def spawn_new_pipes(self):
        # add new pipe when first pipe is about to touch left of screen
        upper, lower = self.generate_pipes()
        self.upper_pipes.append(upper)
        self.lower_pipes.append(lower)

    def remove_old_pipes(self):
        # remove first pipe if its out of the screen
        for pipe in self.upper_pipes:
            if pipe.x < -pipe.w:
                self.upper_pipes.remove(pipe)

        for pipe in self.lower_pipes:
            if pipe.x < -pipe.w:
                self.lower_pipes.remove(pipe)

    def start(self) -> None:
        """Function that start the game"""

        self.init_pipe()

        while True:
            for event in pygame.event.get():
                self.check_quit_event(event)
                if self.is_tap_event(event):
                    self.bird.flap()
            self.background.draw(self.screen)

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
                pygame.quit()
                sys.exit()

    def generate_pipes(self) -> None:
        """Generate pipes randomly

        Return
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
