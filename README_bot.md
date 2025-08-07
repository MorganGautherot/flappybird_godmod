# AI Bot Mode for Flappy Bird

This project now includes an AI bot that can automatically play Flappy Bird without any human input.

## Running the Bot

### Quick Start
```bash
# Run a single bot game
python main_bot.py

# Run 5 bot games and see statistics
python main_bot.py 5
```

### How it Works

The AI bot replaces human keyboard input and makes decisions based on:
1. **Lookahead Simulation**: The bot creates copies of the game state to predict outcomes
2. **Collision Avoidance**: Tests both "flap" and "no-flap" actions to avoid pipes
3. **Gap Centering**: When no collision is imminent, tries to stay centered in pipe gaps

### Features

- **Fully Autonomous**: No human input required (except ESC to quit)
- **Visual Indicator**: "AI BOT" label appears in the top-right corner
- **Performance Statistics**: Tracks scores, high scores, and averages across multiple games
- **Game Statistics**: Shows performance metrics after each session

### Bot Decision Logic

The bot analyzes the next upcoming pipe and:
1. Simulates bird physics (position and velocity) for both flap and no-flap scenarios
2. Checks for collisions using rectangle collision detection (fast and efficient)
3. Chooses the action that avoids collision
4. If both actions are safe, chooses the one that keeps the bird centered in the gap
5. If both actions lead to collision, chooses based on proximity to gap center

**Performance Optimized**: The bot uses lightweight physics simulation instead of deep copying pygame objects, making it fast and avoiding pickle errors.

### Controls

- **ESC**: Quit the game at any time (works in both human and bot modes)
- The bot handles all flapping decisions automatically

### Example Usage

```python
# Create a game in bot mode
from src.game import Game

# Single bot game
bot_game = Game(bot_mode=True)
bot_game.play_game()

# Human game (default)
human_game = Game(bot_mode=False)  # or just Game()
human_game.play_game()
```

## Implementation Details

- Bot mode is controlled by the `bot_mode` parameter in the Game constructor
- The Bot class uses deep copying for safe state simulation
- Visual feedback shows when bot mode is active
- All original human controls are preserved when bot_mode=False
