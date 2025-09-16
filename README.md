# L'Assistant du Héros

## Pitch du jeu

Nous proposons de développer un jeu de plateforme/aventure où le joueur incarne l'assistant du héros, et non le héros lui-même. Tout au long de l'histoire, l'assistant aide le héros à franchir les obstacles, à affronter les ennemis et même à vaincre le boss final… tout en restant dans l'ombre. Mais à la fin, lorsque le héros s'apprête à recevoir tous les honneurs, l'assistant réalise que c'est en réalité lui qui a tout accompli. Son objectif devient alors de prendre la place du héros et de devenir, enfin, le centre de l'histoire. Le jeu propose une narration ironique et cyclique : chaque partie se termine par un changement de rôle, où l'assistant devient le héros, et un nouveau personnage secondaire vient le suivre.

## Technologies utilisées

- **Python 3.8+**
- **Arcade 2.6.17** - Bibliothèque de jeu 2D moderne avec OpenGL
- **Pymunk 6.5.2** - Moteur physique pour les collisions avancées

## Installation

1. Installer Python 3.8 ou plus récent
2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

## Lancement du jeu

```bash
python main.py
```

## Contrôles

- **Flèches gauche/droite** : Déplacer l'assistant
- **Espace** : Sauter
- **A** : Aider le héros (mécanique principale)

## Structure du projet

```
GameJam/
├── main.py                 # Point d'entrée du jeu
├── requirements.txt        # Dépendances Python
├── scenes/                 # Scènes du jeu
│   ├── game_scene.py      # Scène principale
│   └── __init__.py
├── entities/              # Entités du jeu
│   ├── assistant.py       # L'assistant (joueur)
│   ├── hero.py           # Le héros
│   └── __init__.py
├── utils/                 # Utilitaires
│   ├── constants.py       # Constantes du jeu
│   └── __init__.py
└── assets/               # Ressources (à créer)
    ├── sprites/
    ├── sounds/
    └── fonts/
```

## Équipe de développement

- [Noms des 5 développeurs à ajouter]

## Plan de développement

### Mardi
- **8h30-12h** : Setup projet + mécaniques de base
- **12h** : Deadline 1 - Pitch finalisé
- **17h** : Nom du jeu déterminé
- **Soir** : Premiers visuels

### Mercredi
- **Journée** : Développement des mécaniques avancées
- **16h30** : Affiche + jeu quasi final

### Jeudi
- **Matin** : Finalisation
- **Midi** : Vidéo 30s + jeu final
- **Après-midi** : Tests et présentations