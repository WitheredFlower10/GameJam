# Paramètres de l'écran
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Agent de Missions"

# Paramètres du joueur (Agent)
AGENT_MOVEMENT_SPEED = 5
AGENT_SCALE = 1.0
AGENT_SCALING = 1.0

# Paramètres du vaisseau
SHIP_WIDTH = SCREEN_WIDTH
SHIP_HEIGHT = SCREEN_HEIGHT
SHIP_SECTIONS = 3  # Avant, Centre, Arrière

# Paramètres de l'écran de surveillance
SURVEILLANCE_SCREEN_WIDTH = 400
SURVEILLANCE_SCREEN_HEIGHT = 300
SURVEILLANCE_SCREEN_X = 50
SURVEILLANCE_SCREEN_Y = 200

# Paramètres des missions
MISSION_DURATION = 60  # secondes
HERO_HEALTH_MAX = 100
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
HERO_STATE_TRAVELING = "traveling"
HERO_STATE_FIGHTING = "fighting"
HERO_STATE_RESTING = "resting"
HERO_STATE_COMPLETED = "completed"
HERO_STATE_FAILED = "failed"