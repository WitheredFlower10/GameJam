# Paramètres de l'écran
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Agent de Missions"

# Paramètres du joueur (Agent)
AGENT_MOVEMENT_SPEED = 5
AGENT_SCALE = 1.4
AGENT_SCALING = 1.0

# Paramètres du vaisseau
SHIP_WIDTH = SCREEN_WIDTH
SHIP_HEIGHT = SCREEN_HEIGHT
SHIP_SECTIONS = 3  # Avant, Centre, Arrière

# Paramètres de l'écran de surveillance
SURVEILLANCE_SCREEN_WIDTH = 700
SURVEILLANCE_SCREEN_HEIGHT = 400
SURVEILLANCE_SCREEN_X = 50
SURVEILLANCE_SCREEN_Y = 200

# Paramètres des missions
MISSION_DURATION = 60  # secondes
HERO_HEALTH_MAX = 200  # Augmenté pour des batailles plus longues
HERO_STAMINA_MAX = 100

# Couleurs
BACKGROUND_COLOR = (20, 25, 40)      # Bleu foncé spatial
SHIP_COLOR = (40, 45, 60)           # Gris métallique
SCREEN_COLOR = (0, 0, 0)            # Noir pour l'écran
AGENT_COLOR = (100, 150, 200)       # Bleu clair
INTERACTION_COLOR = (255, 100, 100) # Rouge pour les points d'interaction
HERO_COLOR = (255, 215, 0)          # Or pour le héros
ENEMY_COLOR = (200, 50, 50)         # Rouge pour les ennemis

# États du jeu
GAME_STATE_MENU = "menu"
GAME_STATE_PLAYING = "playing"
GAME_STATE_MISSION_ACTIVE = "mission_active"

# États de l'agent
AGENT_STATE_IDLE = "idle"
AGENT_STATE_MOVING = "moving"
AGENT_STATE_INTERACTING = "interacting"

# États du héros
HERO_STATE_WAITING_FOR_MISSION = "waiting_for_mission"
HERO_STATE_FIGHTING = "fighting"
HERO_STATE_COMPLETED = "completed"
HERO_STATE_FAILED = "failed"

# Paramètres des étoiles pour le fond spatial
STAR_COUNT = 200  # Nombre d'étoiles dans le fond
STAR_MIN_SIZE = 1  # Taille minimale des étoiles
STAR_MAX_SIZE = 3  # Taille maximale des étoiles
STAR_COLORS = [
    (255, 255, 255),  # Blanc
    (255, 255, 200),  # Blanc jaunâtre
    (200, 200, 255),  # Blanc bleuté
    (255, 200, 200),  # Blanc rosâtre
]  # Différentes couleurs d'étoiles

# Crédits initiaux du joueur
CREDIT_INITIAL = 20

# --- Constantes de Bataille Galactique ---
PLAYER_SCALING = 0.5
ENEMY_SCALING = 0.5
BULLET_SCALING = 0.3
EXPLOSION_SCALING = 0.6
ENEMY_SPEED = 2
BULLET_SPEED = 5
SPAWN_INTERVAL = 0.8  # secondes entre spawn d'ennemis
GAME_DURATION = 20     # durée minimale en secondes