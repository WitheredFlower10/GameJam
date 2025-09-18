import arcade
import time
import os
from utils.constants import SURVEILLANCE_SCREEN_WIDTH, SURVEILLANCE_SCREEN_HEIGHT
from utils.constants import SURVEILLANCE_SCREEN_X, SURVEILLANCE_SCREEN_Y, SCREEN_COLOR
from utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT


class SurveillanceScreen:
    
    def __init__(self):
        self.hero = None
        self.mission_system = None
        self.connected = False
        self.background_sprites = []
        self.enemy_sprites = []
        
        self.screen_x = SURVEILLANCE_SCREEN_X
        self.screen_y = SURVEILLANCE_SCREEN_Y
        # +20 px (10 à gauche, 10 à droite) par défaut
        self.screen_width = SURVEILLANCE_SCREEN_WIDTH + 20
        self.screen_height = SURVEILLANCE_SCREEN_HEIGHT
        
        self.scroll_speed = 20
        self.background_offset = 0
        
        # Paramètre pour gérer la hauteur de l'image overlay (1.0 = 100%, 1.2 = 120%, etc.)
        self.overlay_height_multiplier = 1.4
        
        # Paramètre pour gérer l'alignement vertical de l'image overlay (0.0 = en haut, 0.5 = centré, 1.0 = en bas)
        self.overlay_vertical_alignment = -0.4
        
        # Charger la texture "transparent" pour le cadre de l'écran
        self.screen_texture = self._load_screen_texture()
        
        # Charger la texture overlay pour l'image par dessus l'écran de surveillance
        self.overlay_texture = self._load_overlay_texture()
        
        # Charger les textures d'animation pour l'overlay
        self.overlay_textures = []
        self._load_overlay_animation_textures()
        
        # Paramètres d'animation
        self.current_overlay_frame = 0
        self.overlay_animation_speed = 0.2  # Temps entre chaque frame en secondes
        self.overlay_animation_timer = 0
    
    def set_hero(self, hero):
        self.hero = hero
    
    def set_mission_system(self, mission_system):
        self.mission_system = mission_system

    def set_connected(self, connected: bool):
        self.connected = bool(connected)
    
    def _load_screen_texture(self):
        """Charge la texture 'transparent' pour le cadre de l'écran de surveillance"""
        texture = None
        base_candidates = [
            'assets',
            os.path.join(os.path.dirname(__file__), '..', 'assets'),
        ]
        base_candidates = [os.path.normpath(p) for p in base_candidates]
        found = None
        for base in base_candidates:
            if not os.path.isdir(base):
                continue
            direct = os.path.join(base, 'transparent.png')
            if os.path.exists(direct):
                found = direct
                break
            for root, _dirs, files in os.walk(base):
                for f in files:
                    if f.lower() == 'transparent.png':
                        found = os.path.join(root, f)
                        break
                if found:
                    break
            if found:
                break
        try:
            if found:
                texture = arcade.load_texture(found)
                print(f"Texture 'transparent' chargée depuis: {found}")
            else:
                print("ERREUR: Fichier 'transparent.png' non trouvé!")
                # Fallback: créer une texture colorée
                texture = arcade.make_soft_square_texture(100, arcade.color.DARK_GRAY, outer_alpha=255)
        except Exception as e:
            print(f"ERREUR lors du chargement de 'transparent.png': {e}")
            # Fallback: créer une texture colorée
            texture = arcade.make_soft_square_texture(100, arcade.color.DARK_GRAY, outer_alpha=255)
        return texture
    
    def _load_overlay_texture(self):
        """Charge la texture 'transparent' pour l'image par dessus l'écran de surveillance"""
        texture = None
        base_candidates = [
            'assets',
            os.path.join(os.path.dirname(__file__), '..', 'assets'),
        ]
        base_candidates = [os.path.normpath(p) for p in base_candidates]
        found = None
        for base in base_candidates:
            if not os.path.isdir(base):
                continue
            direct = os.path.join(base, 'transparent.png')
            if os.path.exists(direct):
                found = direct
                break
            for root, _dirs, files in os.walk(base):
                for f in files:
                    if f.lower() == 'transparent.png':
                        found = os.path.join(root, f)
                        break
                if found:
                    break
            if found:
                break
        try:
            if found:
                texture = arcade.load_texture(found)
                print(f"Texture 'transparent' chargée depuis: {found}")
            else:
                print("ERREUR: Fichier 'transparent.png' non trouvé!")
                # Fallback: créer une texture colorée
                texture = arcade.make_soft_square_texture(100, arcade.color.DARK_GRAY, outer_alpha=255)
        except Exception as e:
            print(f"ERREUR lors du chargement de 'transparent.png': {e}")
            # Fallback: créer une texture colorée
            texture = arcade.make_soft_square_texture(100, arcade.color.DARK_GRAY, outer_alpha=255)
        return texture
    
    def _load_overlay_animation_textures(self):
        """Charge les textures d'animation pour l'overlay (transparent, transparent-2, transparent-3)"""
        self.overlay_textures = []
        
        # Noms des fichiers à charger
        texture_files = ['transparent.png', 'transparent-2.png', 'transparent-3.png']
        
        base_candidates = [
            'assets',
            os.path.join(os.path.dirname(__file__), '..', 'assets'),
        ]
        base_candidates = [os.path.normpath(p) for p in base_candidates]
        
        for filename in texture_files:
            texture = None
            found = None
            
            for base in base_candidates:
                if not os.path.isdir(base):
                    continue
                    
                direct = os.path.join(base, filename)
                if os.path.exists(direct):
                    found = direct
                    break
                    
                for root, _dirs, files in os.walk(base):
                    for f in files:
                        if f.lower() == filename.lower():
                            found = os.path.join(root, f)
                            break
                    if found:
                        break
                if found:
                    break
            
            try:
                if found:
                    texture = arcade.load_texture(found)
                    print(f"Texture overlay '{filename}' chargée depuis: {found}")
                else:
                    print(f"AVERTISSEMENT: Fichier '{filename}' non trouvé!")
                    # Utiliser la première texture comme fallback
                    if self.overlay_textures:
                        texture = self.overlay_textures[0]
                    else:
                        # Fallback: créer une texture colorée
                        texture = arcade.make_soft_square_texture(100, arcade.color.DARK_GRAY, outer_alpha=255)
            except Exception as e:
                print(f"ERREUR lors du chargement de '{filename}': {e}")
                # Utiliser la première texture comme fallback
                if self.overlay_textures:
                    texture = self.overlay_textures[0]
                else:
                    # Fallback: créer une texture colorée
                    texture = arcade.make_soft_square_texture(100, arcade.color.DARK_GRAY, outer_alpha=255)
            
            self.overlay_textures.append(texture)
        
        # Si aucune texture n'a été chargée, créer une texture de fallback
        if not self.overlay_textures:
            fallback_texture = arcade.make_soft_square_texture(100, arcade.color.DARK_GRAY, outer_alpha=255)
            self.overlay_textures = [fallback_texture, fallback_texture, fallback_texture]
            print("AVERTISSEMENT: Aucune texture overlay trouvée, utilisation de textures de fallback")
    
    def create_background(self):
        # Créer des éléments de décor pour le défilement
        for i in range(10):
            # Étoiles
            star = arcade.SpriteSolidColor(2, 2, arcade.color.WHITE)
            star.center_x = i * 50 + 25
            star.center_y = 150 + (i % 3) * 20
            self.background_sprites.append(star)
            
            # Planètes lointaines
            if i % 3 == 0:
                planet = arcade.SpriteSolidColor(30, 30, arcade.color.BLUE_GRAY)
                planet.center_x = i * 80 + 40
                planet.center_y = 100
                self.background_sprites.append(planet)
    
    def update(self, delta_time):
        if self.hero:
            # Faire défiler l'arrière-plan
            self.background_offset += self.scroll_speed * delta_time
            
            # Repositionner les sprites d'arrière-plan
            for sprite in self.background_sprites:
                sprite.center_x -= self.scroll_speed * delta_time
                if sprite.center_x < -50:
                    sprite.center_x += self.screen_width + 100
            
            # Mettre à jour la position du héros sur l'écran
            if self.hero.state == "traveling":
                self.hero.screen_x += 30 * delta_time
                if self.hero.screen_x > self.screen_width:
                    self.hero.screen_x = 0
            
            # Mettre à jour l'animation de l'overlay
            self.overlay_animation_timer += delta_time
            if self.overlay_animation_timer >= self.overlay_animation_speed:
                self.overlay_animation_timer = 0
                self.current_overlay_frame = (self.current_overlay_frame + 1) % len(self.overlay_textures)
    
    def draw(self):
        # Dessiner l'arrière-plan de l'écran (fond)
        left = self.screen_x
        right = self.screen_x + self.screen_width
        bottom = self.screen_y
        top = self.screen_y + self.screen_height
        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, SCREEN_COLOR)
        
        
        # Dessiner la mission active (bataille ou exploration)
        if self.hero and self.hero.battle_mission:
            self.hero.battle_mission.draw()
        elif self.hero and getattr(self.hero, 'explore_mission', None):
            self.hero.explore_mission.draw()
        else:
            # Dessiner les éléments d'arrière-plan normaux
            for sprite in self.background_sprites:
                if (self.screen_x < sprite.center_x < self.screen_x + self.screen_width and
                    self.screen_y < sprite.center_y < self.screen_y + self.screen_height):
                    # Vérifier si le sprite a une méthode draw, sinon utiliser arcade.draw_sprite
                    if hasattr(sprite, 'draw'):
                        sprite.draw()
                    else:
                        arcade.draw_sprite(sprite)

            # Message quand aucune mission: remplacer par le statut de trajet si en route
            try:
                ms = getattr(self, 'mission_system', None)
                traveling = False
                remaining = 0
                if ms and getattr(ms, 'travel_end_time', None):
                    remaining = int(max(0, ms.travel_end_time - time.time()))
                    traveling = remaining > 0
                if traveling:
                    msg = f"Le héros se dirige à la quête ({remaining}s)"
                    color = arcade.color.YELLOW
                else:
                    msg = "Héro en attente de la quête"
                    color = arcade.color.LIGHT_GRAY
                arcade.draw_text(
                    msg,
                    self.screen_x + self.screen_width // 2,
                    self.screen_y + self.screen_height // 2 + 10,
                    color,
                    14,
                    anchor_x="center",
                    bold=True,
                )
            except Exception:
                pass
        
        # Dessiner les informations du héros
        self.draw_hero_info()

        # Afficher un timer de départ si le héros est en route vers la mission (affichage secondaire désactivé pendant l'attente)
        try:
            ms = getattr(self, 'mission_system', None)
            if ms and getattr(ms, 'current_mission', None) and getattr(ms, 'travel_end_time', None):
                remaining = int(max(0, ms.travel_end_time - time.time()))
                if remaining > 0:
                    msg = f"Le héros se dirige à la quête ({remaining}s)"
                    arcade.draw_text(
                        msg,
                        self.screen_x + self.screen_width // 2,
                        self.screen_y + self.screen_height - 30,
                        arcade.color.YELLOW,
                        14,
                        anchor_x="center",
                        bold=True,
                    )
        except Exception:
            pass

        # Si l'écran n'est pas encore "connecté" via le mini-jeu du terminal,
        # appliquer un filtre blanc plus opaque, avec quelques zones totalement opaques
        if not getattr(self, 'connected', False):
            try:
                # Voile principal (moins transparent qu'avant)
                arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, (255, 255, 255, 175))

                # Patches totalement opaques (coordonnées relatives à l'écran)
                w = self.screen_width
                h = self.screen_height
                patches = [
                    # (lx, rx, by, ty) en pourcentage de la largeur/hauteur
                    (0.08, 0.28, 0.62, 0.92),
                    (0.62, 0.88, 0.18, 0.42),
                    (0.34, 0.50, 0.10, 0.24),
                ]
                for (lx, rx, by, ty) in patches:
                    pl = int(left + w * lx)
                    pr = int(left + w * rx)
                    pb = int(bottom + h * by)
                    pt = int(bottom + h * ty)
                    arcade.draw_lrbt_rectangle_filled(pl, pr, pb, pt, (255, 255, 255, 255))
            except Exception:
                # Fallback: contour léger si la couleur RGBA n'est pas supportée
                arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, arcade.color.LIGHT_GRAY, 4)
        
        # Dessiner l'image overlay par dessus l'écran de surveillance
        if self.overlay_textures:
            try:
                # Calculer les dimensions pour que l'image soit légèrement plus grande que l'écran de surveillance
                overlay_margin = 30  # Marge de 20px de chaque côté
                overlay_left = self.screen_x - overlay_margin
                overlay_bottom = self.screen_y - overlay_margin
                overlay_width = self.screen_width + (overlay_margin * 2)
                overlay_height = self.screen_height + (overlay_margin * 2)
                
                # Augmenter la hauteur de 20%
                overlay_height = int(overlay_height * self.overlay_height_multiplier)
                
                # Ajuster la position verticale pour bien englober l'écran (baisser l'image)
                height_increase = overlay_height - (self.screen_height + (overlay_margin * 2))
                overlay_bottom = self.screen_y - overlay_margin - (height_increase // 2)
                
                # Ajuster la position verticale en fonction de l'alignement vertical
                overlay_bottom += (height_increase * self.overlay_vertical_alignment)
                
                # Créer un sprite à partir de la texture overlay
                overlay_sprite = arcade.Sprite(self.overlay_textures[self.current_overlay_frame])
                overlay_sprite.center_x = overlay_left + overlay_width // 2
                overlay_sprite.center_y = overlay_bottom + overlay_height // 2
                overlay_sprite.width = overlay_width
                overlay_sprite.height = overlay_height
                
                # Dessiner le sprite overlay
                arcade.draw_sprite(overlay_sprite)
            except Exception as e:
                print(f"Erreur lors du dessin de l'overlay: {e}")
    
    def draw_hero_info(self):
        if not self.hero:
            return
        
        info_x = self.screen_x + 10
        info_y = self.screen_y + self.screen_height - 20
        
        # Barre de vie (affichée uniquement si le wire puzzle est complété)
        show_health = bool(self.mission_system and getattr(self.mission_system, 'wire_puzzle_completed', False))
        if show_health:
            arcade.draw_text("Vie:", info_x, info_y, arcade.color.WHITE, 12)
            health_width = (self.hero.get_health_percentage() / 100) * 100
            # Positionner la barre bien à l'intérieur de l'écran (éviter de dépasser à gauche)
            bar_left = self.screen_x + 10
            bar_right_max = bar_left + 100
            fill_right = bar_left + max(0, min(100, health_width))
            arcade.draw_lrbt_rectangle_filled(
                bar_left, fill_right, info_y - 10, info_y, arcade.color.GREEN
            )
            arcade.draw_lrbt_rectangle_outline(
                bar_left, bar_right_max, info_y - 10, info_y, arcade.color.WHITE
            )
        
        
        # Compteur d'ennemis tués (si mission de bataille active) - visible seulement si scanner réparé
        show_enemy_counter = bool(self.mission_system and getattr(self.mission_system, 'enemies_screen_completed', False))
        if show_enemy_counter and self.hero.battle_mission and self.hero.battle_mission.is_active:
            kill_text = f"Ennemis: {self.hero.battle_mission.enemies_destroyed}/{self.hero.battle_mission.enemies_to_kill}"
            arcade.draw_text(kill_text, info_x, info_y - 45, arcade.color.YELLOW, 12)
