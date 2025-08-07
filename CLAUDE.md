# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Game
```bash
# Human player mode
python main.py

# AI Bot mode (single game)
python main_bot.py

# AI Bot mode (multiple games)
python main_bot.py 10  # Runs 10 games
```

### Dependency Management
```bash
# Install dependencies
poetry install

# Add new dependency
poetry add <package-name>

# Update dependencies
poetry update
```

### Testing
```bash
# Run tests (using pytest if available)
python -m pytest test/

# Run specific test file
python -m pytest test/test_bird.py
```

### Code Quality
```bash
# Run pre-commit hooks
pre-commit run --all-files
```

## Architecture Overview

This is a Flappy Bird game implementation with "god mode" modifications, built using Pygame. The game features both human gameplay and bot automation capabilities.

### Core Game Loop Architecture
The game follows a traditional game loop pattern centered around the `Game` class in `src/game.py`:
1. **Initialization**: Sets up pygame, creates game objects (bird, background, pipes, score)
2. **Main Loop**: Handles events, updates game state, checks collisions, renders frame
3. **Game Over**: Enters waiting state until quit

### Key Components

**Game Class (`src/game.py`)**: Central game controller that orchestrates all game elements. Manages pipe generation/removal, collision detection, scoring, and the main game loop.

**Bird Class (`src/bird.py`)**: Represents the player character with physics simulation including gravity, flapping mechanics, rotation, and hit mask for pixel-perfect collision detection.

**Pipe Class (`src/windows.py`)**: Manages pipe obstacles that move horizontally across the screen. Pipes are generated in pairs (upper/lower) with random gap positioning.

**Bot Class (`src/game.py`)**: AI system that uses lookahead simulation by creating deep copies of game objects to predict collision outcomes and determine whether to flap or not. The bot can be enabled by creating a Game instance with `bot_mode=True` or by running `main_bot.py`.

### Physics and Collision System
The game uses pixel-perfect collision detection via hit masks rather than simple rectangle collision. The `utils.py` module provides collision utilities that check alpha channel transparency for precise collision boundaries.

### Configuration
All game constants (screen dimensions, physics parameters, asset paths) are centralized in `src/config.py` for easy tuning.

### Asset Management
Game sprites are stored in `assets/sprites/` and loaded on-demand. Score digits (0-9.png) are pre-loaded for performance during score rendering.

## Code Organization Patterns

- Physics calculations use clamping utilities to constrain values within bounds
- Game objects follow a consistent pattern: properties for center/rect, update methods (`next_status`) that optionally draw
- The bot uses deep copying for safe state simulation without affecting the actual game state
- Score system renders individual digit sprites rather than text for consistent visual styling
- All classes include proper error handling for asset loading with informative error messages
- Type hints are used throughout for better code clarity and IDE support
- Game loop is structured with private helper methods for better separation of concerns
