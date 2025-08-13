#!/usr/bin/env python3
"""Algorithme génétique avec plusieurs oiseaux simultanés - Version entièrement automatique"""

import math
import random
import time
from typing import List, Tuple

import pygame

import src.config as config
from src.bird import Bird
from src.score import Score
from src.utils import collision
from src.windows import Background, Pipe


class GeneticBird(Bird):
    """Oiseau avec poids du perceptron et capacité de décision autonome"""

    def __init__(self, weights: List[float], color: tuple = None):
        super().__init__()
        self.weights = weights  # [w1, w2, w3, w4, bias]
        self.fitness = 0
        self.frames_survived = 0
        self.is_alive = True
        self.color = color or (255, 255, 0)  # Couleur par défaut jaune

        # Créer une surface colorée pour cet oiseau
        self.colored_image = self.image.copy()
        self.colored_image.fill(self.color, special_flags=pygame.BLEND_MULT)

    def decide_action(self, upper_pipe, lower_pipe) -> bool:
        """Décision du perceptron"""
        if not upper_pipe or not lower_pipe:
            return False

        # Calculer les métriques
        velocity = self.velocity_y
        dist_top = self.y - (upper_pipe.y + upper_pipe.h)
        dist_bottom = lower_pipe.y - self.y
        horizontal_dist = upper_pipe.x - self.x

        # Normaliser les métriques
        velocity_norm = velocity / 20.0  # Normaliser vitesse (-20 à +20 → -1 à +1)
        dist_top_norm = (
            dist_top / config.SCREEN_HEIGHT
        )  # Normaliser par hauteur d'écran
        dist_bottom_norm = (
            dist_bottom / config.SCREEN_HEIGHT
        )  # Normaliser par hauteur d'écran
        horizontal_dist_norm = (
            horizontal_dist / config.SCREEN_WIDTH
        )  # Normaliser par largeur d'écran

        inputs = [velocity_norm, dist_top_norm, dist_bottom_norm, horizontal_dist_norm]

        # Perceptron avec fonction logistique et bias
        linear_output = (
            sum(w * x for w, x in zip(self.weights[:-1], inputs)) + self.weights[-1]
        )  # bias is the last weight

        try:
            logistic_output = 1.0 / (1.0 + math.exp(-linear_output))
        except OverflowError:
            logistic_output = 0.0 if linear_output < 0 else 1.0

        return logistic_output >= 0.5

    def draw(self, screen: pygame.Surface) -> None:
        """Dessiner l'oiseau avec sa couleur"""
        if self.is_alive:
            rotated_image = pygame.transform.rotate(
                self.colored_image, self.current_rotation
            )
            rotated_rect = rotated_image.get_rect(center=self.rect.center)
            screen.blit(rotated_image, rotated_rect)


class FullyAutoMultiGeneticGame:
    """Jeu avec plusieurs oiseaux génétiques simultanés - Version entièrement automatique"""

    def __init__(self, population_weights: List[List[float]], seed: int = None):
        """
        Args:
            population_weights: Liste des poids pour chaque oiseau
            seed: Graine pour reproductibilité
        """
        # Initialiser pygame
        pygame.init()
        pygame.display.set_caption("Algorithme Génétique Multi-Oiseaux - Auto")
        self.screen = pygame.display.set_mode(
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        )
        self.background = Background()
        self.clock = pygame.time.Clock()

        # Initialiser la graine
        if seed is not None:
            random.seed(seed)
            self.seed = seed
        else:
            import time

            self.seed = int(time.time() * 1000000) % 2**32
            random.seed(self.seed)

        # Créer les oiseaux avec différentes couleurs
        self.birds = []
        colors = [
            (255, 255, 0),  # Jaune
            (255, 0, 0),  # Rouge
            (0, 255, 0),  # Vert
            (0, 0, 255),  # Bleu
            (255, 0, 255),  # Magenta
            (0, 255, 255),  # Cyan
            (255, 128, 0),  # Orange
            (128, 0, 255),  # Violet
            (255, 192, 203),  # Rose
            (128, 128, 128),  # Gris
        ]

        for i, weights in enumerate(population_weights):
            color = colors[i % len(colors)]
            bird = GeneticBird(weights, color)
            self.birds.append(bird)

        # Pipes et score
        self.upper_pipes: List[Pipe] = []
        self.lower_pipes: List[Pipe] = []
        self.score = Score()
        self.last_gap_y = None

        # Stats
        self.frame_count = 0
        self.alive_count = len(self.birds)

    def init_pipes(self):
        """Initialiser les pipes"""
        for i in range(3, 9, 4):
            pipe_up, pipe_bot = self.generate_pipes()
            pipe_up.x = config.SCREEN_WIDTH + pipe_up.w * i
            pipe_bot.x = config.SCREEN_WIDTH + pipe_bot.w * i
            self.upper_pipes.append(pipe_up)
            self.lower_pipes.append(pipe_bot)

    def generate_pipes(self) -> Tuple[Pipe, Pipe]:
        """Générer une paire de pipes"""
        pipe_x = config.SCREEN_WIDTH + 10

        if self.last_gap_y is None:
            gap_y = (config.MIN_GAP_Y + config.MAX_GAP_Y) // 2
        else:
            min_allowed_gap = max(
                config.MIN_GAP_Y, self.last_gap_y - config.MAX_GAP_TRANSITION
            )
            max_allowed_gap = min(
                config.MAX_GAP_Y, self.last_gap_y + config.MAX_GAP_TRANSITION
            )
            gap_y = random.randint(min_allowed_gap, max_allowed_gap)

        self.last_gap_y = gap_y

        pipetop = Pipe(pipe_x, gap_y - config.PIPE_HEIGHT, config.PIPETOP)
        pipebottom = Pipe(pipe_x, gap_y + config.PIPE_GAP, config.PIPEBOTTOM)

        return pipetop, pipebottom

    def get_next_pipe_pair(self):
        """Trouver la prochaine paire de pipes"""
        for upper, lower in zip(self.upper_pipes, self.lower_pipes):
            if (
                upper.x + upper.w > config.SCREEN_WIDTH * 0.2
            ):  # Position approximative des oiseaux
                return upper, lower
        return None, None

    def update_birds(self):
        """Mettre à jour tous les oiseaux vivants"""
        next_upper, next_lower = self.get_next_pipe_pair()

        for bird in self.birds:
            if not bird.is_alive:
                continue

            bird.frames_survived = self.frame_count

            # Décision du bot
            if next_upper and next_lower:
                if bird.decide_action(next_upper, next_lower):
                    bird.flap()

            # Physique de l'oiseau
            bird.next_status(None, False)  # Pas de dessin ici

            # Vérifier collisions avec pipes
            bird_collision = collision(bird, self.upper_pipes) or collision(
                bird, self.lower_pipes
            )

            # Vérifier limites
            bird_out_of_bounds = (
                bird.y > config.SCREEN_HEIGHT - bird.h or bird.y < bird.min_y
            )

            # Marquer comme mort si collision ou hors limites
            if bird_collision or bird_out_of_bounds:
                bird.is_alive = False
                self.alive_count -= 1

    def update_pipes(self):
        """Mettre à jour les pipes"""
        # Ajouter nouvelles pipes
        if self.can_spawn_pipes():
            upper, lower = self.generate_pipes()
            self.upper_pipes.append(upper)
            self.lower_pipes.append(lower)

        # Supprimer anciennes pipes
        self.upper_pipes = [pipe for pipe in self.upper_pipes if pipe.x > -pipe.w]
        self.lower_pipes = [pipe for pipe in self.lower_pipes if pipe.x > -pipe.w]

        # Mettre à jour positions
        for pipe in self.upper_pipes + self.lower_pipes:
            pipe.next_status(None, False)

    def can_spawn_pipes(self) -> bool:
        """Vérifier si on peut spawner de nouvelles pipes"""
        if not self.upper_pipes:
            return True
        last = self.upper_pipes[-1]
        return config.SCREEN_WIDTH - (last.x + last.w) > last.w * 3.0

    def update_score(self):
        """Mettre à jour le score - logique corrigée pour Flappy Bird"""
        # Dans Flappy Bird, les oiseaux restent fixes et les pipes bougent vers eux
        for pipe in self.upper_pipes:
            # Position fixe des oiseaux (comme dans le jeu original)
            bird_x = config.SCREEN_WIDTH * 0.2  # Position approximative des oiseaux

            # Vérifier si cette pipe vient de passer les oiseaux
            pipe_right = pipe.x + pipe.w
            # Si la pipe était à droite de l'oiseau avant et maintenant à gauche
            if pipe_right <= bird_x and pipe_right - pipe.velocity_x > bird_x:
                # Cette pipe vient de passer ! Donner des points aux oiseaux vivants
                for bird in self.birds:
                    if bird.is_alive:
                        bird.fitness += 1
                self.score.add()  # Score global pour l'affichage

    def draw_all(self):
        """Dessiner tout le jeu"""
        # Background
        self.background.draw(self.screen)

        # Pipes
        for upper, lower in zip(self.upper_pipes, self.lower_pipes):
            upper.next_status(self.screen, draw=True)
            lower.next_status(self.screen, draw=True)

        # Oiseaux (seulement les vivants)
        for bird in self.birds:
            if bird.is_alive:
                bird.draw(self.screen)

        # Score et stats
        self.score.draw(self.screen)

        # Info génération
        font = pygame.font.Font(None, 36)
        info_text = font.render(
            f"Oiseaux vivants: {self.alive_count}/{len(self.birds)}",
            True,
            (255, 255, 255),
        )
        self.screen.blit(info_text, (10, 50))

        frame_text = font.render(f"Frame: {self.frame_count}", True, (255, 255, 255))
        self.screen.blit(frame_text, (10, 90))

        pygame.display.update()
        self.clock.tick(config.FPS)

    def run_generation(self):
        """Lancer une génération complète"""
        self.init_pipes()

        # Boucle principale
        running = True
        while running and self.alive_count > 0:
            # Gérer les événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                ):
                    running = False

            self.frame_count += 1

            # Mettre à jour le jeu
            self.update_birds()
            self.update_pipes()
            self.update_score()

            # Dessiner
            self.draw_all()

        # Pause courte pour voir le résultat final
        time.sleep(1)

        return [
            (bird.weights, bird.fitness, bird.frames_survived) for bird in self.birds
        ]


def run_fully_auto_evolution(max_generations=50):
    """Lance l'évolution entièrement automatique avec visualisation multi-oiseaux"""
    print("🧬 ALGORITHME GÉNÉTIQUE MULTI-OISEAUX - ENTIÈREMENT AUTOMATIQUE")
    print("=" * 70)
    print("Les générations s'enchaînent automatiquement!")
    print("ESC pour quitter à tout moment")
    print("=" * 70)

    # Créer population initiale
    population_size = 10000  # Plus petit pour une meilleure visibilité
    population_weights = []

    for _ in range(population_size):
        weights = [random.uniform(-2, 2) for _ in range(5)]  # 4 poids + 1 bias
        population_weights.append(weights)

    generation = 1
    best_ever_fitness = 0
    best_ever_weights = None

    while generation <= max_generations:
        print(f"\n🧬 === GÉNÉRATION {generation}/{max_generations} ===")

        # Créer et lancer le jeu multi-oiseaux
        game = FullyAutoMultiGeneticGame(population_weights, seed=12345 + generation)
        pygame.display.set_caption(
            f"Génération {generation}/{max_generations} - Auto Evolution"
        )

        results = game.run_generation()

        # Vérifier si l'utilisateur veut quitter
        pygame.quit()
        pygame.init()  # Réinitialiser pour la génération suivante

        # Trier par performance (fitness, puis frames)
        results.sort(key=lambda x: (x[1], x[2]), reverse=True)

        # Statistiques
        best_fitness = results[0][1] if results else 0
        avg_fitness = sum(r[1] for r in results) / len(results) if results else 0

        print(f"📊 Résultats Génération {generation}:")
        print(f"   🏆 Meilleur: Score {best_fitness}")
        print(f"   📈 Moyenne: Score {avg_fitness:.1f}")

        # Garder le record absolu
        if best_fitness > best_ever_fitness:
            best_ever_fitness = best_fitness
            best_ever_weights = results[0][0] if results else None
            print(f"   🎉 NOUVEAU RECORD! Score {best_ever_fitness}")

        # Afficher le top 3
        print("   🥇 TOP 3:")
        for i, (weights, fitness, frames) in enumerate(results[:3]):
            weights_str = ", ".join(f"{w:5.2f}" for w in weights)
            print(
                f"      {i+1}. Score: {fitness:2d}, Frames: {frames:3d}, Poids: [{weights_str}]"
            )

        # Si c'est la dernière génération ou qu'on a atteint un excellent score
        if generation >= max_generations or best_fitness >= 10000:
            if best_fitness >= 10000:
                print(
                    f"\n🎉 OBJECTIF ATTEINT! Score de {best_fitness} à la génération {generation}"
                )
            break

        # Stratégie d'évolution: 10% élite + 20% mutés + 60% reproduction + 10% meilleurs avec bruit
        elite_count = max(1, int(population_size * 0.10))  # 10% élite intacte
        mutated_count = max(1, int(population_size * 0.20))  # 20% avec mutation
        breeding_count = max(1, int(population_size * 0.60))  # 60% reproduction
        noisy_elite_count = (
            population_size - elite_count - mutated_count - breeding_count
        )  # 10% meilleurs avec bruit

        # Pour la reproduction, utiliser le top 50%
        breeding_pool_size = max(1, int(population_size * 0.50))
        breeding_pool = results[:breeding_pool_size]

        # Créer nouvelle population
        population_weights = []

        # 1. Garder l'élite intacte (10% meilleurs)
        for i in range(elite_count):
            population_weights.append(results[i][0].copy())

        # 2. Sélectionner aléatoirement 20% parmi les 30% meilleurs avec mutation
        top_30_percent_size = max(1, int(population_size * 0.30))
        top_30_percent = results[:top_30_percent_size]

        for _ in range(mutated_count):
            if top_30_percent:
                # Sélectionner aléatoirement un individu parmi les 30% meilleurs
                selected_individual = random.choice(top_30_percent)
                weights = selected_individual[0].copy()

                # Appliquer mutation
                for j in range(len(weights)):
                    if random.random() < 0.05:  # 5% chance de mutation par poids
                        weights[j] += random.uniform(-0.2, 0.2)
                        weights[j] = max(-5, min(5, weights[j]))
                population_weights.append(weights)
            else:
                # Si pas assez d'individus, créer un nouveau aléatoire
                population_weights.append(
                    [random.uniform(-2, 2) for _ in range(5)]
                )  # 4 poids + 1 bias

        # 3. Reproduction avec les 50% meilleurs (60% de la population)
        for _ in range(breeding_count):
            parent1 = random.choice(breeding_pool)[0]
            parent2 = random.choice(breeding_pool)[0]

            # Croisement
            child_weights = []
            for w1, w2 in zip(parent1, parent2):
                child_weights.append(w1 if random.random() < 0.5 else w2)

            # Mutation légère sur les enfants
            for j in range(len(child_weights)):
                if random.random() < 0.02:  # 2% mutation
                    child_weights[j] += random.uniform(-0.1, 0.1)
                    child_weights[j] = max(-5, min(5, child_weights[j]))

            population_weights.append(child_weights)

        # 4. Meilleurs individus avec bruit de ±10% (10%)
        for i in range(noisy_elite_count):
            if i < len(results):
                # Prendre un des meilleurs individus
                base_weights = results[i][0].copy()
                noisy_weights = []

                # Ajouter du bruit de ±10% à chaque poids
                for weight in base_weights:
                    noise_factor = random.uniform(-0.1, 0.1)  # ±10%
                    noisy_weight = weight * (1 + noise_factor)
                    # Limiter les poids dans une plage raisonnable
                    noisy_weight = max(-5, min(5, noisy_weight))
                    noisy_weights.append(noisy_weight)

                population_weights.append(noisy_weights)
            else:
                # Si pas assez d'individus, utiliser le meilleur avec plus de bruit
                base_weights = results[0][0].copy()
                noisy_weights = []
                for weight in base_weights:
                    noise_factor = random.uniform(
                        -0.2, 0.2
                    )  # ±20% si on manque d'individus
                    noisy_weight = weight * (1 + noise_factor)
                    noisy_weight = max(-5, min(5, noisy_weight))
                    noisy_weights.append(noisy_weight)
                population_weights.append(noisy_weights)

        generation += 1

        # Petite pause entre générations pour voir les stats
        print("   ⏳ Prochaine génération dans 2 secondes...")
        time.sleep(2)

    # Résultat final
    print("\n🏆 === ÉVOLUTION TERMINÉE ===")
    print(f"🎯 Meilleur résultat sur {generation} générations:")
    print(f"   Score: {best_ever_fitness}")
    if best_ever_weights:
        print(
            f"   Poids optimaux: [{', '.join(f'{w:.6f}' for w in best_ever_weights)}]"
        )
    print("=" * 70)

    pygame.quit()


if __name__ == "__main__":
    run_fully_auto_evolution(max_generations=20)
