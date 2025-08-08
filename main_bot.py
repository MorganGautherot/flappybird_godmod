#!/usr/bin/env python3
"""Entry point for running Flappy Bird with AI Bot control."""

import sys
from typing import Optional

from src.game import Game


def main(iterations: Optional[int] = None) -> None:
    """Run the game in bot mode

    Args:
        iterations: Number of games to run. If None, runs indefinitely.
    """
    print("Starting Flappy Bird in AI Bot Mode...")
    print("Press ESC to quit at any time.")

    games_played = 0
    total_score = 0
    high_score = 0

    try:
        while iterations is None or games_played < iterations:
            games_played += 1
            print(f"\nGame #{games_played}")

            # Create and run game in bot mode
            game = Game(bot_mode=True)
            game.play_game()

            # Track statistics
            final_score = game.score.score
            total_score += final_score
            high_score = max(high_score, final_score)

            print(f"Game Over! Score: {final_score}")
            print(f"High Score: {high_score}")
            if games_played > 1:
                avg_score = total_score / games_played
                print(f"Average Score: {avg_score:.1f}")

            # Brief pause between games
            if iterations is None or games_played < iterations:
                print("Starting next game in 2 seconds...")
                import time

                time.sleep(2)

    except KeyboardInterrupt:
        print("\nBot mode interrupted by user.")
    except Exception as e:
        print(f"Error running bot: {e}")
        sys.exit(1)

    print("\nBot Session Complete:")
    print(f"Games Played: {games_played}")
    print(f"High Score: {high_score}")
    if games_played > 1:
        print(f"Average Score: {total_score / games_played:.1f}")


if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) > 1:
        try:
            iterations = int(sys.argv[1])
            main(iterations)
        except ValueError:
            print("Usage: python main_bot.py [number_of_games]")
            sys.exit(1)
    else:
        main()
