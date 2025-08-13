#!/usr/bin/env python3
"""Script pour reproduire une partie spécifique avec une seed donnée."""

import sys
import time

try:
    from multi_bird_genetic import MultiGeneticGame
    from src.game import Game

    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False


def replay_auto_close_game(
    seed: int,
    verbose: bool = True,
    bot_type: str = "single",
    neural_weights: list = None,
) -> None:
    """Reproduit une partie avec fermeture automatique avec une seed spécifique."""
    if bot_type == "single":
        bot_name = "Bot Simple"
    elif bot_type == "two_pipes":
        bot_name = "Bot Deux Tuyaux"
    elif bot_type == "neural":
        bot_name = f"Bot Neural {neural_weights}"
    else:
        bot_name = f"Bot {bot_type}"
    if verbose:
        print(f"🔄 Reproduction de la partie avec la seed: {seed} ({bot_name})")
        print("-" * 50)

    try:
        start_time = time.time()

        # Pour les bots neural, utiliser MultiGeneticGame pour la cohérence
        if bot_type == "neural" and neural_weights:
            import os

            if "SDL_VIDEODRIVER" not in os.environ:
                os.environ["SDL_VIDEODRIVER"] = "dummy"

            # Créer un jeu avec un seul oiseau neural
            population_weights = [neural_weights]
            game = MultiGeneticGame(population_weights, seed=seed)

            if verbose:
                print(f"Partie initialisée avec la seed {seed}")

            results = game.run_generation()
            duration = time.time() - start_time

            # Extraire les résultats du seul oiseau
            weights, fitness, frames = results[0]

            if verbose:
                print("\n🎯 Résultats de la reproduction:")
                print(f"  Seed utilisée: {seed}")
                print(f"  Score final: {fitness}")
                print(f"  Tuyaux passés: {fitness}")
                print(f"  Frames survécues: {frames}")
                print(f"  Durée: {duration:.3f} secondes")

            return fitness, frames
        else:
            # Utiliser la classe Game en mode auto-close pour les autres bots
            class AutoCloseGame(Game):
                def _handle_game_over(self):
                    # Auto-close after game over
                    time.sleep(0.1)
                    return

            # Créer et lancer le jeu avec auto-close
            import os

            if "SDL_VIDEODRIVER" not in os.environ:
                os.environ[
                    "SDL_VIDEODRIVER"
                ] = "dummy"  # Use dummy driver if no display

            game = AutoCloseGame(bot_mode=True, seed=seed, bot_type=bot_type)

            # Set neural weights if using neural bot
            if bot_type == "neural" and neural_weights:
                game.neural_weights = neural_weights

            if verbose:
                print(f"Partie initialisée avec la seed {game.seed}")

            game.play_game()

            duration = time.time() - start_time

            if verbose:
                print("\n🎯 Résultats de la reproduction:")
                print(f"  Seed utilisée: {game.seed}")
                print(f"  Score final: {game.score.score}")
                print(f"  Tuyaux passés: {game.score.score}")
                print(f"  Durée: {duration:.3f} secondes")

            return game.score.score, None

    except Exception as e:
        print(f"❌ Erreur pendant la reproduction: {e}")
        return


def replay_visual_game(
    seed: int, bot_type: str = "single", neural_weights: list = None
) -> None:
    """Reproduit une partie avec affichage visuel en utilisant une seed spécifique."""
    if bot_type == "single":
        bot_name = "Bot Simple"
    elif bot_type == "two_pipes":
        bot_name = "Bot Deux Tuyaux"
    elif bot_type == "neural":
        bot_name = f"Bot Neural {neural_weights}"
    else:
        bot_name = f"Bot {bot_type}"

    if not PYGAME_AVAILABLE:
        print("❌ Pygame non disponible. Mode visuel non supporté.")
        print(
            "💡 Utilisez le mode auto-close: python replay_seed.py -s {} (sans -v)".format(
                seed
            )
        )
        return

    print(f"🎮 Lancement de la partie visuelle avec la seed: {seed} ({bot_name})")
    print("Fermer la fenêtre ou appuyer sur ESC pour quitter")

    try:
        # S'assurer que SDL peut utiliser l'affichage si disponible
        import os

        # Enlever toute configuration dummy si elle existe
        if "SDL_VIDEODRIVER" in os.environ and os.environ["SDL_VIDEODRIVER"] == "dummy":
            del os.environ["SDL_VIDEODRIVER"]

        # Pour les bots neural, utiliser MultiGeneticGame avec affichage visuel
        if bot_type == "neural" and neural_weights:
            # Créer un jeu avec un seul oiseau neural en mode visuel
            population_weights = [neural_weights]
            game = MultiGeneticGame(population_weights, seed=seed)

            print(f"Partie initialisée avec la seed {seed}")

            results = game.run_generation()

            # Extraire les résultats du seul oiseau
            weights, fitness, frames = results[0]

            print("\n🎯 Partie terminée:")
            print(f"  Seed utilisée: {seed}")
            print(f"  Score final: {fitness}")
            print(f"  Frames survécues: {frames}")
        else:
            # Créer et lancer exactement comme main_bot.py pour les autres bots
            game = Game(bot_mode=True, seed=seed, bot_type=bot_type)

            # Set neural weights if using neural bot
            if bot_type == "neural" and neural_weights:
                game.neural_weights = neural_weights

            print(f"Partie initialisée avec la seed {game.seed}")

            # Jouer la partie avec fenêtre graphique pygame
            game.play_game()

            print("\n🎯 Partie terminée:")
            print(f"  Seed utilisée: {game.seed}")
            print(f"  Score final: {game.score.score}")

    except Exception as e:
        print(f"❌ Erreur pendant la partie visuelle: {e}")

        # En cas d'erreur, proposer alternatives
        error_msg = str(e).lower()
        if "display" in error_msg or "video" in error_msg or "sdl" in error_msg:
            print("💡 Problème d'affichage détecté. Solutions:")
            print("   1. Lancez dans un terminal avec interface graphique")
            print("   2. Ou utilisez le mode auto-close:")
            print(f"      python replay_seed.py -s {seed}")
        else:
            print("💡 Essayez le mode auto-close:")
            print(f"   python replay_seed.py -s {seed}")

        import traceback

        traceback.print_exc()


def find_game_in_csv(csv_file: str, game_id: int = None, seed: int = None) -> None:
    """Cherche une partie dans un fichier CSV et affiche les informations."""
    import csv

    try:
        with open(csv_file, "r") as f:
            reader = csv.DictReader(f)

            if game_id is not None:
                # Chercher par game_id
                for row in reader:
                    if int(row["game_id"]) == game_id:
                        print(f"🔍 Partie trouvée (Game ID {game_id}):")
                        print(f"  Seed: {row['seed']}")
                        print(f"  Score: {row['score']}")
                        print(f"  Durée: {row['duration_seconds']}s")
                        print(f"  Statut: {row['status']}")
                        return row["seed"]

                print(f"❌ Aucune partie trouvée avec l'ID {game_id}")

            elif seed is not None:
                # Chercher par seed
                for row in reader:
                    if int(row["seed"]) == seed:
                        print(f"🔍 Partie trouvée (Seed {seed}):")
                        print(f"  Game ID: {row['game_id']}")
                        print(f"  Score: {row['score']}")
                        print(f"  Durée: {row['duration_seconds']}s")
                        print(f"  Statut: {row['status']}")
                        return

                print(f"❌ Aucune partie trouvée avec la seed {seed}")

    except FileNotFoundError:
        print(f"❌ Fichier CSV non trouvé: {csv_file}")
    except Exception as e:
        print(f"❌ Erreur en lisant le CSV: {e}")


def main():
    """Point d'entrée principal."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Reproduire une partie Flappy Bird avec une seed",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python replay_seed.py -s 12345                      # Reproduire seed avec bot simple
  python replay_seed.py -s 12345 -v                   # Mode visuel avec bot simple
  python replay_seed.py -s 12345 -b two_pipes         # Bot avancé, mode auto-close
  python replay_seed.py -s 12345 -v -b two_pipes      # Bot avancé, mode visuel
  python replay_seed.py -s 12345 -b neural -w 0.884 1.957 -1.020 1.782 -0.515        # Bot neural
  python replay_seed.py -s 12345 -v -b neural -w 0.884 1.957 -1.020 1.782 -0.515     # Bot neural visuel
  python replay_seed.py -f results.csv -g 42 -v       # Game ID 42 en visuel
        """,
    )
    parser.add_argument("-s", "--seed", type=int, help="Seed à reproduire")
    parser.add_argument(
        "-g", "--game-id", type=int, help="ID de partie à chercher dans un CSV"
    )
    parser.add_argument("-f", "--csv-file", help="Fichier CSV à analyser")
    parser.add_argument(
        "-v", "--visual", action="store_true", help="Mode visuel (avec affichage)"
    )
    parser.add_argument("-q", "--quiet", action="store_true", help="Mode silencieux")
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

    args = parser.parse_args()

    # Si un fichier CSV est fourni, chercher la seed
    if args.csv_file:
        if args.game_id:
            seed = find_game_in_csv(args.csv_file, game_id=args.game_id)
            if seed:
                args.seed = int(seed)
        elif args.seed:
            find_game_in_csv(args.csv_file, seed=args.seed)

    # Vérifier qu'une seed est fournie
    if not args.seed:
        parser.print_help()
        sys.exit(1)

    # Validation pour bot neural
    if args.bot_type == "neural" and not args.neural_weights:
        parser.error("--neural-weights est requis quand --bot-type=neural")

    if args.neural_weights and len(args.neural_weights) != 5:
        parser.error("--neural-weights doit contenir exactement 5 valeurs")

    # Affichage du bot sélectionné
    bot_display = {
        "single": "🧠 Bot Simple (1 tuyau)",
        "two_pipes": "🔮 Bot Deux Tuyaux (2 tuyaux)",
        "neural": f"🤖 Bot Neural (poids: {args.neural_weights})",
    }
    if not args.quiet:
        print(f"Bot sélectionné: {bot_display[args.bot_type]}")

    try:
        if args.visual:
            replay_visual_game(
                args.seed, bot_type=args.bot_type, neural_weights=args.neural_weights
            )
        else:
            replay_auto_close_game(
                args.seed,
                verbose=not args.quiet,
                bot_type=args.bot_type,
                neural_weights=args.neural_weights,
            )

    except KeyboardInterrupt:
        print("\n⚠️  Reproduction interrompue par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
