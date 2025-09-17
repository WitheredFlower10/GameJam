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
        self.current_ship_section = 1
        self.surveillance_was_displayed = False
        
        # Image de fond
        self.background_texture = None
        self.background_width = SCREEN_WIDTH  # Sera mis à jour selon la taille de l'image
        
        # Système de défilement
        self.camera_x = 0  # Position de la caméra
        self.world_width = SCREEN_WIDTH * 3  # Largeur du monde (3 écrans par défaut)
        
        self.setup()
    
    def setup(self):
        # Initialiser les SpriteLists
        self.agent_list = arcade.SpriteList()
        self.hero_list = arcade.SpriteList()
        
        # Initialiser les entités
        self.agent = Agent()
        # Positionner l'agent au centre du monde (sera ajusté après chargement du background)
        self.agent.center_x = self.world_width // 2
        self.agent.center_y = SCREEN_HEIGHT // 2  # Centre de l'écran verticalement
        self.agent_list.append(self.agent)
        
        self.hero = Hero()
        self.hero_list.append(self.hero)
        
        self.ship = Ship()
        self.mission_system = MissionSystem()
        self.surveillance_screen = SurveillanceScreen()
        
        # Configurer les caméras
        self.camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()
        
        # Initialiser la position de la caméra
        self.update_camera_initial()
        
        # Lier les systèmes
        self.mission_system.set_hero(self.hero)
        self.surveillance_screen.set_hero(self.hero)
        self.agent.set_mission_system(self.mission_system)
        self.agent.set_world_width(self.world_width)
        
        # Passer les points d'interaction du vaisseau au système de missions
        self.mission_system.set_ship_interaction_points(self.ship.get_interaction_points())
        
        # Charger l'image de fond (optionnelle)
        try:
            self.background_texture = arcade.load_texture("assets/background.png")
            # Mettre à jour la largeur du monde selon la taille de l'image
            if self.background_texture:
                self.background_width = self.background_texture.width
                # Le monde fait exactement la même largeur que le background
                self.world_width = self.background_width
                # Mettre à jour la largeur du monde de l'agent
                self.agent.set_world_width(self.world_width)
                # Repositionner l'agent au début du monde pour test
                self.agent.center_x = SCREEN_WIDTH // 2  # Commencer visible
                # Mettre à jour immédiatement la caméra
                self.update_camera_initial()
                print(f"Background chargé: {self.background_width}px de large, monde: {self.world_width}px")
        except FileNotFoundError:
            print("Image de fond 'assets/background.png' non trouvée, utilisation de la couleur par défaut")
            self.background_texture = None
        
        # Couleur d'arrière-plan (si pas d'image)
        if not self.background_texture:
            arcade.set_background_color(SHIP_COLOR)
        
        # Ne pas démarrer de mission automatiquement
        # La mission sera assignée via les interactions
    
    def on_draw(self):
        self.clear()
        
        # Utiliser la caméra pour le monde
        self.camera.use()
        
        # Dessiner l'image de fond si disponible avec défilement
        if self.background_texture:
            # Le background fait exactement la largeur du monde
            # Position du background : il commence à x=0 dans les coordonnées du monde
            bg_x = 0  # Position fixe dans le monde
            
            # Calculer la hauteur du background en gardant les proportions
            bg_ratio = self.background_texture.height / self.background_texture.width
            bg_height = self.background_width * bg_ratio
            
            # Si l'image est plus petite que l'écran, l'étirer à la hauteur de l'écran
            if bg_height < SCREEN_HEIGHT:
                bg_height = SCREEN_HEIGHT
                
            # Centrer verticalement
            bg_y = (SCREEN_HEIGHT - bg_height) // 2
            
            # Dessiner l'image
            arcade.draw_texture_rect(
                self.background_texture,
                arcade.LBWH(bg_x, bg_y, self.background_width, bg_height)
            )
        
        # Dessiner le vaisseau et l'agent
        self.ship.draw()
        self.ship.draw_interaction_points()
        
        # Dessiner les sprites (agent au-dessus de tout)
        self.agent_list.draw()
        
        # Debug: Voir l'agent et le centrage (dans les coordonnées du monde)
        if self.agent:
            # Cercle rouge autour de l'agent pour le voir
            arcade.draw_circle_outline(
                self.agent.center_x, self.agent.center_y, 50, 
                arcade.color.RED, 4
            )
            # Croix au centre de l'écran (en coordonnées du monde)
            screen_center_x = self.camera_x + SCREEN_WIDTH // 2
            arcade.draw_line(
                screen_center_x - 30, SCREEN_HEIGHT // 2,
                screen_center_x + 30, SCREEN_HEIGHT // 2,
                arcade.color.YELLOW, 4
            )
            arcade.draw_line(
                screen_center_x, SCREEN_HEIGHT // 2 - 30,
                screen_center_x, SCREEN_HEIGHT // 2 + 30,
                arcade.color.YELLOW, 4
            )
        
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
        if getattr(self, '_floating_message', None):
            msg = self._floating_message
            arcade.draw_text(msg['text'], SCREEN_WIDTH//2, msg['y'], msg['color'], 20, anchor_x="center", anchor_y="center")

        # Interface utilisateur
        self.gui_camera.use()
        self.draw_ui()
    
    def draw_ui(self):
        # Titre
        arcade.draw_text("Agent de Missions", 10, SCREEN_HEIGHT - 30, 
                        arcade.color.WHITE, 24, bold=True)
        
        # Or en haut à droite
        gold_text = f"Or: {self.mission_system.gold}"
        arcade.draw_text(gold_text, SCREEN_WIDTH - 10, SCREEN_HEIGHT - 30,
                         arcade.color.GOLD, 18, anchor_x="right", bold=True)
        
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
        
        # Debug info
        if self.agent:
            arcade.draw_text(f"Agent: ({self.agent.center_x:.0f}, {self.agent.center_y:.0f})", 
                           10, SCREEN_HEIGHT - 140, arcade.color.WHITE, 16)
            arcade.draw_text(f"Camera: {self.camera_x:.0f}", 
                           10, SCREEN_HEIGHT - 160, arcade.color.WHITE, 16)
            arcade.draw_text(f"Centre écran: {self.camera_x + SCREEN_WIDTH // 2:.0f}", 
                           10, SCREEN_HEIGHT - 180, arcade.color.YELLOW, 16)
            arcade.draw_text(f"Fenêtre: {SCREEN_WIDTH}x{SCREEN_HEIGHT}", 
                           10, SCREEN_HEIGHT - 200, arcade.color.LIGHT_BLUE, 16)
            arcade.draw_text(f"Monde: {self.world_width}px", 
                           10, SCREEN_HEIGHT - 220, arcade.color.LIGHT_GREEN, 16)
    
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
        
        # Panneau central
        panel_left = SCREEN_WIDTH // 2 - 320
        panel_right = SCREEN_WIDTH // 2 + 320
        panel_bottom = SCREEN_HEIGHT // 2 - 220
        panel_top = SCREEN_HEIGHT // 2 + 220
        arcade.draw_lrbt_rectangle_filled(panel_left, panel_right, panel_bottom, panel_top, (20, 20, 30, 230))
        arcade.draw_lrbt_rectangle_outline(panel_left, panel_right, panel_bottom, panel_top, arcade.color.GOLD, 3)
        
        # Titre
        arcade.draw_text(
            "STATION DE PARIS",
            SCREEN_WIDTH // 2, panel_top - 40,
            arcade.color.GOLD, 32, anchor_x="center", bold=True
        )
        
        # Informations de la mission
        arcade.draw_text(
            f"Mission: {betting_info['mission_name']}",
            SCREEN_WIDTH // 2, panel_top - 90,
            arcade.color.WHITE, 20, anchor_x="center"
        )
        
        # Statistiques du héros
        arcade.draw_text(
            f"Progression: {betting_info['mission_progress']:.1f}%",
            SCREEN_WIDTH // 2, panel_top - 120,
            arcade.color.LIGHT_BLUE, 16, anchor_x="center"
        )
        
        arcade.draw_text(
            f"Vie: {betting_info['hero_health']:.1f}%",
            SCREEN_WIDTH // 2, panel_top - 140,
            arcade.color.GREEN, 16, anchor_x="center"
        )
        
        # Options de pari
        arcade.draw_text(
            "Sur quoi voulez-vous parier ?",
            SCREEN_WIDTH // 2, panel_top - 200,
            arcade.color.WHITE, 18, anchor_x="center"
        )
        
        # Boutons de pari
        arcade.draw_text(
            "1 - RÉUSSITE de la mission (x2)",
            SCREEN_WIDTH // 2, panel_top - 240,
            arcade.color.GREEN, 16, anchor_x="center"
        )
        
        arcade.draw_text(
            "2 - ÉCHEC de la mission (x2)",
            SCREEN_WIDTH // 2, panel_top - 270,
            arcade.color.RED, 16, anchor_x="center"
        )
        
        arcade.draw_text(
            "3 - Annuler",
            SCREEN_WIDTH // 2, panel_top - 300,
            arcade.color.GRAY, 16, anchor_x="center"
        )
        
        # Sélection courante
        sel = betting_info['temp_bet_type'] or "—"
        arcade.draw_text(
            f"Sélection: {sel}",
            SCREEN_WIDTH // 2, panel_bottom + 120,
            arcade.color.WHITE, 18, anchor_x="center"
        )
        
        # Montant à parier + contrôles
        arcade.draw_text(
            f"Montant: {betting_info['temp_bet_amount']} (←/→ pour ajuster)",
            SCREEN_WIDTH // 2, panel_bottom + 90,
            arcade.color.GOLD, 18, anchor_x="center"
        )
        
        # Solde
        arcade.draw_text(
            f"Solde: {betting_info['gold']}",
            SCREEN_WIDTH // 2, panel_bottom + 60,
            arcade.color.LIGHT_GRAY, 16, anchor_x="center"
        )
        
        # Validation
        arcade.draw_text(
            "ENTRÉE - Valider le pari",
            SCREEN_WIDTH // 2, panel_bottom + 30,
            arcade.color.LIGHT_GREEN, 16, anchor_x="center"
        )
        
        # Aide
        arcade.draw_text(
            "1=Succès  2=Échec  3=Annuler  ←/→=Montant  Entrée=OK",
            SCREEN_WIDTH // 2, panel_bottom + 10,
            arcade.color.LIGHT_GRAY, 12, anchor_x="center"
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
        info = self.mission_system.get_betting_info()
        if not info:
            return
        
        if key == arcade.key.KEY_1:
            self.mission_system.temp_bet_type = "success"
        elif key == arcade.key.KEY_2:
            self.mission_system.temp_bet_type = "failure"
        elif key == arcade.key.LEFT:
            self.mission_system.temp_bet_amount = max(0, self.mission_system.temp_bet_amount - 10)
        elif key == arcade.key.RIGHT:
            self.mission_system.temp_bet_amount = min(self.mission_system.gold, self.mission_system.temp_bet_amount + 10)
        elif key == arcade.key.ENTER or key == arcade.key.RETURN:
            if not self.mission_system.temp_bet_type:
                print("Choisissez d'abord Succès (1) ou Échec (2)")
                return
            amount = self.mission_system.temp_bet_amount
            result = self.mission_system.place_bet(self.mission_system.temp_bet_type, amount)
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
            
            # Mettre à jour la position de la caméra
            self.update_camera()
            
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

            if getattr(self, '_floating_message', None):
              msg = self._floating_message
              msg['y'] += 1  # bouge vers le haut
              msg['frames'] += 1
              if msg['frames'] > 120: # dure 2 seconde 
                  self._floating_message = None
    
    def update_camera(self):
        # Calculer où devrait être la caméra pour centrer l'agent
        target_camera_x = self.agent.center_x - SCREEN_WIDTH // 2
        
        # Limites de la caméra (ne pas dépasser les bords du monde)
        min_camera_x = 0
        max_camera_x = max(0, self.world_width - SCREEN_WIDTH)
        
        # Appliquer les limites
        self.camera_x = max(min_camera_x, min(max_camera_x, target_camera_x))
        
        # Debug info (temporaire)
        if hasattr(self, '_debug_counter'):
            self._debug_counter += 1
        else:
            self._debug_counter = 0
            
        if self._debug_counter % 60 == 0:  # Print every second
            print(f"Debug - Agent: ({self.agent.center_x:.1f}, {self.agent.center_y:.1f})")
            print(f"Debug - Camera: {self.camera_x:.1f}, World: {self.world_width}, Screen: {SCREEN_WIDTH}")
        
        # Appliquer la position de la caméra
        self.camera.position = (self.camera_x, 0)
    
    def update_camera_initial(self):
        # Forcer la mise à jour initiale de la caméra pour centrer sur l'agent
        target_camera_x = self.agent.center_x - SCREEN_WIDTH // 2
        min_camera_x = 0
        max_camera_x = max(0, self.world_width - SCREEN_WIDTH)
        self.camera_x = max(min_camera_x, min(max_camera_x, target_camera_x))
        self.camera.position = (self.camera_x, 0)
        print(f"Caméra initialisée: agent à ({self.agent.center_x}, {self.agent.center_y}), caméra à {self.camera_x}")
    
    def update_ship_section(self):
        # Déterminer la section du vaisseau selon la position de l'agent dans le monde
        world_section_width = self.world_width // 3
        
        if self.agent.center_x < world_section_width:
            self.current_ship_section = 0  # Avant
        elif self.agent.center_x < 2 * world_section_width:
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

def trigger_repair_screen(self):
        def on_finish(success):
            self.window.show_view(self)
            if success:
                self.show_floating_message("Écran connecté avec succès !", arcade.color.GREEN)
            else:
                self.show_floating_message("Connexion échouée !", arcade.color.RED)
        self._floating_message = None
        self.window.show_view(RepairScreenGame(on_finish_callback=on_finish))

def show_floating_message(self, text, color):
        self._floating_message = {
            'text': text,
            'color': color,
            'y': 100,
            'frames': 0
        }

#dans on_draw() methode, pour afficher le floating message
    
#dans on_update() methode, pour mettre a jour le floating message
 