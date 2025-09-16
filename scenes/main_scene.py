import arcade
from utils.constants import *
from entities.agent import Agent
from entities.hero import Hero
from entities.ship import Ship
from entities.mission_system import MissionSystem
from entities.surveillance_screen import SurveillanceScreen


class MainScene(arcade.View):
    
    def __init__(self):
        super().__init__()
        
        # Entités principales
        self.agent = None
        self.hero = None
        self.ship = None
        self.mission_system = None
        self.surveillance_screen = None
        
        # SpriteLists pour le dessin
        self.agent_list = None
        self.hero_list = None
        
        # Caméras
        self.camera = None
        self.gui_camera = None
        
        # État du jeu
        self.game_state = GAME_STATE_PLAYING
        self.current_ship_section = 1  # 0=Avant, 1=Centre, 2=Arrière
        
        self.setup()
    
    def setup(self):
        # Initialiser les SpriteLists
        self.agent_list = arcade.SpriteList()
        self.hero_list = arcade.SpriteList()
        
        # Initialiser les entités
        self.agent = Agent()
        self.agent.center_x = SCREEN_WIDTH // 2
        self.agent.center_y = 100
        self.agent_list.append(self.agent)
        
        self.hero = Hero()
        self.hero_list.append(self.hero)
        
        self.ship = Ship()
        self.mission_system = MissionSystem()
        self.surveillance_screen = SurveillanceScreen()
        
        # Configurer les caméras
        self.camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()
        
        # Lier les systèmes
        self.mission_system.set_hero(self.hero)
        self.surveillance_screen.set_hero(self.hero)
        self.agent.set_mission_system(self.mission_system)
        
        # Passer les points d'interaction du vaisseau au système de missions
        self.mission_system.set_ship_interaction_points(self.ship.get_interaction_points())
        
        # Démarrer une mission automatiquement
        self.mission_system.start_random_mission()
    
    def on_draw(self):
        self.clear()
        
        # Dessiner le vaisseau et l'agent
        self.camera.use()
        self.ship.draw()
        self.ship.draw_interaction_points()
        
        # Dessiner les sprites
        self.agent_list.draw()
        
        # Dessiner l'écran de surveillance
        self.surveillance_screen.draw()
        
        # Interface utilisateur
        self.gui_camera.use()
        self.draw_ui()
    
    def draw_ui(self):
        # Titre
        arcade.draw_text("Agent de Missions", 10, SCREEN_HEIGHT - 30, 
                        arcade.color.WHITE, 24, bold=True)
        
        # Informations sur la section du vaisseau
        section_names = ["Avant", "Centre", "Arrière"]
        arcade.draw_text(f"Section: {section_names[self.current_ship_section]}", 
                        10, SCREEN_HEIGHT - 60, arcade.color.WHITE, 16)
        
        # État de la mission
        if self.mission_system.current_mission:
            mission = self.mission_system.current_mission
            arcade.draw_text(f"Mission: {mission['name']}", 
                            10, SCREEN_HEIGHT - 90, arcade.color.WHITE, 16)
            arcade.draw_text(f"Progression: {mission.get('progress', 0):.1f}%", 
                            10, SCREEN_HEIGHT - 110, arcade.color.WHITE, 16)
        
        # Contrôles
        arcade.draw_text("FLÈCHES: Se déplacer | ESPACE: Interagir", 
                        10, 30, arcade.color.WHITE, 14)
        
        # Information sur la mission de bataille
        if (self.hero and self.hero.battle_mission and 
            self.hero.battle_mission.is_active):
            arcade.draw_text("MISSION DE BATAILLE EN COURS", 
                            10, 50, arcade.color.YELLOW, 14)
    
    def on_update(self, delta_time):
        if self.game_state == GAME_STATE_PLAYING:
            self.agent.update(delta_time)
            self.hero.update(delta_time)
            self.mission_system.update(delta_time)
            self.surveillance_screen.update(delta_time)
            
            # Mettre à jour les SpriteLists
            self.agent_list.update()
            self.hero_list.update()
            
            # Mettre à jour la section du vaisseau selon la position de l'agent
            self.update_ship_section()
    
    def update_ship_section(self):
        # Déterminer la section du vaisseau selon la position de l'agent
        if self.agent.center_x < SCREEN_WIDTH // 3:
            self.current_ship_section = 0  # Avant
        elif self.agent.center_x < 2 * SCREEN_WIDTH // 3:
            self.current_ship_section = 1  # Centre
        else:
            self.current_ship_section = 2  # Arrière
    
    def on_key_press(self, key, modifiers):
        if self.game_state == GAME_STATE_PLAYING:
            # Transmettre les contrôles à l'agent seulement
            self.agent.on_key_press(key, modifiers)
    
    def on_key_release(self, key, modifiers):
        if self.game_state == GAME_STATE_PLAYING:
            # Transmettre les contrôles à l'agent seulement
            self.agent.on_key_release(key, modifiers)
