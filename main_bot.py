#!/usr/bin/env python3
"""Entry point for running Flappy Bird with AI Bot control."""

import argparse
import sys
import time
from typing import Optional

from src.game import Game


def main(iterations: Optional[int] = None, bot_type: str = "single") -> None:
    """Run the game in bot mode

    Args:
        iterations: Number of games to run. If None, runs indefinitely.
        bot_type: Type of bot to use ("single" or "two_pipes")
    """
    bot_name = "Bot Simple" if bot_type == "single" else "Bot Deux Tuyaux"
    print(f"🤖 Démarrage de Flappy Bird avec {bot_name}...")
    print("Appuyez sur ESC pour quitter à tout moment.")

    games_played = 0
    total_score = 0
    high_score = 0

    try:
        while iterations is None or games_played < iterations:
            games_played += 1
            print(f"\nPartie #{games_played}")

            # Create and run game in bot mode with specified bot type
            game = Game(bot_mode=True, bot_type=bot_type)
            game.play_game()

            # Track statistics
            final_score = game.score.score
            total_score += final_score
            high_score = max(high_score, final_score)

            print(f"Game Over! Score: {final_score}")
            print(f"Meilleur Score: {high_score}")
            if games_played > 1:
                avg_score = total_score / games_played
                print(f"Score Moyen: {avg_score:.1f}")

            # Brief pause between games
            if iterations is None or games_played < iterations:
                print("Prochaine partie dans 2 secondes...")
                time.sleep(2)

    except KeyboardInterrupt:
        print("\n⚠️ Mode bot interrompu par l'utilisateur.")
    except Exception as e:
        print(f"❌ Erreur pendant l'exécution du bot: {e}")
        sys.exit(1)

    print(f"\n🏁 Session {bot_name} Terminée:")
    print(f"Parties Jouées: {games_played}")
    print(f"Meilleur Score: {high_score}")
    if games_played > 1:
        print(f"Score Moyen: {total_score / games_played:.1f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Lancer Flappy Bird avec contrôle IA bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python main_bot.py                          # Bot simple, parties infinies
  python main_bot.py -n 5                     # Bot simple, 5 parties
  python main_bot.py -b two_pipes              # Bot deux tuyaux, parties infinies
  python main_bot.py -n 10 -b two_pipes       # Bot deux tuyaux, 10 parties
        """,
    )

    parser.add_argument(
        "-n", "--num-games", type=int, help="Nombre de parties à jouer (défaut: infini)"
    )

    parser.add_argument(
        "-b",
        "--bot-type",
        choices=["single", "two_pipes"],
        default="single",
        help="Type de bot à utiliser (défaut: single)",
    )

    # Support pour l'ancien format (premier argument = nombre de parties)
    # Pour rétrocompatibilité
    args, unknown = parser.parse_known_args()

    # Si pas d'arguments nommés mais un argument positionnel, utiliser l'ancien format
    if not any([args.num_games, args.bot_type != "single"]) and len(sys.argv) == 2:
        try:
            iterations = int(sys.argv[1])
            print(
                "📝 Note: Utilisez 'python main_bot.py -n 5' pour la nouvelle syntaxe"
            )
            main(iterations=iterations, bot_type="single")
        except ValueError:
            parser.print_help()
            print(f"\n❌ Erreur: '{sys.argv[1]}' n'est pas un nombre valide")
            sys.exit(1)
    else:
        # Nouveau format avec argparse
        if unknown:
            print(f"⚠️ Arguments non reconnus ignorés: {' '.join(unknown)}")

        # Affichage du choix du bot
        bot_display = {
            "single": "🧠 Bot Simple (1 tuyau)",
            "two_pipes": "🔮 Bot Deux Tuyaux (2 tuyaux)",
        }
        print(f"Bot sélectionné: {bot_display[args.bot_type]}")

        main(iterations=args.num_games, bot_type=args.bot_type)
