# Agent de Missions

## Pitch du Jeu

Vous êtes… l'agent de missions.

Votre rôle ? Distribuer des objectifs préétablis aux héros galactiques de passage, puis retourner à vos vraies responsabilités : classer les dossiers numériques, tamponner des autorisations, calibrer des drones de surveillance… Pendant que, quelque part dans l'espace, la véritable bataille se joue à coups de lasers, de robots et d'explosions spatiales.

Parfois, entre deux piles de paperasse futuriste, vous pouvez jeter un œil grâce à une caméra orbitale : vaisseaux qui s'affrontent, stations qui explosent, légendes interstellaires en train de s'écrire… Mais jamais de votre main. Vous n'êtes qu'un rouage secondaire, un spectateur de la guerre.

Votre objectif : remplir vos tâches administratives pour avoir le temps d'espionner — de loin — les exploits des véritables héros.

## Mécaniques de Jeu

### Rôle du Joueur
- **Agent de missions** : Vous distribuez des quêtes aux héros
- **Administrateur** : Vous gérez des tâches administratives dans votre vaisseau
- **Spectateur** : Vous observez les exploits des héros sur un écran de surveillance

### Navigation
- **Mouvement** : Flèches gauche/droite pour se déplacer dans le vaisseau
- **Sections** : Avant (missions), Centre (surveillance), Arrière (paris/analyse)
- **Interactions** : Espace pour interagir avec les points d'intérêt

### Système de Missions
- **Distribution** : Donner des missions aux héros depuis le bureau des missions
- **Surveillance** : Observer la progression du héros en temps réel
- **Résultats** : Les héros peuvent réussir, échouer ou abandonner

### Mini-Quêtes
- **Amélioration surveillance** : Améliorer la qualité de l'écran de surveillance
- **Station de paris** : Parier sur la réussite/échec des héros
- **Analyse de données** : Obtenir des informations détaillées sur les héros

## Architecture Technique

### Structure du Projet
```
GameJam/
├── main.py                 # Point d'entrée du jeu
├── scenes/
│   └── main_scene.py       # Scène principale du jeu
├── entities/
│   ├── agent.py           # Personnage du joueur
│   ├── hero.py            # Héros contrôlé par l'IA
│   ├── ship.py            # Vaisseau et points d'interaction
│   ├── mission_system.py  # Système de gestion des missions
│   └── surveillance_screen.py # Écran de surveillance
├── utils/
│   └── constants.py       # Constantes du jeu
└── README.md
```

### Technologies
- **Arcade** : Framework 2D pour Python
- **Architecture orientée entités** : Chaque élément du jeu est une entité
- **Système de scènes** : Gestion des différentes vues du jeu

## Installation et Lancement

### Prérequis
- Python 3.7+
- Arcade 2.6+

### Installation
```bash
pip install arcade
```

### Lancement
```bash
python main.py
```

## Contrôles

- **Flèches gauche/droite** : Se déplacer dans le vaisseau
- **Espace** : Interagir avec les points d'intérêt
- **Échap** : Quitter le jeu

## Développement

### Prochaines Fonctionnalités
- [ ] Système de paris plus avancé
- [ ] Plus de types de missions
- [ ] Améliorations visuelles
- [ ] Système de progression du joueur
- [ ] Événements aléatoires
- [ ] Interface utilisateur améliorée

### Contribution
Ce projet est développé pour une game jam de 2.5 jours avec une équipe de 5 personnes.