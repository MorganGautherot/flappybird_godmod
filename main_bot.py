#!/usr/bin/env python3
"""Entry point for running Flappy Bird with AI Bot control."""

import argparse
import sys
import time
from typing import Optional

from src.game import Game


def main(
    iterations: Optional[int] = None,
    bot_type: str = "single",
    neural_weights: Optional[list] = None,
) -> None:
    """Run the game in bot mode

    Args:
        iterations: Number of games to run. If None, runs indefinitely.
        bot_type: Type of bot to use ("single", "two_pipes", or "neural")
        neural_weights: List of 5 weights for neural bot [w1, w2, w3, w4, bias]
    """
    if bot_type == "single":
        bot_name = "Bot Simple"
    elif bot_type == "two_pipes":
        bot_name = "Bot Deux Tuyaux"
    elif bot_type == "neural":
        bot_name = f"Bot Neural {neural_weights}"
    else:
        bot_name = f"Bot {bot_type}"

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

            # Set neural weights if using neural bot
            if bot_type == "neural" and neural_weights:
                game.neural_weights = neural_weights

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
  python main_bot.py -b neural -w 0.01 0.97 -1.95 0.72 -0.20  # Bot neural avec poids
  python main_bot.py -n 5 -b neural -w 0.01 0.97 -1.95 0.72 -0.20  # Bot neural, 5 parties
        """,
    )

    parser.add_argument(
        "-n", "--num-games", type=int, help="Nombre de parties à jouer (défaut: infini)"
    )

    parser.add_argument(
        "-b",
        "--bot-type",
        choices=["single", "two_pipes", "neural"],
        default="single",
        help="Type de bot à utiliser (défaut: single)",
    )

    parser.add_argument(
        "-w",
        "--neural-weights",
        nargs=5,
        type=float,
        help="Poids pour le bot neural [w1, w2, w3, w4, bias] (requis si bot-type=neural)",
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

        # Validation pour bot neural
        if args.bot_type == "neural" and not args.neural_weights:
            parser.error("--neural-weights est requis quand --bot-type=neural")

        if args.neural_weights and len(args.neural_weights) != 5:
            parser.error("--neural-weights doit contenir exactement 5 valeurs")

        # Affichage du choix du bot
        bot_display = {
            "single": "🧠 Bot Simple (1 tuyau)",
            "two_pipes": "🔮 Bot Deux Tuyaux (2 tuyaux)",
            "neural": f"🤖 Bot Neural (poids: {args.neural_weights})",
        }
        print(f"Bot sélectionné: {bot_display[args.bot_type]}")

        main(
            iterations=args.num_games,
            bot_type=args.bot_type,
            neural_weights=args.neural_weights,
        )
