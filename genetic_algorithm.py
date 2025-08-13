#!/usr/bin/env python3
"""Algorithme génétique pour optimiser les poids du Bot_neural"""

import random
from typing import List, Tuple

import pygame

from src.game import Game


class Individual:
    """Représente un individu (oiseau) avec ses poids et son score"""

    def __init__(self, weights: List[float]):
        self.weights = weights  # [w1, w2, w3, w4, bias]
        self.fitness = 0  # Score obtenu dans le jeu
        self.frames_survived = 0  # Nombre de frames survécues

    def __str__(self):
        return f"Individual(weights={[f'{w:.3f}' for w in self.weights]}, fitness={self.fitness}, frames={self.frames_survived})"


class GeneticAlgorithm:
    """Algorithme génétique pour optimiser les poids du perceptron"""

    def __init__(
        self,
        population_size: int = 20,
        survival_rate: float = 0.2,
        mutation_rate: float = 0.02,
    ):
        """
        Args:
            population_size: Nombre d'individus par génération
            survival_rate: Pourcentage d'individus qui survivent (20% = 0.2)
            mutation_rate: Taux de mutation (2% = 0.02)
        """
        self.population_size = population_size
        self.survival_rate = survival_rate
        self.mutation_rate = mutation_rate
        self.survivors_count = int(population_size * survival_rate)

        # Créer la population initiale
        self.population = self._create_initial_population()
        self.generation = 1

    def _create_initial_population(self) -> List[Individual]:
        """Crée la population initiale avec des poids aléatoires"""
        population = []

        for _ in range(self.population_size):
            # Initialiser les poids aléatoirement entre -2 et 2 (4 poids + 1 bias)
            weights = [random.uniform(-2.0, 2.0) for _ in range(5)]
            individual = Individual(weights)
            population.append(individual)

        return population

    def evaluate_generation(self, seed: int = None) -> None:
        """Évalue tous les individus de la génération sur le même parcours

        Args:
            seed: Graine pour assurer que tous les oiseaux jouent sur le même parcours
        """
        print(f"\n🧬 === GÉNÉRATION {self.generation} ===")
        print(f"Évaluation de {len(self.population)} individus...")

        # Utiliser une graine fixe pour que tous les oiseaux jouent sur le même parcours
        if seed is None:
            seed = random.randint(1, 1000000)

        # Évaluer chaque individu
        for i, individual in enumerate(self.population):
            print(f"  🐦 Oiseau {i+1}/{len(self.population)}... ", end="", flush=True)

            # Créer une partie avec les poids de cet individu
            fitness, frames = self._evaluate_individual(individual.weights, seed)
            individual.fitness = fitness
            individual.frames_survived = frames

            print(f"Score: {fitness}, Frames: {frames}")

        # Trier par fitness (score décroissant, puis frames décroissant)
        self.population.sort(key=lambda x: (x.fitness, x.frames_survived), reverse=True)

        # Afficher les résultats
        self._print_generation_results()

    def _evaluate_individual(self, weights: List[float], seed: int) -> Tuple[int, int]:
        """Évalue un individu en le faisant jouer au jeu

        Args:
            weights: Poids du perceptron
            seed: Graine pour la reproductibilité

        Returns:
            Tuple[int, int]: (fitness/score, frames_survived)
        """
        # Créer une partie spéciale pour l'évaluation
        game = EvaluationGame(bot_mode=True, seed=seed, bot_type="neural")
        game.neural_weights = weights  # Passer les poids au bot

        # Jouer la partie
        game.play_game()

        return game.score.score, game.frame_count

    def evolve_generation(self) -> None:
        """Fait évoluer la population vers la génération suivante"""
        print(f"\n🔄 Évolution vers la génération {self.generation + 1}...")

        # 1. Sélectionner les survivants (20% des meilleurs)
        survivors = self.population[
            : max(1, self.survivors_count)
        ]  # Au moins 1 survivant
        print(f"   Survivants: {len(survivors)} individus")

        # 2. Créer la nouvelle population par reproduction
        new_population = []

        # Garder les survivants dans la nouvelle génération
        for survivor in survivors:
            new_population.append(Individual(survivor.weights.copy()))

        # Générer le reste par croisement et mutation
        while len(new_population) < self.population_size:
            # Sélectionner deux parents parmi les survivants
            parent1 = random.choice(survivors)
            parent2 = random.choice(survivors)

            # Croisement
            child_weights = self._crossover(parent1.weights, parent2.weights)

            # Mutation
            child_weights = self._mutate(child_weights)

            new_population.append(Individual(child_weights))

        # Remplacer l'ancienne population
        self.population = new_population
        self.generation += 1

        print(f"   Nouvelle génération créée: {len(new_population)} individus")

    def _crossover(
        self, parent1_weights: List[float], parent2_weights: List[float]
    ) -> List[float]:
        """Croisement entre deux parents (mélange des poids)

        Args:
            parent1_weights: Poids du parent 1
            parent2_weights: Poids du parent 2

        Returns:
            List[float]: Poids de l'enfant
        """
        child_weights = []

        for w1, w2 in zip(parent1_weights, parent2_weights):
            # Choisir aléatoirement entre les poids des deux parents
            if random.random() < 0.5:
                child_weights.append(w1)
            else:
                child_weights.append(w2)

        return child_weights

    def _mutate(self, weights: List[float]) -> List[float]:
        """Applique une mutation aux poids

        Args:
            weights: Poids originaux

        Returns:
            List[float]: Poids mutés
        """
        mutated_weights = []

        for weight in weights:
            if random.random() < self.mutation_rate:
                # Mutation: ajouter un petit bruit aléatoire
                mutation = random.uniform(-0.1, 0.1)
                mutated_weight = weight + mutation
                # Limiter les poids entre -5 et 5
                mutated_weight = max(-5.0, min(5.0, mutated_weight))
                mutated_weights.append(mutated_weight)
            else:
                mutated_weights.append(weight)

        return mutated_weights

    def _print_generation_results(self) -> None:
        """Affiche les résultats de la génération"""
        print(f"\n📊 Résultats Génération {self.generation}:")
        print("=" * 60)

        # Top 5
        print("🏆 TOP 5:")
        for i in range(min(5, len(self.population))):
            individual = self.population[i]
            print(
                f"  {i+1}. Score: {individual.fitness:2d}, Frames: {individual.frames_survived:4d}, "
                f"Poids: [{', '.join(f'{w:6.3f}' for w in individual.weights)}]"
            )

        # Statistiques
        if self.population:
            best = self.population[0]
            avg_fitness = sum(ind.fitness for ind in self.population) / len(
                self.population
            )
            avg_frames = sum(ind.frames_survived for ind in self.population) / len(
                self.population
            )

            print("\n📈 Statistiques:")
            print(f"   Meilleur score: {best.fitness}")
            print(f"   Score moyen: {avg_fitness:.1f}")
            print(f"   Frames moyennes: {avg_frames:.0f}")

    def get_best_individual(self) -> Individual:
        """Retourne le meilleur individu de la génération actuelle"""
        return self.population[0] if self.population else None


class EvaluationGame(Game):
    """Classe spéciale pour évaluer les individus AVEC affichage visuel"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.frame_count = 0

    def _handle_game_loop(self):
        """Override pour compter les frames AVEC affichage complet"""
        self.frame_count += 1

        # Handle events (quit events always processed, tap events only in human mode)
        for event in pygame.event.get():
            if self.check_quit_event(event):
                return False  # Quit si ESC
            if not self.bot_mode and self.is_tap_event(event):
                self.bird.flap()

        # Bot decision making
        if self.bot_mode and self.bot:
            decision = self.bot.decide_action()
            if decision == "flap":
                self.bird.flap()

        # Update score
        self._update_score()

        # Check for collisions
        if self._check_collisions():
            return False

        # Update game objects AVEC drawing
        self._update_pipes()
        self._update_and_draw()  # Cette fonction fait le rendu complet

        # Check if bird hit ground
        if self.bird.y > self.bird_lowest_height:
            return False

        return True

    def _handle_game_over(self):
        """Skip game over loop for evaluation"""
        return


def run_evolution(generations: int = 50, seed_base: int = 12345):
    """Lance l'algorithme génétique pour plusieurs générations

    Args:
        generations: Nombre de générations à évoluer
        seed_base: Graine de base pour la reproductibilité
    """
    import pygame

    pygame.init()  # Initialiser pygame normalement AVEC affichage

    print("🧬 ALGORITHME GÉNÉTIQUE - Optimisation Bot_neural")
    print("=" * 60)

    # Créer l'algorithme génétique
    ga = GeneticAlgorithm(population_size=20, survival_rate=0.2, mutation_rate=0.02)

    # Évolution sur plusieurs générations
    for gen in range(generations):
        # Utiliser une graine différente pour chaque génération mais reproductible
        generation_seed = seed_base + gen

        # Évaluer la génération actuelle
        ga.evaluate_generation(seed=generation_seed)

        # Vérifier si on a atteint un bon score
        best = ga.get_best_individual()
        if best and best.fitness >= 50:  # Critère d'arrêt
            print(
                f"\n🎉 OBJECTIF ATTEINT! Score de {best.fitness} atteint à la génération {ga.generation}"
            )
            break

        # Évoluer vers la génération suivante (sauf à la dernière)
        if gen < generations - 1:
            ga.evolve_generation()

        print("\n" + "=" * 60)

    # Résultat final
    print("\n🏆 RÉSULTAT FINAL:")
    best = ga.get_best_individual()
    if best:
        print(f"Meilleur individu après {ga.generation} générations:")
        print(f"Score: {best.fitness}, Frames: {best.frames_survived}")
        print(f"Poids optimaux: [{', '.join(f'{w:.6f}' for w in best.weights)}]")

    return ga


if __name__ == "__main__":
    # Lancer l'évolution
    final_ga = run_evolution(generations=10, seed_base=12345)
