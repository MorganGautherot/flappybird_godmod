import random
import sys
from typing import List, Tuple

import numpy as np
import pygame
from pygame.locals import K_ESCAPE, K_SPACE, K_UP, KEYDOWN, QUIT

import src.config as config
from src.bird import Bird
from src.score import Score
from src.utils import collision
from src.windows import Background, Pipe


class Game:
    def __init__(self, bot_mode: bool = False) -> None:
        """Initialization of the game class

        Args:
            bot_mode: If True, enables AI bot control instead of human input
        """
        try:
            pygame.init()
            title = "Flappy Bird" + (" - AI Bot Mode" if bot_mode else "")
            pygame.display.set_caption(title)
            self.screen = pygame.display.set_mode(
                (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
            )
            self.background = Background()
            self.bird = Bird()
            self.bird_lowest_height = config.SCREEN_HEIGHT - self.bird.h
            self.clock = pygame.time.Clock()
            self.upper_pipes: List[Pipe] = []
            self.lower_pipes: List[Pipe] = []
            self.score = Score()

            # Bot configuration
            self.bot_mode = bot_mode
            self.bot = Bot(self) if bot_mode else None
        except Exception as e:
            print(f"Failed to initialize pygame: {e}")
            sys.exit(1)

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
        """Main game loop"""
        self.init_pipe()

        # Main game loop
        running = True
        while running:
            running = self._handle_game_loop()

        # Game over loop
        self._handle_game_over()

    def _handle_game_loop(self) -> bool:
        """Handle one iteration of the game loop

        Returns:
            bool: True to continue game, False to end
        """
        # Handle events (quit events always processed, tap events only in human mode)
        for event in pygame.event.get():
            if self.check_quit_event(event):
                pygame.quit()
                sys.exit()
            if not self.bot_mode and self.is_tap_event(event):
                self.bird.flap()

        # Bot decision making (only in bot mode)
        if self.bot_mode and self.bot:
            decision = self.bot.decide_action()
            if decision == "flap":
                self.bird.flap()

        # Update score
        self._update_score()

        # Check for collisions
        if self._check_collisions():
            return False

        # Update game objects
        self._update_pipes()
        self._update_and_draw()

        # Check if bird hit ground
        if self.bird.y > self.bird_lowest_height:
            return False

        return True

    def _handle_game_over(self) -> None:
        """Handle the game over state"""
        while True:
            for event in pygame.event.get():
                if self.check_quit_event(event):
                    pygame.quit()
                    sys.exit()

    def _update_score(self) -> None:
        """Update score when bird crosses pipes"""
        for pipe in self.upper_pipes:
            if self.crossed(pipe):
                self.score.add()

    def _check_collisions(self) -> bool:
        """Check for collisions between bird and pipes

        Returns:
            bool: True if collision detected
        """
        return collision(bird=self.bird, pipes=self.upper_pipes) or collision(
            bird=self.bird, pipes=self.lower_pipes
        )

    def _update_pipes(self) -> None:
        """Update pipe positions and manage pipe lifecycle"""
        if self.can_spawn_pipes():
            self.spawn_new_pipes()
        self.remove_old_pipes()

    def _update_and_draw(self) -> None:
        """Update all game objects and draw the frame"""
        self.background.draw(self.screen)

        for up, low in zip(self.upper_pipes, self.lower_pipes):
            up.next_status(self.screen, draw=True)
            low.next_status(self.screen, draw=True)

        self.score.draw(self.screen)
        self.bird.next_status(self.screen, draw=True)

        # Draw bot mode indicator
        if self.bot_mode:
            self._draw_bot_indicator()

        pygame.display.update()
        self.clock.tick(config.FPS)

    def _draw_bot_indicator(self) -> None:
        """Draw visual indicator that bot mode is active"""
        # Initialize font if not already done
        if not hasattr(self, "_bot_font"):
            pygame.font.init()
            self._bot_font = pygame.font.Font(None, 36)

        # Create text surface
        text = self._bot_font.render("AI BOT", True, (255, 255, 0))  # Yellow text
        text_rect = text.get_rect()
        text_rect.topright = (config.SCREEN_WIDTH - 20, 20)

        # Draw semi-transparent background
        background_rect = text_rect.copy()
        background_rect.inflate(20, 10)
        background_surface = pygame.Surface(
            (background_rect.width, background_rect.height)
        )
        background_surface.set_alpha(128)  # Semi-transparent
        background_surface.fill((0, 0, 0))  # Black background

        self.screen.blit(background_surface, background_rect)
        self.screen.blit(text, text_rect)

    def generate_pipes(self) -> Tuple[Pipe, Pipe]:
        """Generate pipes randomly

        Returns:
            Tuple[Pipe, Pipe]: contain pipe up and pipe down
        """
        base_y = config.SCREEN_HEIGHT

        gap_y = random.randrange(0, int(base_y * 0.6 - config.PIPE_GAP))
        gap_y += int(base_y * 0.2)
        pipe_x = config.SCREEN_WIDTH + 10

        pipetop = Pipe(pipe_x, gap_y - config.PIPE_HEIGHT, config.PIPETOP)
        pipebottom = Pipe(pipe_x, gap_y + config.PIPE_GAP, config.PIPEBOTTOM)

        return pipetop, pipebottom

    def check_quit_event(self, event: pygame.event.Event) -> bool:
        """Function that enable the user to quit the game

        Args:
           event(pygame.event.Event): the event of the user

        Returns:
            bool: True if quit event detected
        """
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            return True
        return False

    def is_tap_event(self, event: pygame.event.Event) -> bool:
        """Return True if there is a tap/flap event

        Args:
           event(pygame.event.Event): the event of the user

        Returns:
           bool: True if the event is a space, up or click left
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


class Bot:
    """AI bot for playing Flappy Bird automatically"""

    def __init__(self, game: "Game") -> None:
        """Initialize bot with reference to game

        Args:
            game: The game instance to control
        """
        self.game = game

    def decide_action(self) -> str:
        """Decide whether to flap or not based on lookahead simulation

        Returns:
            str: "flap" if bird should flap, "no_flap" otherwise
        """
        if not self.game.upper_pipes or not self.game.lower_pipes:
            return "no_flap"

        # Find the next pipe to navigate
        next_upper_pipe = None
        next_lower_pipe = None

        for upper, lower in zip(self.game.upper_pipes, self.game.lower_pipes):
            if upper.x + upper.w > self.game.bird.x:
                next_upper_pipe = upper
                next_lower_pipe = lower
                break

        if not next_upper_pipe:
            return "no_flap"

        return self._simulate_outcomes(next_upper_pipe, next_lower_pipe)

    def _simulate_outcomes(self, upper_pipe, lower_pipe) -> str:
        """Simulate both flap and no-flap outcomes

        Args:
            upper_pipe: The next upper pipe
            lower_pipe: The next lower pipe

        Returns:
            str: "flap" or "no_flap" based on collision simulation
        """
        # Create lightweight bird state copies (avoid pygame Surface copying)
        bird_no_flap_y = self.game.bird.y
        bird_no_flap_velocity = self.game.bird.velocity_y

        bird_flap_y = self.game.bird.y
        bird_flap_velocity = self.game.bird.flap_acceleration

        # Simulate one frame of physics for both scenarios
        # No flap scenario
        if bird_no_flap_velocity < self.game.bird.maximum_velocity_y:
            bird_no_flap_velocity += self.game.bird.downward_acceleration_y
        bird_no_flap_y += bird_no_flap_velocity
        bird_no_flap_y = max(
            min(bird_no_flap_y, self.game.bird.max_y), self.game.bird.min_y
        )

        # Flap scenario
        bird_flap_y += bird_flap_velocity
        bird_flap_y = max(min(bird_flap_y, self.game.bird.max_y), self.game.bird.min_y)

        # Check collisions using simple rectangle collision (faster than pixel-perfect)
        bird_rect = self.game.bird.rect

        # Create temporary rectangles for collision testing
        no_flap_rect = pygame.Rect(
            bird_rect.x, bird_no_flap_y, bird_rect.width, bird_rect.height
        )
        flap_rect = pygame.Rect(
            bird_rect.x, bird_flap_y, bird_rect.width, bird_rect.height
        )

        upper_rect = upper_pipe.rect
        lower_rect = lower_pipe.rect

        # Check collisions
        no_flap_collision = no_flap_rect.colliderect(
            upper_rect
        ) or no_flap_rect.colliderect(lower_rect)
        flap_collision = flap_rect.colliderect(upper_rect) or flap_rect.colliderect(
            lower_rect
        )

        # Decision logic: avoid collision if possible
        if no_flap_collision and not flap_collision:
            return "flap"
        elif flap_collision and not no_flap_collision:
            return "no_flap"
        elif no_flap_collision and flap_collision:
            # Both lead to collision, choose based on distance to gap center
            gap_center_y = (upper_pipe.y + upper_pipe.h + lower_pipe.y) / 2
            return "flap" if self.game.bird.y > gap_center_y else "no_flap"
        else:
            # Neither leads to collision, stay centered in gap
            gap_center_y = (upper_pipe.y + upper_pipe.h + lower_pipe.y) / 2
            return "flap" if self.game.bird.y > gap_center_y else "no_flap"
