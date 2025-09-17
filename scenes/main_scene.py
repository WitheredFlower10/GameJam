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
        
        # Monde (dimensions/bornes caméra)
        self.world_width = SCREEN_WIDTH
        self.world_height = SCREEN_HEIGHT
        self.world_left = 0
        self.world_right = self.world_width
        
        # Message flottant (UI)
        self.floating_message = None  # {'text': str, 'color': tuple, 'y': int, 'frames': int}

        # Texture d'arrière-plan (monde)
        self.background_texture = None
        
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
        # Démarrer au centre du monde (x=0)
        self.agent.center_x = 0
        self.agent.center_y = 80  # au bas de l'écran
        self.agent_list.append(self.agent)
        
        self.hero = Hero()
        self.hero_list.append(self.hero)
        
        self.ship = Ship()
        self.mission_system = MissionSystem()
        self.surveillance_screen = SurveillanceScreen()
        
        # Configurer les caméras
        self.camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()
        
        # Déterminer la taille du monde (selon le vaisseau ou une texture de fond)
        self.determine_world_size()
        # Propager les bornes monde centrées (ex: -2000 .. 2000)
        self.agent.world_left = self.world_left
        self.agent.world_right = self.world_right

        # Lier les systèmes
        self.mission_system.set_hero(self.hero)
        self.surveillance_screen.set_hero(self.hero)
        self.agent.set_mission_system(self.mission_system)
        
        # Passer les points d'interaction du vaisseau au système de missions
        self.mission_system.set_ship_interaction_points(self.ship.get_interaction_points())
        
        # Ne pas démarrer de mission automatiquement
        # La mission sera assignée via les interactions
    
    def determine_world_size(self):
        """Détermine la taille du monde pour la caméra.
        Priorité: Ship.world_width/world_height, sinon lecture d'une texture 'background.png'."""
        # Par défaut
        self.world_width = SCREEN_WIDTH
        self.world_height = SCREEN_HEIGHT
        self.world_left = -self.world_width // 2
        self.world_right = self.world_width // 2
        
        # 1) Préférence: attributs sur le vaisseau
        has_ship_world = False
        if hasattr(self.ship, 'world_width') and hasattr(self.ship, 'world_height'):
            try:
                w = int(getattr(self.ship, 'world_width'))
                h = int(getattr(self.ship, 'world_height'))
                if w > 0 and h > 0:
                    self.world_width = w
                    self.world_height = h
                    self.world_left = -w // 2
                    self.world_right = w // 2
                    has_ship_world = True
            except Exception:
                pass
        
        # 2) Sinon: tenter de charger une texture d'arrière-plan
        candidate_paths = []
        # Essayer des chemins potentiels fournis par le Ship
        for attr_name in ('background_texture_path', 'background_path', 'texture_path'):
            if hasattr(self.ship, attr_name):
                path = getattr(self.ship, attr_name)
                if isinstance(path, str):
                    candidate_paths.append(path)
        # Valeurs par défaut
        candidate_paths.extend(['background.png', 'assets/background.png'])
        
        for path in candidate_paths:
            try:
                tex = arcade.load_texture(path)
                if tex and tex.width > 0 and tex.height > 0:
                    self.background_texture = tex
                    # Si aucune taille monde fiable fournie par le vaisseau, utiliser celle de la texture
                    if not has_ship_world:
                        self.world_width = tex.width
                        self.world_height = tex.height
                        self.world_left = -tex.width // 2
                        self.world_right = tex.width // 2
                    return
            except Exception:
                continue
        # Si rien trouvé, on conserve la taille d'écran par défaut
        # Forcer une carte large minimale si désiré (ex: 4000px)
        if self.world_width < 4000:
            self.world_width = 4000
            self.world_left = -2000
            self.world_right = 2000

    def on_draw(self):
        self.clear()
        
        # Dessiner le vaisseau et l'agent
        self.camera.use()
        self.draw_background()
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
        self.draw_floating_message()
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
    
    def draw_floating_message(self):
        # Dessiner un message flottant centré (en coordonnées écran/GUI)
        if not self.floating_message:
            return
        msg = self.floating_message
        arcade.draw_text(
            msg['text'],
            SCREEN_WIDTH // 2,
            msg['y'],
            msg.get('color', arcade.color.WHITE),
            18,
            anchor_x="center",
            bold=True
        )

    def draw_background(self):
        if not hasattr(self, "_bg_ready") or not self._bg_ready:
            try:
                # Si ton Ship expose déjà une texture, récupère-la :
                if hasattr(self.ship, "background_texture"):
                    self._bg_tex = self.ship.background_texture
                elif hasattr(self.ship, "get_background_texture"):
                    self._bg_tex = self.ship.get_background_texture()
                else:
                    self._bg_tex = arcade.load_texture("background.png")
            except Exception:
                self._bg_tex = None

            # Déduis les bornes du monde
            if self._bg_tex is not None:
                self.world_width = getattr(self, "world_width", self._bg_tex.width)
                self.world_height = getattr(self, "world_height", self._bg_tex.height)

            # Prépare un sprite de secours (marche partout)
            if self._bg_tex is not None:
                self._bg_sprite = arcade.Sprite()
                self._bg_sprite.texture = self._bg_tex
                self._bg_sprite.left = 0
                self._bg_sprite.bottom = 0
            else:
                self._bg_sprite = None

            self._bg_ready = True

        # Rien à dessiner ?
        if self._bg_tex is None:
            return

        w, h = self._bg_tex.width, self._bg_tex.height

        # 1) Arcade 2.x : draw_lrwh_rectangle_textured existe
        if hasattr(arcade, "draw_lrwh_rectangle_textured"):
            arcade.draw_lrwh_rectangle_textured(self.world_left, self.world_right, 0, h, self._bg_tex)
            return

        # 2) Arcade 3.x : dessiner le Sprite
        if self._bg_sprite is not None:
            self._bg_sprite.left = self.world_left
            self._bg_sprite.bottom = 0
            self._bg_sprite.draw()


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

            # Mettre à jour le message flottant (animation + durée ~2s)
            if self.floating_message:
                self.floating_message['y'] += 1
                self.floating_message['frames'] = self.floating_message.get('frames', 0) + 1
                # ~2 secondes à 60 FPS
                if self.floating_message['frames'] >= 120:
                    self.floating_message = None
            
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

            # Mettre à jour la caméra APRÈS toutes les mises à jour
            self.update_camera()
    
    def update_ship_section(self):
        # Déterminer la section du vaisseau selon la position de l'agent
        if self.agent.center_x < SCREEN_WIDTH // 3:
            self.current_ship_section = 0  # Avant
        elif self.agent.center_x < 2 * SCREEN_WIDTH // 3:
            self.current_ship_section = 1  # Centre
        else:
            self.current_ship_section = 2  # Arrière
    
    def update_camera(self):
        # Suivi fluide: Camera2D.position représente le CENTRE de la caméra
        half_w = SCREEN_WIDTH / 2
        half_h = SCREEN_HEIGHT / 2

        # Cibler le centre sur l'agent en X
        target_center_x = max(self.world_left + half_w, min(self.world_right - half_w, self.agent.center_x))
        # Verrou vertical: garder le bas du monde (ou sol) aligné avec le bas de l'écran
        target_center_y = half_h

        # Easing vers la cible
        current_x, current_y = self.camera.position
        ease = 0.18
        new_x = current_x + (target_center_x - current_x) * ease
        new_y = current_y + (target_center_y - current_y) * ease
        self.camera.position = (new_x, new_y)
    
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

    # API simple pour déclencher un message flottant depuis d'autres systèmes
    def show_floating_message(self, text, color=arcade.color.WHITE):
        self.floating_message = {
            'text': str(text),
            'color': color,
            'y': SCREEN_HEIGHT // 2,
            'frames': 0,
        }
