import arcade
from utils.constants import *
from entities.agent import Agent
from entities.hero import Hero
from entities.ship import Ship
from entities.mission_system import MissionSystem
from entities.surveillance_screen import SurveillanceScreen
from mini_games.wire_puzzle_overlay import WirePuzzleOverlay
from mini_games.repair_overlay import RepairMinigameOverlay
from scenes.game_over_scene import GameOverScene
from scenes.game_end_scene import GameEndScene

from mini_games.terminal import MainTerminal



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
        
        # SpriteLists pour les collisions
        self.collision_list = None
        
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
        # Décalage vertical du background (positif = vers le haut, négatif = vers le bas)
        self.background_y_offset = 100
        
        # État du jeu
        self.game_state = GAME_STATE_PLAYING
        self.current_ship_section = 1  # 0=Avant, 1=Centre, 2=Arrière
        self.surveillance_was_displayed = False
        self.surveillance_screen_connected = False
        
        # Variables pour le mouvement smooth de l'écran de surveillance
        self.surveillance_target_x = 0
        self.surveillance_target_y = 0
        self.surveillance_smooth_factor = 0.08 # Plus petit = plus smooth (0.05-0.2)

        
        # Dimensions UI adaptatives (initialisées aux valeurs par défaut)
        self.ui_width = SCREEN_WIDTH
        self.ui_height = SCREEN_HEIGHT

        # Terminal principal
        self.terminal = None
        #Son
        self.sound_back = None
        self.sound_enabled = True
        self.background_music_player = None
        self.music_should_loop = True  # Flag pour contrôler la boucle

       

       
        
        self.setup()
    
    def on_text(self, text):
        if self.terminal and hasattr(self.terminal, 'on_text'):
            self.terminal.on_text(text)
            return

    def on_resize_event(self, width, height):
        """Appelé quand la fenêtre change de taille (toggle fullscreen)"""
        print(f"MainScene - Redimensionnement détecté: {width}x{height}")
        
        # Recalculer les éléments UI qui dépendent de la taille d'écran
        # Redimensionner l'écran de surveillance
        if self.surveillance_screen:
            # Adapter la taille de l'écran de surveillance à la nouvelle résolution
            screen_scale = min(width / 1024, height / 768)  # Échelle basée sur 1024x768
            # +20 px (10 à gauche, 10 à droite)
            self.surveillance_screen.screen_width = int(700 * screen_scale) + 20
            self.surveillance_screen.screen_height = int(400 * screen_scale)
            self.surveillance_screen.screen_x = int(50 * screen_scale)
            self.surveillance_screen.screen_y = int(200 * screen_scale)
            print(f"Écran de surveillance redimensionné: {self.surveillance_screen.screen_width}x{self.surveillance_screen.screen_height}")
        
        # Stocker les nouvelles dimensions pour les éléments UI
        self.ui_width = width
        self.ui_height = height
        
        # Recalculer les positions UI relatives
        # Les éléments UI s'adaptent maintenant à la résolution
        print(f"UI adaptée à la résolution: {self.ui_width}x{self.ui_height}")
        
        # Repositionner immédiatement la caméra avec les nouvelles dimensions
        self.repositioner_camera()
        
        # Adapter d'autres éléments UI si nécessaire
        # Le ship et l'agent s'adaptent automatiquement via la caméra
    
    def setup(self):
        # Initialiser les SpriteLists
        self.agent_list = arcade.SpriteList()
        self.hero_list = arcade.SpriteList()
        self.collision_list = arcade.SpriteList()
        self.sound_back = arcade.load_sound("assets/sounds/interstellar.wav")
        self.start_background_music()
        
        # Initialiser les entités
        self.agent = Agent()
        self.agent_list.append(self.agent)
        
        self.hero = Hero()
        self.hero_list.append(self.hero)
        
        self.ship = Ship()
        
        # Ajouter le HeroNPC aux collisions
        if self.ship.hero_npc:
            self.collision_list.append(self.ship.hero_npc)
        self.mission_system = MissionSystem()
        self.surveillance_screen = SurveillanceScreen()
        
        # Configurer les caméras
        self.camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()
        # Zoom fixe (dézoomer un peu la vue). 1.0 = normal, <1 = dézoom
        self.camera_zoom = 0.85
        
        # Déterminer la taille du monde (selon le vaisseau ou une texture de fond)
        self.determine_world_size()
        
        # Positionner l'agent au début du monde (avec les nouvelles coordonnées)
        self.agent.center_x = 2000  # Au milieu
        self.agent.center_y = 200  # Sur le sol du background
        
        # Propager les bornes du monde à l'agent
        self.agent.world_left = self.world_left
        self.agent.world_right = self.world_right

        # Lier les systèmes
        self.mission_system.set_hero(self.hero)
        self.surveillance_screen.set_hero(self.hero)
        # Connecter le MissionSystem à l'écran de surveillance pour révéler la vie après le mini-jeu
        if hasattr(self.surveillance_screen, 'set_mission_system'):
            self.surveillance_screen.set_mission_system(self.mission_system)
        # État de connexion initial: non connecté tant que le mini-jeu n'est pas terminé
        if hasattr(self.surveillance_screen, 'set_connected'):
            self.surveillance_screen.set_connected(False)
        self.agent.set_mission_system(self.mission_system)
        self.agent.set_collision_list(self.collision_list)
        
        # Définir les callbacks pour les scènes de fin de jeu
        def on_game_over():
            """Callback pour la scène de défaite"""
            game_over_scene = GameOverScene()
            self.window.show_view(game_over_scene)
        
        def on_game_end():
            """Callback pour la scène de victoire"""
            game_end_scene = GameEndScene()
            self.window.show_view(game_end_scene)
        
        self.hero.set_game_end_callbacks(on_game_over, on_game_end)
        
        # Passer les points d'interaction du vaisseau au système de missions
        self.mission_system.set_ship_interaction_points(self.ship.get_interaction_points())
        self.mission_system.set_ship(self.ship)



    def start_background_music(self):
        """Démarrer la musique de fond"""
        if self.sound_enabled and self.background_music_player is None:
            try:
                self.background_music_player = self.sound_back.play(loop=self.music_should_loop, volume=0.1)
                print("Musique de fond démarrée")
            except Exception as e:
                print(f"Erreur lecture musique: {e}")

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
        # Valeurs par défaut - priorité à notre background 4000px
        candidate_paths.extend(['assets/background.png', 'background.png'])
        
        for path in candidate_paths:
            try:
                tex = arcade.load_texture(path)
                if tex and tex.width > 0 and tex.height > 0:
                    self.background_texture = tex
                    print(f"Background chargé: {path} ({tex.width}x{tex.height})")
                    
                     # Si aucune taille monde fiable fournie par le vaisseau, utiliser celle de la texture
                    if not has_ship_world:
                         self.world_width = tex.width  # Largeur exacte du background
                         self.world_height = tex.height  # Hauteur exacte du background
                         # Le monde fait exactement la taille du background
                         self.world_left = 0
                         self.world_right = tex.width  # Limite exacte du background
                    return
            except Exception as e:
                print(f"Impossible de charger {path}: {e}")
                continue
                
        # Si rien trouvé, créer un monde de 4000px par défaut
        print("Aucun background trouvé, utilisation d'un monde 4000px")
        w,h = arcade.get_display_size()
        self.world_width = 4000
        self.world_height = h  # Hauteur par défaut adaptée au background
        self.world_left = 0
        self.world_right = 4000  # Limite exacte du monde


    def on_draw(self):
        self.clear()

        # Dessiner le vaisseau et l'agent
        self.camera.use()
        self.draw_star_background()
        self.draw_background()
        self.ship.draw()
        
        # Dessiner le héros NPC
        self.ship.draw_hero_npc(self.mission_system)
        
        # Utiliser la caméra et la taille d'écran pour afficher correctement les flèches
        self.ship.draw_interaction_points(self.camera, self.ui_width, self.ui_height, self.mission_system)

        # Dessiner les sprites
        self.agent_list.draw()

        # Marquer si l'écran de surveillance doit être affiché (le dessin se fait en couche GUI)
        should_draw_surveillance = bool(self.mission_system.current_mission)
        if not should_draw_surveillance:
            # L'écran n'est plus affiché - la mission est terminée
            if hasattr(self, 'surveillance_was_displayed') and self.surveillance_was_displayed:
                self.surveillance_was_displayed = False
                # La mission est terminée, calculer le résultat du pari
                if (self.mission_system.bet_placed and not self.mission_system.bet_result):
                    self.mission_system.calculate_bet_result()
                    print("Résultat du pari calculé - Écran de surveillance fermé !")

        # Interface utilisateur
        self.gui_camera.use()

        # Dessiner l'écran de surveillance en coordonnées écran et le faire suivre l'agent
        # Afficher dès le lancement, même sans mission active (affichera le message d'attente)
        self._update_surveillance_screen_position()
        # Synchroniser les missions du héros avec la position/tailles de l'écran de surveillance
        self._sync_mission_overlay_bounds()
        # Si une mission démarre à cette frame, s'assurer que le contenu apparaît déjà au bon endroit
        self.surveillance_screen.draw()
        if should_draw_surveillance:
            # Marquer que l'écran était affiché (pour la logique de résultat de pari)
            self.surveillance_was_displayed = True

        # Dessiner le Wire Puzzle en overlay s'il est actif
        if hasattr(self, 'wire_overlay') and self.wire_overlay is not None:
            self.wire_overlay.on_draw()
        # Dessiner les mini-jeux de réparation/scanner
        if hasattr(self, 'repair_overlay') and self.repair_overlay is not None:
            self.repair_overlay.on_draw()
        if hasattr(self, 'enemy_scan_overlay') and self.enemy_scan_overlay is not None:
            self.enemy_scan_overlay.on_draw()

        self.draw_floating_message()
        self.draw_ui()

        # Afficher le terminal si initialisé
        if self.terminal:
            # Synchroniser l'état de connexion écran depuis le terminal
            try:
                if hasattr(self.surveillance_screen, 'set_connected'):
                    self.surveillance_screen.set_connected(bool(getattr(self.terminal, 'screen_connected', False)))
            except Exception:
                pass
            self.terminal.on_draw()
            
    
    def draw_ui(self):
        
        # Crédits (encore plus haut, aligné avec les titres)
        x_left = 10
        y_cursor = self.ui_height - 6
        arcade.draw_text(f"Crédits: {self.mission_system.gold}", x_left, y_cursor, arcade.color.GOLD, 18, bold=True)
        y_cursor -= 26

        # Objectifs (tâches de réparation)
        # États
        try:
            repair_health_done = bool(getattr(self.mission_system, 'wire_puzzle_completed', False))
        except Exception:
            repair_health_done = False
        try:
            repair_enemies_done = bool(getattr(self.mission_system, 'enemies_screen_completed', False))
        except Exception:
            repair_enemies_done = False
        try:
            repair_connection_done = bool(
                getattr(self.surveillance_screen, 'connected', False) or getattr(self, 'surveillance_screen_connected', False)
            )
        except Exception:
            repair_connection_done = False
        try:
            missions_completed = int(getattr(self.mission_system, 'missions_completed_success_count', 0))
        except Exception:
            missions_completed = 0

        # Faisabilité
        mission_launched = getattr(self.mission_system, 'missions_launched_count', 0) >= 1
        show_repair_health = mission_launched or repair_health_done  # Disponible dès qu'une mission est lancée
        show_repair_connection = True
        show_repair_enemies = (missions_completed >= 1) or repair_enemies_done

        if show_repair_health or show_repair_connection or show_repair_enemies:
            arcade.draw_text("Objectifs:", x_left, y_cursor, arcade.color.WHITE, 14, bold=True)
            y_cursor -= 20

            def draw_obj(label, done, y):
                icon = "✔" if done else "✖"
                color = arcade.color.LIGHT_GREEN if done else arcade.color.LIGHT_GRAY
                arcade.draw_text(f"{icon} {label}", x_left, y, color, 13)

            if show_repair_health:
                draw_obj("Réparer la santé", repair_health_done, y_cursor)
                y_cursor -= 18
            if show_repair_enemies:
                draw_obj("Réparer le scanner ennemis", repair_enemies_done, y_cursor)
                y_cursor -= 18
            if show_repair_connection:
                draw_obj("Connecter l'écran sur le terminal", repair_connection_done, y_cursor)
                y_cursor -= 26
        
        # État de la mission
        if self.mission_system.current_mission:
            mission = self.mission_system.current_mission
            arcade.draw_text(f"Mission: {mission['name']}", x_left, y_cursor, arcade.color.WHITE, 16)
            y_cursor -= 22
        else:
            arcade.draw_text("Aucune mission active", x_left, y_cursor, arcade.color.WHITE, 16)
            y_cursor -= 22
        
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
                            self.ui_width // 2, 100, arcade.color.GOLD, 18,
                            anchor_x="center")
        
        # Bouton retour au menu
        arcade.draw_text("ÉCHAP: Retour au menu", 
                        self.ui_width - 200, 30, arcade.color.LIGHT_GRAY, 12)

    def draw_star_background(self):
        """Dessine les étoiles en arrière-plan"""
        if hasattr(self.window, 'stars'):
            for star in self.window.stars:
                # Calculer le scintillement
                star['twinkle_phase'] += star['twinkle_speed']
                twinkle_factor = 0.7 + 0.3 * abs(star['twinkle_phase'] % (2 * 3.14159))
                twinkle_alpha = int(star['alpha'] * twinkle_factor)
                
                # S'assurer que l'alpha reste entre 0 et 255
                twinkle_alpha = max(0, min(255, twinkle_alpha))
                
                # Dessiner l'étoile avec la couleur de base et l'alpha calculé
                arcade.draw_circle_filled(
                    star['x'], 
                    star['y'], 
                    star['size'], 
                    (*star['color'], twinkle_alpha)
                )

    def draw_background(self):
        """Dessine le background du monde - méthode forcée pour position absolue"""
        if self.background_texture:
            # Utiliser la méthode la plus directe possible
            try:
                # Essayer draw_scaled_texture_rectangle si disponible
                if hasattr(arcade, "draw_scaled_texture_rectangle"):
                    arcade.draw_scaled_texture_rectangle(
                        self.background_texture.width // 2,  # center_x
                        (self.background_texture.height // 2) + self.background_y_offset,  # center_y avec décalage
                        self.background_texture,
                        1.0,  # scale
                        0     # angle
                    )
                # Sinon draw_texture_rectangle classique
                elif hasattr(arcade, "draw_texture_rectangle"):
                    arcade.draw_texture_rectangle(
                        self.background_texture.width // 2,  # center_x
                        (self.background_texture.height // 2) + self.background_y_offset,  # center_y avec décalage
                        self.background_texture.width,  # width
                        self.background_texture.height,  # height
                        self.background_texture
                    )
                # Méthode lrwh si disponible
                elif hasattr(arcade, "draw_lrwh_rectangle_textured"):
                    arcade.draw_lrwh_rectangle_textured(
                        0, self.background_texture.width,  # left, right
                        0 + self.background_y_offset, self.background_texture.height + self.background_y_offset,  # bottom, top avec décalage
                        self.background_texture
                    )
                else:
                    # Fallback Sprite avec reset forcé
                    self._bg_sprite_list = arcade.SpriteList()  # Reset à chaque frame
                    bg_sprite = arcade.Sprite()
                    bg_sprite.texture = self.background_texture
                    bg_sprite.left = 0
                    bg_sprite.bottom = 0 + self.background_y_offset
                    self._bg_sprite_list.append(bg_sprite)
                    self._bg_sprite_list.draw()
                    
            except Exception as e:
                print(f"Erreur dessin background: {e}")
                # Fallback: fond coloré simple
                arcade.draw_lrbt_rectangle_filled(
                    0, self.world_width, 0, self.world_height,
                    arcade.color.DARK_BLUE_GRAY
                )
        else:
            # Pas de texture : fond simple
            arcade.draw_lrbt_rectangle_filled(
                0, self.world_width, 0, self.world_height,
                arcade.color.BLACK
            )


    def _update_surveillance_screen_position(self):
        # Convertir la position monde de l'agent en coordonnées écran (Camera2D centrée)
        screen_w = self.window.width
        screen_h = self.window.height
        zoom = getattr(self, 'camera_zoom', 1.0) or 1.0
        try:
            cam_x, cam_y = self.camera.position
        except Exception:
            cam_x, cam_y = (self.agent.center_x, self.agent.center_y)

        agent_x = self.agent.center_x
        agent_y = self.agent.center_y

        screen_x = int((agent_x - cam_x) * zoom + (screen_w / 2))
        screen_y = int((agent_y - cam_y) * zoom + (screen_h / 2))

        # Positionner l'écran de surveillance excentré sur la gauche de l'agent
        offset_y = 350
        offset_x = -500  # Décalage vers la gauche (négatif = gauche)
        padding_x = 32  # plus de marge gauche/droite
        padding_y = 12  # marge verticale identique
        desired_x = screen_x + offset_x  # Position excentrée sur la gauche
        desired_y = screen_y + offset_y

        # Conserver l'écran dans les bornes de l'écran
        max_x = screen_w - self.surveillance_screen.screen_width - padding_x
        max_y = screen_h - self.surveillance_screen.screen_height - padding_y
        desired_x = max(padding_x, min(max_x, desired_x))
        desired_y = max(padding_y, min(max_y, desired_y))
        
        # Mise à jour des positions cibles
        self.surveillance_target_x = desired_x
        self.surveillance_target_y = desired_y

    def _apply_smooth_surveillance_movement(self, delta_time):
        """Applique un mouvement smooth à l'écran de surveillance avec délai de suivi"""
        if not self.surveillance_screen:
            return
            
        # Interpolation linéaire vers la position cible
        current_x = self.surveillance_screen.screen_x
        current_y = self.surveillance_screen.screen_y
        
        # Calculer la distance vers la cible
        dx = self.surveillance_target_x - current_x
        dy = self.surveillance_target_y - current_y
        
        # Appliquer le mouvement smooth (plus le facteur est petit, plus c'est smooth)
        smooth_factor = self.surveillance_smooth_factor * (60 * delta_time)  # Normaliser pour 60 FPS
        smooth_factor = min(1.0, smooth_factor)  # Éviter les overshoots
        
        # Mettre à jour la position actuelle
        self.surveillance_screen.screen_x = current_x + (dx * smooth_factor)
        self.surveillance_screen.screen_y = current_y + (dy * smooth_factor)

    def _sync_mission_overlay_bounds(self):
        # Propager les bornes actuelles de l'écran de surveillance aux missions actives
        screen_x = self.surveillance_screen.screen_x
        screen_y = self.surveillance_screen.screen_y
        screen_w = self.surveillance_screen.screen_width
        screen_h = self.surveillance_screen.screen_height
        if self.hero and self.hero.battle_mission:
            bm = self.hero.battle_mission
            if hasattr(bm, 'set_screen_bounds'):
                bm.set_screen_bounds(screen_x, screen_y, screen_w, screen_h)
        if self.hero and getattr(self.hero, 'explore_mission', None):
            em = self.hero.explore_mission
            if hasattr(em, 'set_screen_bounds'):
                em.set_screen_bounds(screen_x, screen_y, screen_w, screen_h)
    
    def draw_floating_message(self):
        # Dessiner un message flottant centré (en coordonnées écran/GUI)
        if not self.floating_message:
            return
        msg = self.floating_message
        arcade.draw_text(
            msg['text'],
            self.ui_width // 2,
            msg['y'],
            msg.get('color', arcade.color.WHITE),
            18,
            anchor_x="center",
            bold=True
        )

    def draw_betting_interface(self):
        # Interface de paris en overlay
        betting_info = self.mission_system.get_betting_info()
        if not betting_info:
            return

        # Fond semi-transparent
        arcade.draw_lrbt_rectangle_filled(
            0, self.ui_width, 0, self.ui_height,
            (0, 0, 0, 150)
        )

        if hasattr(self, 'betting_input_mode') and self.betting_input_mode:
            box_w = 420
            box_h = 70
            box_x = (self.ui_width - box_w) // 2
            box_y = self.ui_height - 60
            arcade.draw_lrbt_rectangle_filled(
                box_x, box_x + box_w, box_y, box_y + box_h,
                (30, 30, 30, 230)
            )
            arcade.draw_lrbt_rectangle_outline(
                box_x, box_x + box_w, box_y, box_y + box_h,
                arcade.color.GOLD, 2
            )
            if self.betting_input_mode == 'success':
                label = "Montant à parier sur la RÉUSSITE :"
                color = arcade.color.LIGHT_GREEN
            else:
                label = "Montant à parier sur l'ÉCHEC :"
                color = arcade.color.LIGHT_GREEN
            arcade.draw_text(label, self.ui_width // 2, box_y + box_h - 28, color, 18, anchor_x="center", bold=True)
            amount_str = getattr(self, 'betting_input_amount', '')
            arcade.draw_text(f"{amount_str}", self.ui_width // 2, box_y + 18, arcade.color.WHITE, 28, anchor_x="center", bold=True)

        # Titre
        arcade.draw_text(
            "STATION DE PARIS",
            self.ui_width // 2, self.ui_height - 100,
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
        if hasattr(self, 'betting_input_mode') and self.betting_input_mode:
            arcade.draw_text(
                "Entrez le montant puis appuyez sur Entrée (ESC pour annuler)",
                self.ui_width // 2, self.ui_height - 120,
                arcade.color.LIGHT_GRAY, 15, anchor_x="center"
            )
        else:
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
        if not hasattr(self, 'betting_input_mode'):
            self.betting_input_mode = None  # None, 'success', 'echec'
            self.betting_input_amount = ''
        if self.betting_input_mode:
            if arcade.key.KEY_0 <= key <= arcade.key.KEY_9:
                if len(self.betting_input_amount) < 7:
                    self.betting_input_amount += chr(key)
            elif key == arcade.key.BACKSPACE:
                self.betting_input_amount = self.betting_input_amount[:-1]
            elif key in (arcade.key.ENTER, arcade.key.RETURN):
                try:
                    amount = int(self.betting_input_amount)
                except Exception:
                    amount = 0
                if amount <= 0:
                    self.show_floating_message("Montant invalide !", arcade.color.RED)
                elif amount > self.mission_system.gold:
                    self.show_floating_message("Fonds insuffisants !", arcade.color.RED)
                else:
                    result = self.mission_system.place_bet(self.betting_input_mode, amount)
                    self.show_floating_message(str(result), arcade.color.GREEN if "placé" in str(result) else arcade.color.RED)
                    print(result)
                    self.betting_input_mode = None
                    self.betting_input_amount = ''
                    return
                self.betting_input_amount = ''
            elif key == arcade.key.ESCAPE:
                self.betting_input_mode = None
                self.betting_input_amount = ''
            return
        if key == arcade.key.KEY_1:
            self.betting_input_mode = 'success'
            self.betting_input_amount = ''
            self.show_floating_message("Entrez le montant à parier (Succès)", arcade.color.LIGHT_GREEN)
        elif key == arcade.key.KEY_2:
            self.betting_input_mode = 'echec'
            self.betting_input_amount = ''
            self.show_floating_message("Entrez le montant à parier (Échec)", arcade.color.LIGHT_RED)
        elif key == arcade.key.KEY_3:
            self.mission_system.close_betting_interface()
            self.show_floating_message("Pari annulé.", arcade.color.LIGHT_GRAY)
    
    def on_update(self, delta_time):
        if self.game_state == GAME_STATE_PLAYING:
            self.agent.update(delta_time)
            self.hero.update(delta_time)
            self.mission_system.update(delta_time, self.ship)
            self.surveillance_screen.update(delta_time)
            
            # Appliquer le mouvement smooth à l'écran de surveillance
            self._apply_smooth_surveillance_movement(delta_time)
            
            # Mettre à jour l'animation du héros NPC
            self.ship.update_hero_npc(delta_time)
            
            # Mettre à jour les SpriteLists
            self.agent_list.update()
            self.hero_list.update()

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

            # Lancer le mini-jeu Wire Puzzle si demandé (overlay)
            if getattr(self.mission_system, 'wire_puzzle_requested', False):
                self.mission_system.wire_puzzle_requested = False
                def _on_complete():
                    self.wire_overlay = None
                self.wire_overlay = WirePuzzleOverlay(self.window, on_exit_callback=_on_complete, mission_system=self.mission_system)

            # Lancer le mini-jeu de réparation SANTÉ si demandé (overlay)
            if getattr(self.mission_system, 'repair_requested', False):
                self.mission_system.repair_requested = False
                def _on_repair_complete():
                    self.repair_overlay = None
                self.repair_overlay = RepairMinigameOverlay(self.window, on_exit_callback=_on_repair_complete, mission_system=self.mission_system, completion_attr="repair_completed", title="RÉPARATION ÉCRAN - SYSTÈME DE SANTÉ")

            # Lancer le mini-jeu de réparation SCANNER ENNEMIS si demandé (overlay)
            if getattr(self.mission_system, 'enemies_screen_requested', False):
                self.mission_system.enemies_screen_requested = False
                def _on_scan_complete():
                    self.enemy_scan_overlay = None
                self.enemy_scan_overlay = RepairMinigameOverlay(self.window, on_exit_callback=_on_scan_complete, mission_system=self.mission_system, completion_attr="enemies_screen_completed", title="CALIBRATION SCANNER ENNEMIS")

            # Mettre à jour la caméra APRÈS toutes les mises à jour
            self.update_camera()

            if self.terminal:
                self.mission_system.gold = self.terminal.gold
            if not self.terminal and self.mission_system.terminal_on:
                    self.terminal = MainTerminal(self.window, on_exit_callback=self.close_terminal, screen_connected=self.surveillance_screen_connected, gold=self.mission_system.gold)

    

    
    def repositioner_camera(self):
        """Repositionne immédiatement la caméra après un redimensionnement"""
        screen_w = self.window.width
        screen_h = self.window.height
        # Corriger pour le zoom: demi-largeur/hauteur en unités monde
        zoom = getattr(self, 'camera_zoom', 1.0) or 1.0
        half_w = (screen_w / 2) / zoom
        half_h = (screen_h / 2) / zoom

        # Cibler le centre sur l'agent en X
        target_center_x = max(self.world_left + half_w, min(self.world_right - half_w, self.agent.center_x))
        target_center_y = half_h

        # Positionnement immédiat (sans easing)
        self.camera.position = (target_center_x, target_center_y)
        # Appliquer le zoom fixe
        try:
            self.camera.zoom = self.camera_zoom
        except Exception:
            pass
        print(f"Caméra repositionnée à: ({target_center_x}, {target_center_y})")

    def update_camera(self):
        # Suivi fluide: Camera2D.position représente le CENTRE de la caméra
        # En fullscreen, on utilise la taille réelle de l'écran
        screen_w = self.window.width
        screen_h = self.window.height
        # Corriger pour le zoom: demi-largeur/hauteur en unités monde
        zoom = getattr(self, 'camera_zoom', 1.0) or 1.0
        half_w = (screen_w / 2) / zoom
        half_h = (screen_h / 2) / zoom

        # Cibler le centre sur l'agent en X
        target_center_x = max(self.world_left + half_w, min(self.world_right - half_w, self.agent.center_x))
        
        # Pour que le background touche le bas : le centre Y de la caméra doit être à half_h
        # Cela met y=0 du monde au bas de l'écran
        target_center_y = half_h

        # Easing vers la cible
        current_x, current_y = self.camera.position
        ease = 0.18
        new_x = current_x + (target_center_x - current_x) * ease
        new_y = current_y + (target_center_y - current_y) * ease
        self.camera.position = (new_x, new_y)
        # Appliquer le zoom fixe
        try:
            self.camera.zoom = self.camera_zoom
        except Exception:
            pass
    
    def on_key_press(self, key, modifiers):
        if hasattr(self, 'wire_overlay') and self.wire_overlay is not None:
            self.wire_overlay.on_key_press(key, modifiers)
            return
        if hasattr(self, 'repair_overlay') and self.repair_overlay is not None:
            self.repair_overlay.on_key_press(key, modifiers)
            return
        if hasattr(self, 'enemy_scan_overlay') and self.enemy_scan_overlay is not None:
            self.enemy_scan_overlay.on_key_press(key, modifiers)
            return
        if self.terminal:
            self.terminal.on_key_press(key, modifiers)
            return
        if key == arcade.key.ESCAPE:
            self.background_music_player.delete()
            # Retour au menu
            from scenes.menu_scene import MenuScene
            menu_scene = MenuScene()
            self.window.show_view(menu_scene)
        elif key == arcade.key.TAB:
            #### Test fonction Ouvrir le terminal
            if self.terminal:
                pass
            else:
                self.terminal = MainTerminal(self.window, on_exit_callback=self.close_terminal, screen_connected=self.surveillance_screen_connected, gold=self.mission_system.gold)
                print("Terminal ouvert.")
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

    def close_terminal(self):
        if self.terminal:
            self.surveillance_screen_connected = self.terminal.screen_connected
            self.mission_system.terminal_on = False
            self.terminal = None
            print("Terminal fermé.")
