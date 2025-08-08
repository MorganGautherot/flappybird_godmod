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
    def __init__(
        self, bot_mode: bool = False, seed: int = None, bot_type: str = "single"
    ) -> None:
        """Initialization of the game class

        Args:
            bot_mode: If True, enables AI bot control instead of human input
            seed: Random seed for reproducible games (None for random seed)
            bot_type: Type of bot to use ("single" for Bot, "two_pipes" for Bot_two_pipes)
        """
        try:
            # Set random seed for reproducible games
            if seed is not None:
                random.seed(seed)
                self.seed = seed
            else:
                import time

                self.seed = int(time.time() * 1000000) % 2**32
                random.seed(self.seed)

            # Initialize pygame and display
            pygame.init()
            title = "Flappy Bird" + (" - AI Bot Mode" if bot_mode else "")
            pygame.display.set_caption(title)
            self.screen = pygame.display.set_mode(
                (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
            )
            self.background = Background()
            self.clock = pygame.time.Clock()

            self.bird = Bird()
            self.bird_lowest_height = config.SCREEN_HEIGHT - self.bird.h
            self.upper_pipes: List[Pipe] = []
            self.lower_pipes: List[Pipe] = []
            self.score = Score()

            # Bot configuration
            self.bot_mode = bot_mode
            if bot_mode:
                if bot_type == "two_pipes":
                    self.bot = Bot_two_pipes(self)
                else:
                    self.bot = Bot(self)
            else:
                self.bot = None

            # Pipe generation state
            self.last_gap_y = (
                None  # Track last pipe gap position for smooth transitions
            )
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
        """Generate pipes with constrained gap transitions for playability

        Returns:
            Tuple[Pipe, Pipe]: contain pipe up and pipe down
        """
        pipe_x = config.SCREEN_WIDTH + 10

        # Calculate gap TOP Y position with constraints
        if self.last_gap_y is None:
            # First pipe - center it in the playable area
            gap_y = (config.MIN_GAP_Y + config.MAX_GAP_Y) // 2
        else:
            # Subsequent pipes - constrain transition distance
            min_allowed_gap = max(
                config.MIN_GAP_Y, self.last_gap_y - config.MAX_GAP_TRANSITION
            )
            max_allowed_gap = min(
                config.MAX_GAP_Y, self.last_gap_y + config.MAX_GAP_TRANSITION
            )

            gap_y = random.randint(min_allowed_gap, max_allowed_gap)

        # Store gap position for next pipe generation
        self.last_gap_y = gap_y

        # Create pipes with gap at calculated position
        # gap_y is the top of the gap, so top pipe ends at gap_y, bottom pipe starts at gap_y + GAP
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


class Bot_two_pipes:
    """Advanced AI bot that considers two consecutive actions (moves) ahead for better decision making"""

    def __init__(self, game: "Game") -> None:
        """Initialize bot with reference to game

        Args:
            game: The game instance to control
        """
        self.game = game

    def decide_action(self) -> str:
        """Decide whether to flap or not based on two-move lookahead simulation

        First check if immediate action is needed (like original bot),
        then use two-move simulation for fine-tuning.

        Returns:
            str: "flap" if bird should flap now, "no_flap" otherwise
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

        # First, check if we need immediate action to avoid collision
        immediate_decision = self._check_immediate_collision(
            next_upper_pipe, next_lower_pipe
        )
        if immediate_decision is not None:
            return immediate_decision

        # If no immediate danger, use two-move simulation for optimal positioning
        return self._simulate_two_moves(next_upper_pipe, next_lower_pipe)

    def _simulate_two_moves(self, upper_pipe, lower_pipe) -> str:
        """Simulate two consecutive moves and choose the best first action

        Strategy:
        1. First filter out sequences that cause game over
        2. Among safe sequences, choose the one closest to gap center

        Args:
            upper_pipe: The upper pipe to navigate
            lower_pipe: The lower pipe to navigate

        Returns:
            str: "flap" or "no_flap" based on best two-move sequence
        """
        # All possible two-move sequences
        move_sequences = [
            (True, True),  # flap, then flap
            (True, False),  # flap, then no_flap
            (False, True),  # no_flap, then flap
            (False, False),  # no_flap, then no_flap
        ]

        # Evaluate all sequences
        safe_sequences = []
        unsafe_sequences = []

        for move1, move2 in move_sequences:
            result = self._evaluate_two_move_sequence_survival(
                upper_pipe, lower_pipe, move1, move2
            )

            if result["survives"]:
                safe_sequences.append((move1, move2, result["gap_distance"]))
            else:
                unsafe_sequences.append((move1, move2, result["gap_distance"]))

        # Strategy 1: If we have safe sequences, choose the one closest to gap center
        if safe_sequences:
            # Sort by gap distance, then by number of flaps (prefer fewer flaps if equal)
            def sequence_priority(seq):
                move1, move2, gap_distance = seq
                flap_count = int(move1) + int(move2)
                return (
                    gap_distance,
                    flap_count,
                )  # Sort by distance first, then flap count

            best_sequence = min(safe_sequences, key=sequence_priority)
            return "flap" if best_sequence[0] else "no_flap"

        # Strategy 2: All sequences are unsafe, choose the least bad one (closest to gap center)
        else:
            best_sequence = min(unsafe_sequences, key=lambda x: x[2])
            return "flap" if best_sequence[0] else "no_flap"

    def _evaluate_two_move_sequence_survival(
        self, upper_pipe, lower_pipe, move1: bool, move2: bool
    ) -> dict:
        """Evaluate a two-move sequence focusing on survival and gap positioning

        Args:
            upper_pipe: Upper pipe to navigate
            lower_pipe: Lower pipe to navigate
            move1: First action (True=flap, False=no_flap)
            move2: Second action (True=flap, False=no_flap)

        Returns:
            dict: {
                'survives': bool,  # True if sequence doesn't cause game over
                'gap_distance': float,  # Distance to gap center after 2 moves
                'final_position': float  # Bird Y position after 2 moves
            }
        """
        # Initial bird state
        bird_y = float(self.game.bird.y)
        bird_velocity = float(self.game.bird.velocity_y)
        bird_has_flapped = self.game.bird.bird_has_flapped

        # Get bird physics constants
        max_velocity = self.game.bird.maximum_velocity_y
        min_velocity = self.game.bird.minimum_velocity_y
        gravity = self.game.bird.downward_acceleration_y
        flap_power = self.game.bird.flap_acceleration
        min_y = self.game.bird.min_y
        max_y = self.game.bird.max_y

        # === SIMULATE FIRST MOVE ===
        if move1:  # Flap
            bird_velocity = flap_power
            bird_has_flapped = True
        else:  # No flap - apply gravity ONLY if not has_flapped
            if bird_velocity < max_velocity and not bird_has_flapped:
                bird_velocity += gravity

        # Reset has_flapped flag
        if bird_has_flapped:
            bird_has_flapped = False

        # Apply velocity limits and update position
        bird_velocity = max(min(bird_velocity, max_velocity), min_velocity)
        bird_y = max(min(bird_y + bird_velocity, max_y), min_y)

        # Check survival after first move
        if bird_y >= max_y or bird_y <= min_y:
            return {
                "survives": False,
                "gap_distance": float("inf"),
                "final_position": bird_y,
            }

        # Check pipe collision after first move
        bird_rect = pygame.Rect(
            self.game.bird.x, bird_y, self.game.bird.w, self.game.bird.h
        )
        if bird_rect.colliderect(upper_pipe.rect) or bird_rect.colliderect(
            lower_pipe.rect
        ):
            return {
                "survives": False,
                "gap_distance": float("inf"),
                "final_position": bird_y,
            }

        # === SIMULATE SECOND MOVE ===
        if move2:  # Flap
            bird_velocity = flap_power
            bird_has_flapped = True
        else:  # No flap - apply gravity ONLY if not has_flapped
            if bird_velocity < max_velocity and not bird_has_flapped:
                bird_velocity += gravity

        # Reset has_flapped flag
        if bird_has_flapped:
            bird_has_flapped = False

        # Apply velocity limits and update position
        bird_velocity = max(min(bird_velocity, max_velocity), min_velocity)
        bird_y = max(min(bird_y + bird_velocity, max_y), min_y)

        # Check survival after second move
        if bird_y >= max_y or bird_y <= min_y:
            return {
                "survives": False,
                "gap_distance": float("inf"),
                "final_position": bird_y,
            }

        # Check pipe collision after second move
        bird_rect = pygame.Rect(
            self.game.bird.x, bird_y, self.game.bird.w, self.game.bird.h
        )
        if bird_rect.colliderect(upper_pipe.rect) or bird_rect.colliderect(
            lower_pipe.rect
        ):
            return {
                "survives": False,
                "gap_distance": float("inf"),
                "final_position": bird_y,
            }

        # === CALCULATE GAP DISTANCE ===
        gap_center_y = (upper_pipe.y + upper_pipe.h + lower_pipe.y) / 2
        gap_distance = abs(bird_y - gap_center_y)

        return {
            "survives": True,
            "gap_distance": gap_distance,
            "final_position": bird_y,
        }

    def _evaluate_two_move_sequence(
        self, upper_pipe, lower_pipe, move1: bool, move2: bool
    ) -> float:
        """Evaluate a specific two-move sequence

        Args:
            upper_pipe: Upper pipe to navigate
            lower_pipe: Lower pipe to navigate
            move1: First action (True=flap, False=no_flap)
            move2: Second action (True=flap, False=no_flap)

        Returns:
            float: Score for this sequence (higher is better)
        """
        # Initial bird state - use EXACT same values as the real bird
        bird_y = float(self.game.bird.y)
        bird_velocity = float(self.game.bird.velocity_y)
        bird_has_flapped = self.game.bird.bird_has_flapped

        # Get bird physics constants
        max_velocity = self.game.bird.maximum_velocity_y
        min_velocity = self.game.bird.minimum_velocity_y
        gravity = self.game.bird.downward_acceleration_y
        flap_power = self.game.bird.flap_acceleration
        min_y = self.game.bird.min_y
        max_y = self.game.bird.max_y

        # === SIMULATE FIRST MOVE ===
        if move1:  # Flap
            bird_velocity = flap_power
            bird_has_flapped = True
        else:  # No flap - apply gravity ONLY if not has_flapped (like real bird)
            if bird_velocity < max_velocity and not bird_has_flapped:
                bird_velocity += gravity

        # Reset has_flapped flag (like real bird does each frame)
        if bird_has_flapped:
            bird_has_flapped = False

        # Apply velocity limits
        bird_velocity = max(min(bird_velocity, max_velocity), min_velocity)

        # Update position (like real bird with clamp)
        bird_y = max(min(bird_y + bird_velocity, max_y), min_y)

        # Check if bird hit ground or ceiling (should be game over)
        if bird_y >= max_y or bird_y <= min_y:
            return -2000  # Hit boundaries - instant death

        # (Note: boundary penalties will be applied in scoring section)

        # Check collision with pipes after first move
        bird_rect = pygame.Rect(
            self.game.bird.x, bird_y, self.game.bird.w, self.game.bird.h
        )
        if bird_rect.colliderect(upper_pipe.rect) or bird_rect.colliderect(
            lower_pipe.rect
        ):
            return -1000  # Pipe collision after 1 move - very bad

        # === SIMULATE SECOND MOVE ===
        if move2:  # Flap
            bird_velocity = flap_power
            bird_has_flapped = True
        else:  # No flap - apply gravity ONLY if not has_flapped (like real bird)
            if bird_velocity < max_velocity and not bird_has_flapped:
                bird_velocity += gravity

        # Reset has_flapped flag (like real bird does each frame)
        if bird_has_flapped:
            bird_has_flapped = False

        # Apply velocity limits
        bird_velocity = max(min(bird_velocity, max_velocity), min_velocity)

        # Update position (like real bird with clamp)
        bird_y = max(min(bird_y + bird_velocity, max_y), min_y)

        # Check if bird hit ground or ceiling
        if bird_y >= max_y or bird_y <= min_y:
            return (
                -1500
            )  # Hit boundaries after 2 moves - very bad but not as bad as immediate

        # (Note: boundary penalties will be applied in final scoring section)

        # Check collision with pipes after second move
        bird_rect = pygame.Rect(
            self.game.bird.x, bird_y, self.game.bird.w, self.game.bird.h
        )
        if bird_rect.colliderect(upper_pipe.rect) or bird_rect.colliderect(
            lower_pipe.rect
        ):
            return -500  # Pipe collision after 2 moves - bad but manageable

        # === SCORING ===
        # Calculate distance to gap center for positioning
        gap_center_y = (upper_pipe.y + upper_pipe.h + lower_pipe.y) / 2
        gap_distance = abs(bird_y - gap_center_y)

        # Base score for surviving 2 moves without hitting boundaries or pipes
        score = 100

        # Smart gap positioning scoring
        # Penalty for being far from gap center, but less aggressive
        score -= gap_distance * 0.1

        # Bonus for good positioning relative to gap
        if gap_distance < 15:
            score += 15  # Big bonus for being very close
        elif gap_distance < 30:
            score += 8  # Good bonus for being close
        elif gap_distance < 60:
            score += 3  # Small bonus for reasonable positioning

        # Additional penalties for being too close to boundaries
        boundary_margin = 30
        if bird_y < min_y + boundary_margin:  # Too close to ceiling
            score -= (min_y + boundary_margin - bird_y) * 0.5  # Progressive penalty
        if bird_y > max_y - boundary_margin:  # Too close to ground
            score -= (bird_y - (max_y - boundary_margin)) * 0.5  # Progressive penalty

        # Penalty for excessive or ineffective flapping
        flap_count = int(move1) + int(move2)

        # Extra penalty for ineffective flaps (when velocity is already at flap_power)
        initial_velocity = float(self.game.bird.velocity_y)
        if move1 and initial_velocity == self.game.bird.flap_acceleration:
            score -= 10  # Big penalty for useless flap
        if (
            move2 and abs(bird_velocity - self.game.bird.flap_acceleration) < 0.1
        ):  # After first move
            score -= 10  # Big penalty for useless second flap

        if flap_count == 2:
            score -= 3  # Small penalty for double flap
        elif flap_count == 0:
            score -= 1  # Very small penalty for no flapping

        # Bonus for good velocity control (not too fast up or down)
        if abs(bird_velocity) < 5:
            score += 2  # Bonus for controlled velocity

        return score

    def _check_immediate_collision(self, upper_pipe, lower_pipe):
        """Check if immediate action is needed to avoid collision (using correct bird physics)

        Args:
            upper_pipe: The upper pipe to check against
            lower_pipe: The lower pipe to check against

        Returns:
            str: "flap" if immediate flap needed, "no_flap" if immediate no-flap needed,
                 None if no immediate action required
        """
        # Create lightweight bird state copies with correct physics
        bird_y = self.game.bird.y
        bird_velocity = self.game.bird.velocity_y
        bird_has_flapped = self.game.bird.bird_has_flapped

        # Get constants
        max_velocity = self.game.bird.maximum_velocity_y
        min_velocity = self.game.bird.minimum_velocity_y
        gravity = self.game.bird.downward_acceleration_y
        flap_power = self.game.bird.flap_acceleration
        min_y = self.game.bird.min_y
        max_y = self.game.bird.max_y

        # === NO FLAP SCENARIO ===
        no_flap_velocity = bird_velocity
        no_flap_has_flapped = bird_has_flapped

        # Apply gravity only if not has_flapped
        if no_flap_velocity < max_velocity and not no_flap_has_flapped:
            no_flap_velocity += gravity

        # Reset has_flapped flag
        if no_flap_has_flapped:
            no_flap_has_flapped = False

        # Apply velocity limits and update position
        no_flap_velocity = max(min(no_flap_velocity, max_velocity), min_velocity)
        no_flap_y = max(min(bird_y + no_flap_velocity, max_y), min_y)

        # === FLAP SCENARIO ===
        flap_velocity = flap_power  # Flap sets velocity directly
        flap_has_flapped = True

        # Reset has_flapped flag
        if flap_has_flapped:
            flap_has_flapped = False

        # Apply velocity limits and update position
        flap_velocity = max(min(flap_velocity, max_velocity), min_velocity)
        flap_y = max(min(bird_y + flap_velocity, max_y), min_y)

        # Check collisions using rectangle collision
        bird_rect = self.game.bird.rect

        # Create temporary rectangles for collision testing
        no_flap_rect = pygame.Rect(
            bird_rect.x, no_flap_y, bird_rect.width, bird_rect.height
        )
        flap_rect = pygame.Rect(bird_rect.x, flap_y, bird_rect.width, bird_rect.height)

        upper_rect = upper_pipe.rect
        lower_rect = lower_pipe.rect

        # Check collisions
        no_flap_collision = no_flap_rect.colliderect(
            upper_rect
        ) or no_flap_rect.colliderect(lower_rect)
        flap_collision = flap_rect.colliderect(upper_rect) or flap_rect.colliderect(
            lower_rect
        )

        # Immediate action logic: if one action leads to collision and the other doesn't, choose the safe one
        if no_flap_collision and not flap_collision:
            return "flap"
        elif flap_collision and not no_flap_collision:
            return "no_flap"

        # If both are safe or both lead to collision, let the two-move simulation decide
        return None
