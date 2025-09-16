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
        self.surveillance_was_displayed = False
        
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
        
        # Ne pas démarrer de mission automatiquement
        # La mission sera assignée via les interactions
    
    def on_draw(self):
        self.clear()
        
        # Dessiner le vaisseau et l'agent
        self.camera.use()
        self.ship.draw()
        self.ship.draw_interaction_points()
        
        # Dessiner les sprites
        self.agent_list.draw()
        
        # Dessiner l'écran de surveillance seulement si une mission est active
        if self.mission_system.current_mission:
            self.surveillance_screen.draw()
            # Marquer que l'écran était affiché
            self.surveillance_was_displayed = True
        else:
            # L'écran n'est plus affiché - la mission est terminée
            if hasattr(self, 'surveillance_was_displayed') and self.surveillance_was_displayed:
                self.surveillance_was_displayed = False
                # La mission est terminée, calculer le résultat du pari
                if (self.mission_system.bet_placed and not self.mission_system.bet_result):
                    self.mission_system.calculate_bet_result()
                    print("Résultat du pari calculé - Écran de surveillance fermé !")
        
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
        else:
            arcade.draw_text("Aucune mission active", 
                            10, SCREEN_HEIGHT - 90, arcade.color.GRAY, 16)
            arcade.draw_text("Allez au Bureau des Missions pour assigner une quête", 
                            10, SCREEN_HEIGHT - 110, arcade.color.LIGHT_GRAY, 14)
        
        # Contrôles
        arcade.draw_text("FLÈCHES: Se déplacer | ESPACE: Interagir", 
                        10, 30, arcade.color.WHITE, 14)
        
        # Information sur la mission de bataille
        if (self.hero and self.hero.battle_mission and 
            self.hero.battle_mission.is_active):
            arcade.draw_text("MISSION DE BATAILLE EN COURS", 
                            10, 50, arcade.color.YELLOW, 14)
        
        # Interface de paris
        if self.mission_system.betting_active:
            self.draw_betting_interface()
        
        # Résultat de pari
        if self.mission_system.bet_result:
            arcade.draw_text(self.mission_system.bet_result, 
                            SCREEN_WIDTH // 2, 100, arcade.color.GOLD, 18,
                            anchor_x="center")
        
        # Bouton retour au menu
        arcade.draw_text("ÉCHAP: Retour au menu", 
                        SCREEN_WIDTH - 200, 30, arcade.color.LIGHT_GRAY, 12)
    
    def draw_betting_interface(self):
        # Interface de paris en overlay
        betting_info = self.mission_system.get_betting_info()
        if not betting_info:
            return
        
        # Fond semi-transparent
        arcade.draw_lrbt_rectangle_filled(
            0, SCREEN_WIDTH, 0, SCREEN_HEIGHT,
            (0, 0, 0, 150)
        )
        
        # Titre
        arcade.draw_text(
            "STATION DE PARIS",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100,
            arcade.color.GOLD, 32, anchor_x="center", bold=True
        )
        
        # Informations de la mission
        arcade.draw_text(
            f"Mission: {betting_info['mission_name']}",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150,
            arcade.color.WHITE, 20, anchor_x="center"
        )
        
        # Statistiques du héros
        arcade.draw_text(
            f"Progression: {betting_info['mission_progress']:.1f}%",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 180,
            arcade.color.LIGHT_BLUE, 16, anchor_x="center"
        )
        
        arcade.draw_text(
            f"Vie: {betting_info['hero_health']:.1f}%",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 200,
            arcade.color.GREEN, 16, anchor_x="center"
        )
        
        arcade.draw_text(
            f"Endurance: {betting_info['hero_stamina']:.1f}%",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 220,
            arcade.color.BLUE, 16, anchor_x="center"
        )
        
        # Options de pari
        arcade.draw_text(
            "Sur quoi voulez-vous parier ?",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 280,
            arcade.color.WHITE, 18, anchor_x="center"
        )
        
        # Boutons de pari
        arcade.draw_text(
            "1 - RÉUSSITE de la mission (x2 gains)",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 320,
            arcade.color.GREEN, 16, anchor_x="center"
        )
        
        arcade.draw_text(
            "2 - ÉCHEC de la mission (x2 gains)",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 350,
            arcade.color.RED, 16, anchor_x="center"
        )
        
        arcade.draw_text(
            "3 - Annuler",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 380,
            arcade.color.GRAY, 16, anchor_x="center"
        )
        
        # Instructions
        arcade.draw_text(
            "Appuyez sur 1, 2 ou 3 pour choisir",
            SCREEN_WIDTH // 2, 100,
            arcade.color.LIGHT_GRAY, 14, anchor_x="center"
        )
    
    def draw_bet_result(self):
        # Afficher le résultat détaillé du pari
        bet_result = self.mission_system.bet_result
        if not bet_result:
            return
        
        # Fond semi-transparent
        arcade.draw_lrbt_rectangle_filled(
            0, SCREEN_WIDTH, 0, SCREEN_HEIGHT,
            (0, 0, 0, 200)
        )
        
        # Couleur selon le résultat
        if bet_result['won']:
            title_color = arcade.color.GREEN
            border_color = arcade.color.LIGHT_GREEN
        else:
            title_color = arcade.color.RED
            border_color = arcade.color.LIGHT_RED
        
        # Titre principal
        arcade.draw_text(
            "RÉSULTAT DU PARI",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150,
            title_color, 36, anchor_x="center", bold=True
        )
        
        # Bordure décorative
        arcade.draw_lrbt_rectangle_outline(
            SCREEN_WIDTH // 2 - 300, SCREEN_WIDTH // 2 + 300,
            SCREEN_HEIGHT // 2 - 200, SCREEN_HEIGHT // 2 + 200,
            border_color, 4
        )
        
        # Message détaillé (ligne par ligne)
        message_lines = bet_result['message'].split('\n')
        start_y = SCREEN_HEIGHT // 2 + 100
        
        for i, line in enumerate(message_lines):
            color = title_color if i == 0 else arcade.color.WHITE
            size = 24 if i == 0 else 18
            
            arcade.draw_text(
                line,
                SCREEN_WIDTH // 2, start_y - (i * 40),
                color, size, anchor_x="center"
            )
        
        # Informations supplémentaires
        arcade.draw_text(
            f"Montant du pari: {bet_result['bet_amount']} crédits",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50,
            arcade.color.LIGHT_GRAY, 16, anchor_x="center"
        )
        
        # Instructions pour continuer
        arcade.draw_text(
            "Appuyez sur ESPACE pour continuer",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 150,
            arcade.color.LIGHT_GRAY, 14, anchor_x="center"
        )
    
    def handle_betting_input(self, key):
        # Gérer les entrées pour l'interface de paris
        if key == arcade.key.KEY_1:
            # Parier sur la réussite
            result = self.mission_system.place_bet("success", 100)  # 100 crédits par défaut
            print(result)
        elif key == arcade.key.KEY_2:
            # Parier sur l'échec
            result = self.mission_system.place_bet("failure", 100)  # 100 crédits par défaut
            print(result)
        elif key == arcade.key.KEY_3:
            # Annuler
            self.mission_system.close_betting_interface()
            print("Pari annulé.")
    
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
            
            # Debug: Vérifier l'état de la MISSION PRINCIPALE DU HÉROS
            if self.mission_system.bet_placed and not self.mission_system.bet_result:
                print(f"Debug - Pari placé: {self.mission_system.bet_placed}")
                print(f"Debug - Résultat du pari: {self.mission_system.bet_result}")
                print(f"Debug - Mission principale assignée: {self.mission_system.current_mission is not None}")
                if self.hero and self.hero.battle_mission:
                    print(f"Debug - Mission principale du héros active: {self.hero.battle_mission.is_active}")
                    print(f"Debug - Mission principale du héros terminée: {self.hero.battle_mission.mission_completed}")
                    print(f"Debug - Ennemis détruits par le héros: {self.hero.battle_mission.enemies_destroyed}")
                print(f"Debug - Mission principale finie: {self.mission_system.is_mission_finished()}")
            
            # Calculer le résultat du pari quand la mission de bataille se termine
            if (self.mission_system.bet_placed and 
                not self.mission_system.bet_result and
                self.hero and self.hero.battle_mission and
                not self.hero.battle_mission.is_active):
                # La mission de bataille (mission principale du héros) est terminée
                self.mission_system.calculate_bet_result()
                print("Résultat du pari calculé - Mission de bataille terminée !")
            
            # Détection alternative: vérifier si la mission est terminée
            elif (self.mission_system.bet_placed and 
                  not self.mission_system.bet_result and
                  self.hero and self.hero.battle_mission and
                  self.hero.battle_mission.is_mission_finished()):
                # La mission de bataille est terminée
                self.mission_system.calculate_bet_result()
                print("Résultat du pari calculé - Mission terminée (détection alternative) !")
            
            # Détection par l'écran de surveillance: si l'écran n'est plus affiché
            elif (self.mission_system.bet_placed and 
                  not self.mission_system.bet_result and
                  not self.mission_system.current_mission and
                  hasattr(self, 'surveillance_was_displayed') and 
                  self.surveillance_was_displayed):
                # L'écran de surveillance s'est fermé - la mission est terminée
                self.mission_system.calculate_bet_result()
                print("Résultat du pari calculé - Écran de surveillance fermé (détection update) !")
    
    def update_ship_section(self):
        # Déterminer la section du vaisseau selon la position de l'agent
        if self.agent.center_x < SCREEN_WIDTH // 3:
            self.current_ship_section = 0  # Avant
        elif self.agent.center_x < 2 * SCREEN_WIDTH // 3:
            self.current_ship_section = 1  # Centre
        else:
            self.current_ship_section = 2  # Arrière
    
    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            # Retour au menu
            from scenes.menu_scene import MenuScene
            menu_scene = MenuScene()
            self.window.show_view(menu_scene)
        elif self.mission_system.betting_active:
            # Gérer l'interface de paris
            self.handle_betting_input(key)
        elif self.mission_system.bet_result and key == arcade.key.SPACE:
            # Fermer le résultat du pari
            self.mission_system.bet_result = None
            self.mission_system.bet_placed = False
            print("Résultat du pari fermé.")
        elif self.game_state == GAME_STATE_PLAYING:
            # Transmettre les contrôles à l'agent seulement
            self.agent.on_key_press(key, modifiers)
    
    def on_key_release(self, key, modifiers):
        if self.game_state == GAME_STATE_PLAYING:
            # Transmettre les contrôles à l'agent seulement
            self.agent.on_key_release(key, modifiers)
