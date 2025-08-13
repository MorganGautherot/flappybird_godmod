#!/usr/bin/env python3
"""Sequential visual batch testing - runs games with pygame window one after another."""

import csv
import sys
import time
from datetime import datetime
from typing import Dict, List

from multi_bird_genetic import MultiGeneticGame
from src.game import Game


class AutoCloseGame(Game):
    """Game class that automatically closes after game over in bot mode."""

    def _handle_game_over(self) -> None:
        """Handle the game over state - auto-close in bot mode."""
        if self.bot_mode:
            # In bot mode, just close automatically after a brief pause
            time.sleep(0.1)  # Brief pause to see the final state
            return
        else:
            # In human mode, keep original behavior
            super()._handle_game_over()


def run_single_visual_game(
    game_id: int,
    seed: int = None,
    verbose: bool = True,
    bot_type: str = "single",
    neural_weights: list = None,
) -> Dict:
    """Run a single visual game and return results."""
    try:
        if verbose:
            print(f"🎮 Partie {game_id} (seed: {seed})...", end=" ", flush=True)

        start_time = time.time()

        # Pour les bots neural, utiliser MultiGeneticGame pour la cohérence
        if bot_type == "neural" and neural_weights:
            # Créer un jeu avec un seul oiseau neural en mode visuel
            population_weights = [neural_weights]
            game = MultiGeneticGame(population_weights, seed=seed)

            results = game.run_generation()
            duration = time.time() - start_time

            # Extraire les résultats du seul oiseau
            weights, fitness, frames = results[0]

            result = {
                "game_id": game_id,
                "seed": seed,
                "score": fitness,
                "duration_seconds": round(duration, 3),
                "pipes_passed": fitness,
                "status": "completed",
                "timestamp": datetime.now().isoformat(),
            }

            if verbose:
                print(f"Score: {result['score']} (durée: {duration:.2f}s)")

            return result
        else:
            # Créer et lancer un jeu auto-fermé pour les autres bots
            game = AutoCloseGame(bot_mode=True, seed=seed, bot_type=bot_type)

            # Set neural weights if using neural bot
            if bot_type == "neural" and neural_weights:
                game.neural_weights = neural_weights

            game.play_game()

            duration = time.time() - start_time

            result = {
                "game_id": game_id,
                "seed": game.seed,
                "score": game.score.score,
                "duration_seconds": round(duration, 3),
                "pipes_passed": game.score.score,
                "status": "completed",
                "timestamp": datetime.now().isoformat(),
            }

            if verbose:
                print(f"Score: {result['score']} (durée: {duration:.2f}s)")

            return result

    except Exception as e:
        error_result = {
            "game_id": game_id,
            "seed": seed if seed is not None else 0,
            "score": 0,
            "duration_seconds": 0,
            "pipes_passed": 0,
            "status": f"error: {str(e)}",
            "timestamp": datetime.now().isoformat(),
        }

        if verbose:
            print(f"ÉCHEC: {str(e)}")

        return error_result


def run_sequential_visual_batch(
    num_games: int,
    output_file: str = None,
    verbose: bool = True,
    bot_type: str = "single",
    neural_weights: list = None,
) -> List[Dict]:
    """Run games visually one after another and save results to CSV."""

    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if bot_type == "single":
            bot_suffix = "single"
        elif bot_type == "two_pipes":
            bot_suffix = "two_pipes"
        elif bot_type == "neural":
            bot_suffix = "neural"
        else:
            bot_suffix = bot_type
        output_file = f"sequential_visual_{bot_suffix}_results_{timestamp}.csv"

    if bot_type == "single":
        bot_name = "Bot Simple"
    elif bot_type == "two_pipes":
        bot_name = "Bot Deux Tuyaux"
    elif bot_type == "neural":
        bot_name = f"Bot Neural {neural_weights}"
    else:
        bot_name = f"Bot {bot_type}"
    print(f"🎮 Lancement séquentiel de {num_games} parties VISUELLES avec {bot_name}")
    print(
        "Chaque partie s'ouvre dans une fenêtre pygame et se ferme automatiquement au game over"
    )
    print(f"Résultats seront sauvés dans: {output_file}")
    print("-" * 60)

    results = []
    start_time = time.time()

    # Generate unique seeds for each game
    base_seed = int(time.time() * 1000) % 2**31

    try:
        # Run games one by one in a simple loop
        for game_id in range(1, num_games + 1):
            seed = base_seed + game_id
            result = run_single_visual_game(
                game_id,
                seed=seed,
                verbose=verbose,
                bot_type=bot_type,
                neural_weights=neural_weights,
            )
            results.append(result)

            # Progress update every 5 games (or every game if <= 10 total)
            if verbose and (num_games <= 10 or game_id % 5 == 0):
                progress = (game_id / num_games) * 100
                elapsed = time.time() - start_time
                avg_time = elapsed / game_id
                estimated_total = avg_time * num_games
                remaining = estimated_total - elapsed

                print(
                    f"Progression: {game_id}/{num_games} ({progress:.1f}%) - "
                    f"Temps moyen: {avg_time:.2f}s/partie - "
                    f"Temps restant estimé: {remaining/60:.1f}min"
                )

    except KeyboardInterrupt:
        print("\n🛑 Batch testing visuel interrompu par l'utilisateur")

    total_time = time.time() - start_time

    # Save to CSV
    fieldnames = [
        "game_id",
        "seed",
        "score",
        "duration_seconds",
        "pipes_passed",
        "status",
        "timestamp",
    ]

    with open(output_file, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # Print statistics
    print_visual_stats(results, total_time, output_file)

    return results


def print_visual_stats(results: List[Dict], total_time: float, output_file: str):
    """Print comprehensive statistics for visual batch run."""
    successful_games = [r for r in results if r["status"] == "completed"]
    failed_games = [r for r in results if r["status"] != "completed"]
    scores = [r["score"] for r in successful_games]
    durations = [r["duration_seconds"] for r in successful_games]

    print(f"\n{'='*60}")
    print("RÉSULTATS DU BATCH VISUEL SÉQUENTIEL")
    print(f"{'='*60}")

    # Basic stats
    print(f"Total parties lancées: {len(results)}")
    print(f"Parties réussies: {len(successful_games)}")
    print(f"Parties échouées: {len(failed_games)}")
    print(f"Taux de réussite: {len(successful_games)/len(results)*100:.1f}%")
    print(
        f"Temps total d'exécution: {total_time/60:.1f} minutes ({total_time:.1f} secondes)"
    )
    print(f"Temps moyen par partie: {total_time/len(results):.2f} secondes")

    if failed_games:
        print("\nParties échouées:")
        for failed in failed_games[:5]:  # Show first 5 failures
            print(f"  Partie {failed['game_id']}: {failed['status']}")
        if len(failed_games) > 5:
            print(f"  ... et {len(failed_games)-5} autres")

    if scores:
        print("\nStatistiques des Scores:")
        print(f"  Score minimum: {min(scores)}")
        print(f"  Score maximum: {max(scores)}")
        print(f"  Score moyen: {sum(scores)/len(scores):.1f}")
        print(f"  Score médian: {sorted(scores)[len(scores)//2]}")

        # Top 5 scores with their seeds
        score_seed_pairs = [
            (r["score"], r["seed"], r["game_id"]) for r in successful_games
        ]
        top_scores = sorted(score_seed_pairs, reverse=True)[:5]

        print("\n🏆 Top 5 des Meilleurs Scores:")
        for i, (score, seed, game_id) in enumerate(top_scores, 1):
            print(f"  {i}. Score {score} - Seed {seed} (Partie #{game_id})")

        # Score distribution
        ranges = [(0, 0), (1, 5), (6, 10), (11, 20), (21, 50), (51, 999)]
        print("\nDistribution des Scores:")
        for min_s, max_s in ranges:
            if max_s == 999:
                count = len([s for s in scores if s >= min_s])
                percentage = count / len(scores) * 100
                print(f"  {min_s}+ tuyaux: {count} parties ({percentage:.1f}%)")
            else:
                count = len([s for s in scores if min_s <= s <= max_s])
                percentage = count / len(scores) * 100
                print(f"  {min_s}-{max_s} tuyaux: {count} parties ({percentage:.1f}%)")

    if durations:
        print("\nStatistiques de Durée:")
        print(f"  Partie la plus rapide: {min(durations):.2f} secondes")
        print(f"  Partie la plus longue: {max(durations):.2f} secondes")
        print(f"  Durée moyenne: {sum(durations)/len(durations):.2f} secondes")

    print(f"\nRésultats sauvegardés dans: {output_file}")

    # Performance summary
    if total_time > 0:
        games_per_minute = len(results) / (total_time / 60)
        print(f"Performance: {games_per_minute:.1f} parties par minute")

    # Useful reproduction commands
    if scores and len(top_scores) > 0:
        best_score, best_seed, best_game = top_scores[0]
        print(f"\n💡 Pour reproduire le meilleur score ({best_score}):")
        print(f"  python replay_seed.py -s {best_seed} -v")


def main():
    """Main entry point for sequential visual batch testing."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Sequential Visual Flappy Bird batch testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python sequential_visual.py 10                    # 10 parties avec bot simple
  python sequential_visual.py 20 -b two_pipes       # 20 parties avec bot avancé
  python sequential_visual.py 5 -b neural -w 0.884 1.957 -1.020 1.782 -0.515    # 5 parties avec bot neural
  python sequential_visual.py 5 -o results.csv      # Sauver dans fichier spécifique
        """,
    )
    parser.add_argument("num_games", type=int, help="Number of games to run")
    parser.add_argument("-o", "--output", help="Output CSV filename")
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Reduce output verbosity"
    )
    parser.add_argument(
        "-b",
        "--bot-type",
        choices=["single", "two_pipes", "neural"],
        default="single",
        help="Type of bot to use (default: single)",
    )
    parser.add_argument(
        "-w",
        "--neural-weights",
        nargs=5,
        type=float,
        help="Poids pour le bot neural [w1, w2, w3, w4, bias] (requis si bot-type=neural)",
    )

    args = parser.parse_args()

    if args.num_games <= 0:
        print("Erreur: Le nombre de parties doit être positif")
        sys.exit(1)

    # Validation pour bot neural
    if args.bot_type == "neural" and not args.neural_weights:
        parser.error("--neural-weights est requis quand --bot-type=neural")

    if args.neural_weights and len(args.neural_weights) != 5:
        parser.error("--neural-weights doit contenir exactement 5 valeurs")

    # Warning for large numbers
    if args.num_games > 20:
        print(f"⚠️  Attention: Vous allez lancer {args.num_games} parties visuelles.")
        print(
            "   Chaque partie ouvrira une fenêtre pygame qui se fermera automatiquement."
        )
        print("   Cela peut prendre du temps...")
        confirm = input("   Voulez-vous continuer ? (o/n): ").lower()
        if confirm not in ["o", "oui", "y", "yes"]:
            print("Opération annulée.")
            sys.exit(0)

    # Affichage du bot sélectionné
    bot_display = {
        "single": "🧠 Bot Simple (1 tuyau)",
        "two_pipes": "🔮 Bot Deux Tuyaux (2 tuyaux)",
        "neural": f"🤖 Bot Neural (poids: {args.neural_weights})",
    }
    print(f"Bot sélectionné: {bot_display[args.bot_type]}")

    try:
        run_sequential_visual_batch(
            num_games=args.num_games,
            output_file=args.output,
            verbose=not args.quiet,
            bot_type=args.bot_type,
            neural_weights=args.neural_weights,
        )
        print("\n🎉 Batch testing visuel terminé avec succès!")

    except KeyboardInterrupt:
        print("\nBatch testing visuel interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"Erreur pendant le batch testing visuel: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
