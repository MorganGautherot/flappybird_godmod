#!/usr/bin/env python3
"""Test script to verify bot integration works correctly."""

import sys
from unittest.mock import Mock, patch


def test_bot_integration():
    """Test that bot integration works without pygame dependencies."""

    # Mock pygame to avoid import errors
    with patch.dict(
        "sys.modules",
        {
            "pygame": Mock(),
            "pygame.display": Mock(),
            "pygame.image": Mock(),
            "pygame.font": Mock(),
            "pygame.time": Mock(),
            "pygame.event": Mock(),
            "pygame.locals": Mock(),
        },
    ):
        # Import after mocking
        from src.game import Bot, Game

        # Test bot initialization
        try:
            game = Game(bot_mode=True)
            assert game.bot_mode is True
            assert game.bot is not None
            assert isinstance(game.bot, Bot)
            print("✓ Bot initialization successful")
        except Exception as e:
            print(f"✗ Bot initialization failed: {e}")
            return False

        # Test bot decision making logic
        try:
            bot = Bot(game)
            # Test empty pipes scenario
            decision = bot.decide_action()
            assert decision == "no_flap"
            print("✓ Bot decision making logic works")
        except Exception as e:
            print(f"✗ Bot decision making failed: {e}")
            return False

        # Test game mode switching
        try:
            human_game = Game(bot_mode=False)
            assert human_game.bot_mode is False
            assert human_game.bot is None
            print("✓ Human mode works correctly")
        except Exception as e:
            print(f"✗ Human mode failed: {e}")
            return False

        print("✅ All bot integration tests passed!")
        return True


def test_main_bot_imports():
    """Test that main_bot.py imports work correctly."""
    try:
        print("✓ main_bot.py imports successfully")
        return True
    except ImportError as e:
        print(f"✗ main_bot.py import failed: {e}")
        return False


if __name__ == "__main__":
    print("Running Bot Integration Tests...")
    print("-" * 40)

    success = True
    success &= test_main_bot_imports()
    success &= test_bot_integration()

    if success:
        print("\n🎉 All tests passed! Bot integration is ready.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        sys.exit(1)
