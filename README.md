# Flappy Bird GodMod 🐦

Une version améliorée de Flappy Bird avec IA bot, système de seeds reproductibles et génération de tuyaux intelligente.

## 🚀 Installation et Lancement

### Prérequis
```bash
# Installer les dépendances avec Poetry
poetry install

# Ou avec pip
pip install -r requirements.txt
```

### Lancement Rapide
```bash
# Jouer en mode humain
python main.py

# Jouer avec le bot IA simple
python main_bot.py

# Jouer avec le bot IA avancé (deux tuyaux)
python main_bot.py -b two_pipes

# Lancer 5 parties avec le bot simple
python main_bot.py -n 5

# Lancer 10 parties avec le bot avancé
python main_bot.py -n 10 -b two_pipes

# Comparer les deux bots
python test_two_bots.py -n 20
```

## 🤖 Mode Bot IA

Cette version inclut **deux types de bots IA** qui jouent automatiquement à Flappy Bird sans intervention humaine :

### 🧠 Bot Simple (1 tuyau)
- Analyse uniquement le prochain tuyau
- Logique de décision rapide et efficace
- Bon pour la plupart des situations

### 🔮 Bot Avancé (2 tuyaux)
- Analyse les **deux prochains tuyaux** simultanément
- Planification à plus long terme
- Meilleure anticipation des situations complexes
- Plus de calculs mais potentiellement de meilleurs scores

### Comment ça Marche

Le bot IA remplace les contrôles clavier et prend des décisions basées sur :
1. **Simulation Prédictive** : Crée des copies de l'état du jeu pour prédire les résultats
2. **Évitement de Collision** : Teste les actions "battre des ailes" et "ne pas battre" pour éviter les tuyaux
3. **Centrage dans les Gaps** : Quand aucune collision n'est imminente, essaie de rester centré dans les ouvertures

### Fonctionnalités
- **Entièrement Autonome** : Aucune intervention humaine requise (sauf ESC pour quitter)
- **Indicateur Visuel** : Label "AI BOT" apparaît en haut à droite
- **Statistiques de Performance** : Suivi des scores, meilleurs scores et moyennes sur plusieurs parties
- **Logique de Décision Optimisée** : Utilise une simulation physique légère pour des performances rapides

### Logique de Décision du Bot

Le bot analyse le prochain tuyau à venir et :
1. Simule la physique de l'oiseau (position et vélocité) pour les deux scénarios (battre/ne pas battre)
2. Vérifie les collisions avec détection de collision rectangulaire (rapide et efficace)
3. Choisit l'action qui évite la collision
4. Si les deux actions sont sûres, choisit celle qui garde l'oiseau centré dans l'ouverture
5. Si les deux actions mènent à une collision, choisit basé sur la proximité au centre de l'ouverture

### Utilisation

```python
from src.game import Game

# Partie avec bot simple (défaut)
bot_game = Game(bot_mode=True)
bot_game.play_game()

# Partie avec bot avancé (deux tuyaux)
advanced_bot_game = Game(bot_mode=True, bot_type="two_pipes")
advanced_bot_game.play_game()

# Partie humaine (défaut)
human_game = Game(bot_mode=False)  # ou juste Game()
human_game.play_game()
```

### Commandes d'Utilisation

```bash
# Bot simple - parties infinies
python main_bot.py

# Bot avancé - parties infinies
python main_bot.py -b two_pipes

# 5 parties avec bot simple
python main_bot.py -n 5

# 10 parties avec bot avancé
python main_bot.py -n 10 -b two_pipes

# Aide et options
python main_bot.py --help
```

## 🌱 Système de Seeds - Parties Reproductibles

Le système de seeds permet de reproduire exactement les mêmes parties, essentiel pour le débogage, l'analyse de performance et la comparaison d'algorithmes.

### Génération Automatique des Seeds
- **Chaque partie** reçoit automatiquement une seed unique
- **Basée sur timestamp** : `int(time.time() * 1000000) % 2^32`
- **Séquentielle** : Partie 1 = base_seed + 1, Partie 2 = base_seed + 2, etc.
- **Sauvée dans CSV** : Colonne `seed` pour chaque partie

### Reproductibilité
- **Même seed** = **même partie exacte**
- **Même score, mêmes tuyaux, mêmes décisions bot**
- **Déterminisme complet** du générateur aléatoire

### Format CSV
```csv
game_id,seed,score,duration_seconds,pipes_passed,status,timestamp
1,1691415123457,23,2.156,23,completed,2025-08-07T19:30:45.123456
2,1691415123458,8,0.894,8,completed,2025-08-07T19:30:46.234567
```

### Reproduction de Parties
```bash
# Reproduire avec une seed connue (bot simple)
python replay_seed.py -s 1691415123457

# Mode visuel avec bot simple (voir la partie se jouer)
python replay_seed.py -s 1691415123457 -v

# Reproduire avec bot avancé (deux tuyaux)
python replay_seed.py -s 1691415123457 -b two_pipes

# Mode visuel avec bot avancé
python replay_seed.py -s 1691415123457 -v -b two_pipes

# Chercher une seed depuis un CSV
python replay_seed.py -f results.csv -g 42  # Game ID 42
```

## 🎯 Génération de Tuyaux Intelligente

Ce projet inclut une génération intelligente de tuyaux qui prévient les séquences impossibles à naviguer.

### Problème Résolu
Dans l'implémentation originale, les ouvertures de tuyaux étaient complètement aléatoires, pouvant créer des scenarios impossibles comme :
- Une ouverture en haut de l'écran suivie immédiatement par une ouverture en bas
- Des transitions si larges que même un jeu parfait ne pourrait les naviguer
- Des séquences nécessitant des temps de réaction surhumains

### Solution : Transitions d'Ouvertures Contraintes

#### Comment ça Marche
1. **Premier Tuyau** : Toujours généré au centre de la zone jouable pour un début équitable
2. **Tuyaux Suivants** : Position d'ouverture contrainte basée sur la position du tuyau précédent
3. **Transition Maximum** : Limite la distance maximale entre deux ouvertures consécutives
4. **Contraintes de Limites** : Garde les ouvertures dans des bornes verticales raisonnables

#### Paramètres de Configuration

Dans `src/config.py` :
```python
MAX_GAP_TRANSITION = 150  # Distance verticale maximale entre ouvertures consécutives
MIN_GAP_Y = 100          # Position Y minimale du centre d'ouverture (du haut)
MAX_GAP_Y = 500          # Position Y maximale du centre d'ouverture (du haut)
```

#### Algorithme
Pour chaque nouveau tuyau :
1. Si c'est le premier tuyau : `gap_y = (MIN_GAP_Y + MAX_GAP_Y) / 2`
2. Sinon :
   - Calculer la plage autorisée : `[last_gap_y - MAX_GAP_TRANSITION, last_gap_y + MAX_GAP_TRANSITION]`
   - Contraindre aux limites : `[MAX(MIN_GAP_Y, min_range), MIN(MAX_GAP_Y, max_range)]`
   - Choisir une position aléatoire dans cette plage contrainte

#### Avantages
- **Toujours Jouable** : Aucune séquence de tuyaux impossible
- **Toujours Challengeant** : Maintient l'aléatoire dans des bornes raisonnables
- **Difficulté Fluide** : Les transitions graduelles semblent plus naturelles
- **Compatible Bot** : L'IA peut mieux prédire et naviguer les séquences contraintes
- **Configurable** : Facile d'ajuster la difficulté en changeant les paramètres de contrainte

## 📊 Tests en Lot (Batch Testing)

### Tests Séquentiels
```bash
# Tests séquentiels simples
python sequential.py 10                              # 10 parties séquentielles
python sequential.py 100 -o results.csv             # Sauver dans un fichier spécifique

# Tests visuels séquentiels (chaque partie s'ouvre et se ferme automatiquement)
python sequential_visual.py 5                       # 5 parties visuelles bot simple
python sequential_visual.py 10 -b two_pipes         # 10 parties visuelles bot avancé
python sequential_visual.py 20 -b two_pipes -o test.csv  # Bot avancé avec fichier custom
```

### Analyse des Résultats
```bash
# Analyser les résultats d'un fichier CSV
python analyze_seeds.py results.csv

# Vue tableau des scores seulement
python analyze_seeds.py results.csv --scores-only
```

## 🎮 Contrôles

### Mode Humain
- **ESPACE** ou **FLÈCHE HAUT** : Battre des ailes
- **CLIC GAUCHE SOURIS** : Battre des ailes
- **ESC** : Quitter le jeu

### Mode Bot
- **ESC** : Quitter le jeu (le bot gère automatiquement les battements d'ailes)
- Indicateur visuel "AI BOT" en haut à droite

## 📁 Structure du Projet

```
flappybird_godmod/
├── src/                     # Code source principal
│   ├── game.py             # Classe principale du jeu
│   ├── bird.py             # Logique de l'oiseau
│   ├── windows.py          # Arrière-plan et tuyaux
│   ├── score.py            # Système de score
│   ├── utils.py            # Utilitaires (détection collision)
│   └── config.py           # Configuration
├── assets/                 # Ressources graphiques
├── main.py                 # Lancement mode humain
├── main_bot.py            # Lancement mode bot
├── replay_seed.py         # Reproduction de parties avec seed
├── sequential.py          # Tests séquentiels
├── sequential_visual.py   # Tests visuels séquentiels
└── analyze_seeds.py       # Analyse des résultats CSV
```

## 🎯 Cas d'Usage

### Débogage d'un Score Faible
```bash
# Trouver une partie avec score 0
python analyze_seeds.py results.csv --scores-only | grep "    0"
# Reproduire cette partie
python replay_seed.py -s [seed_trouvée] -v
```

### Analyser des Patterns
```bash
# Identifier les parties exceptionnelles
python analyze_seeds.py results.csv
# Reproduire les meilleures et pires
python replay_seed.py -s [best_seed] -v
python replay_seed.py -s [worst_seed] -v
```

### Session Complète d'Analyse
```bash
# 1. Lancer un batch test
python sequential.py 50

# 2. Analyser les résultats
python analyze_seeds.py sequential_results_[timestamp].csv

# 3. Reproduire la meilleure partie
python replay_seed.py -s [best_seed] -v
```

## ✨ Fonctionnalités Principales

- **🤖 Bot IA Autonome** : Joue automatiquement avec logique de décision avancée
- **🌱 Seeds Reproductibles** : Chaque partie peut être reproduite exactement
- **🎯 Tuyaux Intelligents** : Génération contrainte pour éviter les séquences impossibles
- **📊 Batch Testing** : Tests en lot avec statistiques détaillées
- **🎮 Mode Visuel et Auto-Close** : Options pour différents types d'analyse
- **📈 Analyse Avancée** : Outils pour analyser les performances et patterns

## 🔧 Configuration

Ajustez les paramètres dans `src/config.py` :
- **Dimensions d'écran** : `SCREEN_WIDTH`, `SCREEN_HEIGHT`
- **FPS** : `FPS`
- **Contraintes de tuyaux** : `MAX_GAP_TRANSITION`, `MIN_GAP_Y`, `MAX_GAP_Y`
- **Mode bot par défaut** : `BOT_MODE`

## 🏆 Objectifs

Ce projet améliore Flappy Bird avec :
1. **Reproductibilité Scientifique** : Seeds pour des expériences contrôlées
2. **IA Performante** : Bot capable de scores élevés et consistants
3. **Jouabilité Équilibrée** : Tuyaux toujours navigables mais challengeants
4. **Outils d'Analyse** : Suite complète pour analyser les performances

Parfait pour la recherche en IA, l'analyse de gameplay, ou simplement pour voir un bot maîtriser Flappy Bird ! 🎮✨
