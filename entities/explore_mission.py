import arcade
import random
import time
import os
from utils.constants import (
    SURVEILLANCE_SCREEN_WIDTH, SURVEILLANCE_SCREEN_HEIGHT, SURVEILLANCE_SCREEN_X, SURVEILLANCE_SCREEN_Y,
    BULLET_SPEED,
)
from entities.battle_mission import Explosion


class ExploreMission:
    """Mission d'exploration de type platformer, auto-contrôlée"""

    def __init__(self, hero):
        self.hero = hero
        self.player_list = None
        self.platform_list = None
        self.enemy_list = None
        self.bullet_list = None
        self.explosion_list = None
        self.artifact_list = None

        self.is_active = False
        self.mission_completed = False
        self.success = False

        self.gravity = 0.3  # Équilibrée avec jump_strength 20.0 pour atteindre 80 pixels de hauteur
        self.move_speed = 0.75
        self.jump_strength = 8.5  # Ajustée pour atteindre la hauteur de saut de 80 pixels
        
        # Animation système pour le héros
        self.hero_walk_textures = []
        self.hero_animation_index = 0
        
        # Charger la texture d'ennemi (sera chargée dans setup())
        self.enemy_texture = None
        self.hero_animation_timer = 0.0
        self.hero_animation_speed = 0.3  # secondes par frame
        self.hero_is_moving = False
        self.hero_was_moving = False
        self.hero_on_platform = False  # Indique si le héros est sur une plateforme
        self.hero_platform_level = 0  # Niveau de la plateforme actuelle
        self._load_hero_textures()
        
        # Système de hauteurs standardisées adaptées à la nouvelle taille du héros PNG
        self.jump_height = 80  # Hauteur qu'un saut peut atteindre (en pixels) - comme demandé
        # Overlay bounds (can be updated by the scene)
        self.overlay_x = SURVEILLANCE_SCREEN_X
        self.overlay_y = SURVEILLANCE_SCREEN_Y
        self.overlay_w = SURVEILLANCE_SCREEN_WIDTH + 20
        self.overlay_h = SURVEILLANCE_SCREEN_HEIGHT
        self.platform_levels = [
            self.overlay_y + 15,  # Niveau sol (0)
            self.overlay_y + 15 + self.jump_height,  # Niveau 1
            self.overlay_y + 15 + self.jump_height * 2,  # Niveau 2
            self.overlay_y + 15 + self.jump_height * 3,  # Niveau 3
            self.overlay_y + 15 + self.jump_height * 4,  # Niveau 4
        ]
        self.last_shot_time = 0
        self.last_enemy_shot = 0  # Pour les tirs d'ennemis
        self.start_time = time.time()
        self.max_duration_seconds = 10.0
        self.duration_expired = False
        self.force_artifact_next = False
        self.min_health_threshold = 2  # Truquage: ne jamais descendre en-dessous
        
        # Système de téléportation et patterns
        self.pattern_generated = False
        self.artifact_chance = 0.01 # 1% de chance d'apparition d'artefact
        self.evaluated_platforms = set()  # Plateformes déjà évaluées pour le saut
        self.min_enemy_spacing = 30
        self.last_random_jump_time = 0  # Temps du dernier saut aléatoire
        self.laser_sound = arcade.load_sound("assets/sounds/laser.wav")
        self.start_mission()
    
    def _get_hero_dimensions(self):
        """Retourne les dimensions réelles du héros (largeur, hauteur) - taille fixe pour la consistance"""
        # Utiliser une taille fixe basée sur la première frame d'animation pour éviter les changements constants
        if self.hero_walk_textures and len(self.hero_walk_textures) > 0:
            # Utiliser la première frame comme référence
            first_texture = self.hero_walk_textures[0]
            try:
                width = float(first_texture.width) * self.hero.scale
                height = float(first_texture.height) * self.hero.scale
                return width, height
            except (TypeError, AttributeError):
                pass
        
        # Fallback : utiliser les propriétés du sprite actuel
        if hasattr(self.hero, 'width') and hasattr(self.hero, 'height'):
            width = float(self.hero.width)
            height = float(self.hero.height)
            return width, height
        
        # Dernière option : dimensions par défaut
        width = 16.0 * self.hero.scale
        height = 16.0 * self.hero.scale
        return width, height
    
    def _position_hero_on_ground(self, ground_level):
        """Positionne le héros pour que ses pieds touchent exactement le niveau du sol spécifié"""
        hero_width, hero_height = self._get_hero_dimensions()
        # Le bas du sprite (pieds) doit être au niveau ground_level
        # Donc le centre doit être à ground_level + (hauteur/2)
        self.hero.center_y = ground_level + hero_height / 2
    
    def _is_hero_on_ground(self):
        """Vérifie si le héros est au sol (pas en saut)"""
        hero_width, hero_height = self._get_hero_dimensions()
        hero_bottom = self.hero.center_y - hero_height / 2
        ground_level = self.platform_levels[0]
        
        # Tolérance de 5px comme dans le système de collision
        return hero_bottom <= ground_level + 5

    def start_mission(self):
        self.is_active = True
        self.setup()

    def setup(self):
        self.player_list = arcade.SpriteList()
        self.platform_list = arcade.SpriteList(use_spatial_hash=True)
        self.enemy_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.explosion_list = arcade.SpriteList()
        self.artifact_list = arcade.SpriteList()

        # Sauvegarder l'état original du héros
        self.original_hero_x = self.hero.center_x
        self.original_hero_y = self.hero.center_y
        self.original_hero_change_x = getattr(self.hero, 'change_x', 0)
        self.original_hero_change_y = getattr(self.hero, 'change_y', 0)
        self.original_hero_scale = getattr(self.hero, 'scale', 1.0)

        # Charger la texture d'ennemi
        self.enemy_texture = self._load_enemy_texture()

        # Réduire la taille du héros pour cette mission seulement
        self.hero.scale = 0.25  # Diviser la taille par 4 (2 fois plus petit que précédemment)

        # Positionner le héros au sol côté gauche (niveau 0) - pieds sur le sol
        self.hero.center_x = self.overlay_x + 20
        self._position_hero_on_ground(self.platform_levels[0])
        self.hero.change_x = 0
        self.hero.change_y = 0
        self.player_list.append(self.hero)

        # Générer le premier pattern de plateformes
        self.generate_new_pattern()
        self.pattern_generated = True

    def end_mission(self):
        self.is_active = False
        self.mission_completed = True
        
        # Restaurer l'état original du héros pour ne pas affecter les autres missions
        if hasattr(self, 'original_hero_x'):
            self.hero.center_x = self.original_hero_x
            self.hero.center_y = self.original_hero_y
            self.hero.change_x = self.original_hero_change_x
            self.hero.change_y = self.original_hero_change_y
            self.hero.scale = self.original_hero_scale  # Restaurer la taille originale
        
        # Nettoyer les propriétés temporaires d'exploration
        if hasattr(self.hero, 'temp_velocity_y'):
            delattr(self.hero, 'temp_velocity_y')
        
        # self.success est déjà positionné lors de la collecte d'artefact

    def update(self, delta_time: float):
        if not self.is_active:
            return

        # Chrono de mission: après 60s, marquer que la PROCHAINE génération contient un artefact
        if (not self.duration_expired) and (time.time() - self.start_time >= self.max_duration_seconds):
            self.duration_expired = True
            self.force_artifact_next = True

        # Vérifier si le héros atteint le bord droit de l'écran (seulement s'il est au sol/sur plateforme)
        current_velocity_y = getattr(self.hero, 'temp_velocity_y', 0)
        if (self.hero.center_x >= self.overlay_x + self.overlay_w - 20 and 
            (self.hero_on_platform or self._is_hero_on_ground()) and
            current_velocity_y >= 0):  # Pas en train de tomber
            self.teleport_hero_and_regenerate()

        # Auto-contrôle du héros: avancer, sauter parfois (uniquement si cette mission est active)
        if self.is_active:
            # Variables temporaires pour le mouvement (n'affectent pas le héros original)
            current_velocity_x = self.move_speed
            current_velocity_y = getattr(self.hero, 'temp_velocity_y', 0)
            
            # Détecter les plateformes devant le héros pour sauter intelligemment
            hero_future_x = self.hero.center_x + 30  # Position future du héros
            should_jump = False
            
            # Vérifier s'il y a une plateforme devant qui nécessite un saut
            for platform in self.platform_list:
                # Utiliser un ID unique pour chaque plateforme (basé sur sa position)
                platform_id = (round(platform.center_x), round(platform.center_y))
                
                # Si cette plateforme a déjà été évaluée, passer à la suivante
                if platform_id in self.evaluated_platforms:
                    continue
                
                # Utiliser les dimensions de la texture pour les plateformes
                platform_width = platform.texture.width if hasattr(platform, 'texture') and platform.texture else 60
                platform_height = platform.texture.height if hasattr(platform, 'texture') and platform.texture else 15
                platform_left = platform.center_x - platform_width / 2
                platform_top = platform.center_y + platform_height / 2
                
                # Déterminer le niveau actuel du héros (plus robuste)
                hero_current_level = 0  # Par défaut au sol
                hero_width, hero_height = self._get_hero_dimensions()
                hero_bottom = self.hero.center_y - hero_height / 2
                
                for i, level_y in enumerate(self.platform_levels):
                    if abs(hero_bottom - level_y) < 15:  # Tolérance de 15 pixels pour les pieds
                        hero_current_level = i
                        break
                
                # Déterminer le niveau de la plateforme
                platform_level = 0
                for i, level_y in enumerate(self.platform_levels):
                    if abs(platform.center_y - level_y) < 10:  # Tolérance de 10 pixels
                        platform_level = i
                        break
                
                # Conditions pour sauter :
                # 1. Le héros doit être proche de la plateforme
                # 2. La plateforme doit être EXACTEMENT 1 niveau au-dessus du héros
                # 3. La plateforme doit être dans une distance raisonnable devant le héros
                hero_distance_to_platform = platform_left - self.hero.center_x
                
                if (platform_level == hero_current_level + 1 and  # Exactement 1 niveau au-dessus
                    -10 < hero_distance_to_platform < 40):    # Distance plus large (-10 à 40 pixels)
                    
                    # Marquer cette plateforme comme évaluée
                    self.evaluated_platforms.add(platform_id)
                    
                    # 80% de chance de sauter (une seule fois par plateforme)
                    if random.random() < 0.8:
                        should_jump = True
                        break
            
            # Bloquer le saut si un artefact est proche (<= 50 px) devant le héros
            if len(self.artifact_list) > 0:
                try:
                    artifact = self.artifact_list[0]
                    dx_to_artifact = artifact.center_x - self.hero.center_x
                    if dx_to_artifact > 0 and dx_to_artifact <= 50:
                        should_jump = False
                except Exception:
                    pass
            
            # Saut intelligent ou saut aléatoire occasionnel
            if (should_jump and current_velocity_y == 0):
                current_velocity_y = self.jump_strength
                print(f"Héros saute intelligemment! Force: {self.jump_strength}")
            elif (current_velocity_y == 0 and 
                  time.time() - self.last_random_jump_time > 2.0 and  # Délai minimum de 2 secondes
                  random.random() < 0.02):  # 2% de chance de saut aléatoire
                current_velocity_y = self.jump_strength
                self.last_random_jump_time = time.time()  # Reset du timer
                print(f"Héros saute aléatoirement! Force: {self.jump_strength}")
            
            # Gravité
            current_velocity_y -= self.gravity

            # Mouvement horizontal avec vérification de collision
            new_x = self.hero.center_x + current_velocity_x
            self.hero.center_x = new_x
            
            # Collisions horizontales avec plateformes (seulement si vraiment bloqué sur le côté)
            for platform in self.platform_list:
                if arcade.check_for_collision(self.hero, platform):
                    # Calculer les dimensions de la plateforme
                    platform_width = platform.texture.width if hasattr(platform, 'texture') and platform.texture else 60
                    platform_height = platform.texture.height if hasattr(platform, 'texture') and platform.texture else 15
                    if hasattr(platform, 'scale_x'):
                        platform_width *= platform.scale_x
                    if hasattr(platform, 'scale_y'):
                        platform_height *= platform.scale_y
                    
                    platform_left = platform.center_x - platform_width / 2
                    platform_right = platform.center_x + platform_width / 2
                    platform_top = platform.center_y + platform_height / 2
                    platform_bottom = platform.center_y - platform_height / 2
                    
                    # Seulement empêcher si le héros est vraiment bloqué sur le côté (pas en train de tomber)
                    # Calculer les vraies dimensions du héros
                    hero_width, hero_height = self._get_hero_dimensions()
                    hero_bottom = self.hero.center_y - hero_height / 2
                    hero_top = self.hero.center_y + hero_height / 2
                    
                    # Collision horizontale seulement si :
                    # 1. Le héros est au niveau vertical de la plateforme
                    # 2. Il n'est pas en train de tomber rapidement
                    # 3. Il essaie vraiment de traverser horizontalement
                    if (hero_bottom < platform_top - 5 and hero_top > platform_bottom + 5 and  # Au niveau vertical avec marge
                        abs(current_velocity_y) < 2):  # Pas en train de tomber rapidement
                        # Utiliser les dimensions déjà calculées
                        # Seulement repousser si vraiment sur le côté gauche de la plateforme
                        if self.hero.center_x > platform_left and self.hero.center_x < platform_right:
                            self.hero.center_x = platform_left - hero_width / 2
            
            # Limites écran horizontales
            left_bound = self.overlay_x + 20
            # Keep hero inside 20px margins left/right
            right_bound = self.overlay_x + self.overlay_w - 20
            if self.hero.center_x > right_bound:
                self.hero.center_x = right_bound
            if self.hero.center_x < left_bound:
                self.hero.center_x = left_bound

            # Vérifier d'abord si on est déjà sur une plateforme stable
            if self.hero_on_platform:
                # Maintenir la position Y stable sur la plateforme (comme l'agent au sol)
                self._position_hero_on_ground(self.hero_platform_level)
                
                # Vérifier si on veut sauter ou si on tombe de la plateforme
                hero_width, hero_height = self._get_hero_dimensions()
                hero_left = self.hero.center_x - hero_width / 2
                hero_right = self.hero.center_x + hero_width / 2
                
                # Vérifier si on est encore au-dessus d'une plateforme
                still_on_platform = False
                for platform in self.platform_list:
                    platform_width = platform.texture.width if hasattr(platform, 'texture') and platform.texture else 60
                    if hasattr(platform, 'scale_x'):
                        platform_width *= platform.scale_x
                    platform_left = platform.center_x - platform_width / 2
                    platform_right = platform.center_x + platform_width / 2
                    platform_top = platform.center_y + (platform.texture.height if hasattr(platform, 'texture') and platform.texture else 15) / 2
                    
                    # Si le héros est encore au-dessus de cette plateforme
                    if (abs(platform_top - self.hero_platform_level) < 5 and  # Même niveau
                        hero_right > platform_left + 10 and hero_left < platform_right - 10):  # Encore au-dessus avec marge
                        still_on_platform = True
                        break
                
                # Si plus au-dessus d'une plateforme, commencer à tomber
                if not still_on_platform:
                    self.hero_on_platform = False
                    current_velocity_y = 0  # Commencer la chute doucement
            else:
                # Mouvement vertical normal avec collisions plateformes
                self.hero.center_y += current_velocity_y
                hits = arcade.check_for_collision_with_list(self.hero, self.platform_list)
                if hits:
                    # Se poser sur la plateforme seulement si on tombe dessus (pas si on la traverse)
                    if current_velocity_y <= 0:  # Seulement quand on tombe
                        # Trouver le haut de la plateforme la plus haute touchée
                        top = max((s.center_y + (s.texture.height if hasattr(s, 'texture') and s.texture else 15) / 2) for s in hits)
                        # Positionner le héros pour que ses pieds touchent le haut de la plateforme
                        self._position_hero_on_ground(top)
                        current_velocity_y = 0
                        # Marquer qu'on est sur une plateforme (verrouillage stable)
                        self.hero_on_platform = True
                        self.hero_platform_level = top
                else:
                    # Si pas de collision avec plateforme, vérifier si on est au sol
                    hero_width, hero_height = self._get_hero_dimensions()
                    hero_bottom = self.hero.center_y - hero_height / 2
                    ground_level = self.platform_levels[0]
                    
                    if hero_bottom <= ground_level + 5:  # Tolérance de 5px
                        # Verrouiller au sol comme l'agent
                        self._position_hero_on_ground(ground_level)
                        current_velocity_y = 0
                        self.hero_on_platform = False
            
            # Sauvegarder la vélocité temporaire pour la prochaine frame
            self.hero.temp_velocity_y = current_velocity_y

        # Tir automatique vers la droite
        if time.time() - self.last_shot_time > 0.5:
            bullet = arcade.Sprite()
            bullet.texture = arcade.make_soft_square_texture(5, (255, 255, 0), outer_alpha=255)  # Jaune explicite, taille divisée par 2
            bullet.center_x = self.hero.center_x + 10
            bullet.center_y = self.hero.center_y
            bullet.change_x = BULLET_SPEED
            self.bullet_list.append(bullet)
            self.last_shot_time = time.time()
            if self.laser_sound:
                arcade.play_sound(self.laser_sound, volume=0.1)

        # Tir des ennemis statiques
        if time.time() - self.last_enemy_shot > 2.0:  # Tir toutes les 2 secondes
            for enemy in self.enemy_list:
                if random.random() < 0.3:  # 30% de chance qu'un ennemi tire
                    enemy_bullet = arcade.Sprite()
                    enemy_bullet.texture = arcade.make_soft_square_texture(4, (255, 0, 0), outer_alpha=255)  # Rouge explicite, taille divisée par 2
                    enemy_bullet.center_x = enemy.center_x - 10
                    enemy_bullet.center_y = enemy.center_y
                    enemy_bullet.change_x = -3  # Vitesse vers la gauche
                    self.bullet_list.append(enemy_bullet)
            self.last_enemy_shot = time.time()

        # Mettre à jour projectiles
        self.bullet_list.update()
        for bullet in list(self.bullet_list):
            # Supprimer les balles qui sortent de l'écran
            # Despawn bullets inside margins: 20px before right, 20px after left
            if (bullet.center_x > self.overlay_x + self.overlay_w - 20 or
                bullet.center_x < self.overlay_x + 20):
                bullet.remove_from_sprite_lists()
            
            # Collision balles d'ennemis avec le héros
            if (hasattr(bullet, 'change_x') and bullet.change_x < 0 and  # Balle qui va vers la gauche (ennemi)
                arcade.check_for_collision(bullet, self.hero)):
                bullet.remove_from_sprite_lists()
                # Truquage: ne jamais laisser mourir le héros dans Explore
                new_health = self.hero.health - 2
                if new_health < self.min_health_threshold:
                    new_health = self.min_health_threshold
                self.hero.health = new_health

        # Collisions balles du héros avec ennemis
        for bullet in list(self.bullet_list):
            # Seulement les balles qui vont vers la droite (héros)
            if hasattr(bullet, 'change_x') and bullet.change_x > 0:
                hit_list = arcade.check_for_collision_with_list(bullet, self.enemy_list)
                if hit_list:
                    bullet.remove_from_sprite_lists()
                    for enemy in hit_list:
                        boom = Explosion(enemy.center_x, enemy.center_y)
                        self.explosion_list.append(boom)
                        enemy.remove_from_sprite_lists()

        # Mouvement propre des ennemis (approche)
        # Les ennemis sont maintenant statiques (pas de mouvement)

        # Dommages si contact héros/ennemi
        for enemy in list(self.enemy_list):
            if arcade.check_for_collision(enemy, self.hero):
                boom = Explosion(enemy.center_x, enemy.center_y)
                self.explosion_list.append(boom)
                enemy.remove_from_sprite_lists()
                
                # Le héros perd de la vie mais ne meurt jamais (truquage discret)
                new_health = self.hero.health - 5
                if new_health < self.min_health_threshold:
                    new_health = self.min_health_threshold
                self.hero.health = new_health

        self.explosion_list.update()

        # Vérifier récupération de l'artefact
        if len(self.artifact_list) > 0:
            artifact = self.artifact_list[0]
            picked = False
            try:
                if arcade.check_for_collision(self.hero, artifact):
                    picked = True
            except Exception:
                picked = False
            if not picked and self._hero_overlaps_artifact_lenient(artifact):
                picked = True
            if picked:
                self.success = True
                # Effet simples
                fx = Explosion(artifact.center_x, artifact.center_y)
                self.explosion_list.append(fx)
                artifact.remove_from_sprite_lists()
                self.end_mission()
        
        # Mettre à jour l'animation du héros
        self._update_hero_animation(delta_time)

    def is_mission_finished(self):
        return self.mission_completed and not self.is_active

    def draw(self):
        if not self.is_active:
            return
        
        # Dessiner tous les sprites (plus besoin de filtrage car plus de défilement)
        self.platform_list.draw()
        self.artifact_list.draw()
        self.player_list.draw()
        self.enemy_list.draw()
        self.bullet_list.draw()
        self.explosion_list.draw()

    def teleport_hero_and_regenerate(self):
        """Téléporte le héros à gauche et génère un nouveau pattern"""
        print(f"Téléportation du héros - Position: ({self.hero.center_x}, {self.hero.center_y}), Au sol: {self._is_hero_on_ground()}, Sur plateforme: {self.hero_on_platform}")
        # Téléporter le héros au début de l'écran (niveau sol) - pieds sur le sol
        self.hero.center_x = self.overlay_x + 20
        self._position_hero_on_ground(self.platform_levels[0])
        self.hero.change_y = 0  # Réinitialiser la vélocité verticale
        
        # Nettoyer les anciens sprites (sauf le héros)
        self.platform_list.clear()
        self.enemy_list.clear()
        self.artifact_list.clear()
        self.bullet_list.clear()
        self.explosion_list.clear()
        
        # Réinitialiser les plateformes évaluées pour le nouveau pattern
        self.evaluated_platforms.clear()
        
        # Générer un nouveau pattern
        self.generate_new_pattern()
        print("Nouveau pattern généré !")

    def generate_new_pattern(self):
        """Génère un nouveau pattern de plateformes, ennemis et artefacts"""
        # Sol de base adapté au héros PNG
        ground = arcade.Sprite()
        ground.texture = arcade.make_soft_square_texture(15, (0, 100, 0), outer_alpha=255)  # Vert foncé, taille adaptée
        # Rétrécir légèrement le sol pour éviter qu'il ne touche les bords
        ground.scale_x = max(0, (self.overlay_w - 10) / 15)
        ground.scale_y = 1
        ground.center_x = self.overlay_x + self.overlay_w // 2
        ground.center_y = self.overlay_y + 10
        self.platform_list.append(ground)
        
        # Plateformes à hauteurs standardisées avec génération intelligente
        num_platforms = random.randint(4, 8)  # Réduit pour s'adapter à la hauteur de saut de 80
        platforms_info = []  # Pour éviter les superpositions
        
        # Générer une progression logique de niveaux
        max_level = random.randint(1, 3)  # Limité aux 3 premiers niveaux avec hauteur de saut de 80
        available_levels = list(range(1, max_level + 1))  # Niveaux 1 à max_level
        
        # S'assurer qu'il y a au moins une plateforme de chaque niveau jusqu'au maximum
        guaranteed_platforms = []
        for level in available_levels:
            guaranteed_platforms.append(level)
        
        # Ajouter des plateformes supplémentaires aléatoires
        remaining_platforms = num_platforms - len(guaranteed_platforms)
        for _ in range(remaining_platforms):
            guaranteed_platforms.append(random.choice(available_levels))
        
        # Mélanger l'ordre des plateformes
        random.shuffle(guaranteed_platforms)
        
        for i, level in enumerate(guaranteed_platforms):
            attempts = 0
            while attempts < 10:  # Limite les tentatives pour éviter boucle infinie
                width = random.randint(40, 80)  # Largeur adaptée au héros PNG
                height = 12  # Hauteur adaptée au héros PNG
                x = self.overlay_x + random.randint(40, self.overlay_w - 70)  # Éviter les 50px à droite
                
                y = self.platform_levels[level]
                
                # Vérifier les superpositions avec les plateformes existantes
                overlap = False
                for existing in platforms_info:
                    # Vérifier seulement la superposition horizontale puisque les hauteurs sont standardisées
                    if (abs(x - existing['x']) < (width + existing['width']) / 2 + 20):  # Espacement adapté au héros PNG
                        overlap = True
                        break
                
                if not overlap:
                    platform = arcade.Sprite()
                    platform.texture = arcade.make_soft_square_texture(12, (139, 69, 19), outer_alpha=255)  # Marron, taille adaptée au héros PNG
                    platform.scale_x = width / 12
                    platform.scale_y = height / 12
                    platform.center_x = x
                    platform.center_y = y
                    self.platform_list.append(platform)
                    platforms_info.append({'x': x, 'y': y, 'width': width, 'height': height, 'level': level})
                    break
                
                attempts += 1
        
        # Ennemis statiques (tous en rouge) placés sur des surfaces, avec espacement minimal
        num_enemies = random.randint(4, 8)
        min_enemy_spacing = 30  # rayon minimal (px) entre ennemis
        
        # Créer une liste des surfaces disponibles (niveaux standardisés + plateformes)
        available_surfaces = []
        
        # Sol principal (niveau 0) - marges divisées par 2
        ground_surface = {
            'x_min': self.overlay_x + 20,
            'x_max': self.overlay_x + self.overlay_w - 20,
            'y': self.platform_levels[0] + 4,  # Niveau sol + demi-hauteur ennemi (divisé par 2)
            'level': 0
        }
        available_surfaces.append(ground_surface)
        
        # Ajouter les plateformes comme surfaces
        platform_surfaces = []
        for platform_info in platforms_info:
            platform_left = platform_info['x'] - platform_info['width'] / 2
            platform_right = platform_info['x'] + platform_info['width'] / 2
            surf = {
                'x_min': platform_left + 5,  # Marge divisée par 2
                'x_max': platform_right - 5,
                'y': platform_info['y'] + 8,  # Surface + demi-hauteur ennemi (divisé par 2)
                'level': platform_info['level']
            }
            platform_surfaces.append(surf)
            available_surfaces.append(surf)
        
        # Placer les ennemis sur les surfaces disponibles en respectant l'espacement
        placed_positions = []  # [(x,y)]

        # 1) Placer au moins la moitié des ennemis au sol
        min_on_ground = (num_enemies + 1) // 2
        ground_placed = 0
        for _ in range(min_on_ground):
            attempts = 0
            placed = False
            while attempts < 100 and not placed:
                if ground_surface['x_max'] <= ground_surface['x_min']:
                    break
                x = random.randint(int(ground_surface['x_min']), int(ground_surface['x_max']))
                y = ground_surface['y']
                ok = True
                for (px, py) in placed_positions:
                    dx = x - px
                    dy = y - py
                    if (dx*dx + dy*dy) < (min_enemy_spacing * min_enemy_spacing):
                        ok = False
                        break
                if ok:
                    enemy = arcade.Sprite()
                    if self.enemy_texture:
                        enemy.texture = self.enemy_texture
                        # Ajuster la taille pour qu'elle soit identique au héros
                        enemy.scale = 0.6  # Même taille que le héros
                        # Positionner l'ennemi avec les pieds sur le sol/plateforme
                        enemy.center_x = x
                        enemy.center_y = y + 20  # Ajustement pour le nouveau scale 0.6
                        print(f"Ennemi créé avec texture PNG à ({x}, {y + 20})")
                    else:
                        # Fallback si la texture n'est pas chargée
                        enemy.texture = arcade.make_soft_square_texture(8, (255, 0, 0), outer_alpha=255)
                        enemy.center_x = x
                        enemy.center_y = y
                        print(f"Ennemi créé avec fallback rouge à ({x}, {y})")
                    self.enemy_list.append(enemy)
                    placed_positions.append((x, y))
                    ground_placed += 1
                    placed = True
                attempts += 1

        # 2) Placer le reste sur n'importe quelle surface (plateformes + sol), avec espacement
        remaining = num_enemies - ground_placed
        for _ in range(remaining):
            attempts = 0
            placed = False
            while attempts < 50 and not placed:
                surface_pool = platform_surfaces if platform_surfaces else [ground_surface]
                surface = random.choice(surface_pool)
                if surface['x_max'] > surface['x_min']:
                    x = random.randint(int(surface['x_min']), int(surface['x_max']))
                    y = surface['y']
                    ok = True
                    for (px, py) in placed_positions:
                        dx = x - px
                        dy = y - py
                        if (dx*dx + dy*dy) < (min_enemy_spacing * min_enemy_spacing):
                            ok = False
                            break
                    if ok:
                        enemy = arcade.Sprite()
                        if self.enemy_texture:
                            enemy.texture = self.enemy_texture
                            # Ajuster la taille pour qu'elle soit identique au héros
                            enemy.scale = 0.6  # Même taille que le héros
                            # Positionner l'ennemi avec les pieds sur le sol/plateforme
                            enemy.center_x = x
                            enemy.center_y = y + 20  # Ajustement pour le nouveau scale 0.6
                            # Ajuster la hitbox pour qu'elle soit touchable 5px plus haut
                            print(f"Ennemi créé avec texture PNG à ({x}, {y + 20})")
                        else:
                            # Fallback si la texture n'est pas chargée
                            enemy.texture = arcade.make_soft_square_texture(8, (255, 0, 0), outer_alpha=255)
                            enemy.center_x = x
                            enemy.center_y = y
                            print(f"Ennemi créé avec fallback rouge à ({x}, {y})")
                        self.enemy_list.append(enemy)
                        placed_positions.append((x, y))
                        placed = True
                attempts += 1
        
        # Artefact (cube jaune) - au niveau du sol
        must_force_artifact = False
        if self.force_artifact_next:
            must_force_artifact = True
            self.force_artifact_next = False
        if must_force_artifact or (random.random() < self.artifact_chance):
            artifact = arcade.Sprite()
            artifact.texture = arcade.make_soft_square_texture(8, (255, 215, 0), outer_alpha=255)  # Or explicite, taille divisée par 2
            # Placer l'artefact dans les 70 derniers pixels à droite
            right_min = max(20, self.overlay_w - 70)
            right_max = self.overlay_w - 20
            artifact.center_x = self.overlay_x + random.randint(int(right_min), int(right_max))
            artifact.center_y = self.platform_levels[0]
            self.artifact_list.append(artifact)

    def _load_hero_textures(self):
        """Charge les textures d'animation de marche du héros"""
        # Cherche les assets dans différents emplacements possibles
        base_candidates = [
            'assets',
            os.path.join(os.path.dirname(__file__), '..', 'assets'),
        ]
        base_candidates = [os.path.normpath(p) for p in base_candidates]
        
        walk_dir = None
        for base in base_candidates:
            walk_path = os.path.join(base, 'walk')
            if os.path.exists(walk_path):
                walk_dir = walk_path
                break
        
        if walk_dir:
            # Charger les frames hero-walk-frame-x.png
            for i in range(4):  # 0, 1, 2, 3
                frame_path = os.path.join(walk_dir, f'hero-walk-frame-{i}.png')
                if os.path.exists(frame_path):
                    try:
                        texture = arcade.load_texture(frame_path)
                        self.hero_walk_textures.append(texture)
                        print(f"Texture héros chargée: {frame_path}")
                    except Exception as e:
                        print(f"Erreur chargement {frame_path}: {e}")
        
        print(f"Textures de marche héros chargées: {len(self.hero_walk_textures)}")
        
        # Si on a des textures, utiliser la première comme texture par défaut
        if self.hero_walk_textures and hasattr(self.hero, 'texture'):
            self.hero.texture = self.hero_walk_textures[0]
    
    def _load_enemy_texture(self):
        """Charge la texture d'ennemi walking_enemie.png"""
        # Cherche les assets dans différents emplacements possibles
        base_candidates = [
            'assets',
            os.path.join(os.path.dirname(__file__), '..', 'assets'),
        ]
        base_candidates = [os.path.normpath(p) for p in base_candidates]
        
        for base in base_candidates:
            # Chercher dans le dossier enemies/
            enemy_path = os.path.join(base, 'enemies', 'walking_enemie.png')
            if os.path.exists(enemy_path):
                try:
                    texture = arcade.load_texture(enemy_path)
                    print(f"Texture ennemis chargée: {enemy_path}")
                    return texture
                except Exception as e:
                    print(f"Erreur chargement texture ennemis {enemy_path}: {e}")
        
        print("Texture walking_enemie.png non trouvée, utilisation du fallback")
        return None
    
    def _update_hero_animation(self, delta_time):
        """Met à jour l'animation de marche du héros - inspiré de l'agent"""
        if not self.hero_walk_textures:
            return  # Pas d'animation si pas de textures
        
        # Déterminer si le héros se déplace ET qu'il est au sol/sur plateforme
        # Animation seulement si le héros marche (pas en saut)
        is_on_ground = self.hero_on_platform or self._is_hero_on_ground()
        self.hero_is_moving = is_on_ground  # Animation seulement au sol/plateforme
        
        # Animation simple comme l'agent : juste changer la texture, pas toucher à la position
        if self.hero_is_moving:
            self.hero_animation_timer += delta_time
            
            # Changer de frame selon la vitesse d'animation
            if self.hero_animation_timer >= self.hero_animation_speed:
                self.hero_animation_timer = 0.0
                self.hero_animation_index = (self.hero_animation_index + 1) % len(self.hero_walk_textures)
                
                # Appliquer la nouvelle texture (comme l'agent, sans toucher à la position)
                if hasattr(self.hero, 'texture'):
                    self.hero.texture = self.hero_walk_textures[self.hero_animation_index]
        
        # Si on a arrêté de bouger (en saut), rester sur la première frame
        elif self.hero_was_moving and not self.hero_is_moving:
            self.hero_animation_index = 0
            self.hero_animation_timer = 0.0
            if hasattr(self.hero, 'texture'):
                self.hero.texture = self.hero_walk_textures[0]
        
        # Mémoriser l'état pour la prochaine frame
        self.hero_was_moving = self.hero_is_moving

    def set_screen_bounds(self, x, y, w, h):
        # Update overlay bounds and recompute level baselines
        dx = x - getattr(self, 'overlay_x', x)
        dy = y - getattr(self, 'overlay_y', y)
        self.overlay_x = x
        self.overlay_y = y
        self.overlay_w = w
        self.overlay_h = h
        self.platform_levels = [
            self.overlay_y + 15,
            self.overlay_y + 15 + self.jump_height,
            self.overlay_y + 15 + self.jump_height * 2,
            self.overlay_y + 15 + self.jump_height * 3,
            self.overlay_y + 15 + self.jump_height * 4,
        ]
        # Translate existing sprites to match overlay move
        def shift_list(sprite_list, dx, dy):
            if sprite_list:
                for s in list(sprite_list):
                    try:
                        s.center_x += dx
                        s.center_y += dy
                    except Exception:
                        pass
        shift_list(self.platform_list, dx, dy)
        shift_list(self.enemy_list, dx, dy)
        shift_list(self.artifact_list, dx, dy)
        shift_list(self.bullet_list, dx, dy)
        shift_list(self.explosion_list, dx, dy)
        if self.hero is not None:
            try:
                self.hero.center_x += dx
                self.hero.center_y += dy
            except Exception:
                pass

    def _hero_overlaps_artifact_lenient(self, artifact):
        """Retourne True si le héros doit ramasser l'artefact avec une tolérance verticale au sol.
        - Chec horizontal: chevauchement en X avec petite marge
        - Chec vertical: les pieds du héros (bas du sprite) ne sont pas trop haut au-dessus de l'artefact
        """
        try:
            hero_w, hero_h = self._get_hero_dimensions()
            hero_left = self.hero.center_x - hero_w / 2.0
            hero_right = self.hero.center_x + hero_w / 2.0
            hero_bottom = self.hero.center_y - hero_h / 2.0
        except Exception:
            hero_left = self.hero.center_x - 10.0
            hero_right = self.hero.center_x + 10.0
            hero_bottom = self.hero.center_y - 10.0
        try:
            aw = float(getattr(artifact, 'width', 8.0))
            ah = float(getattr(artifact, 'height', 8.0))
        except Exception:
            aw, ah = 8.0, 8.0
        art_left = artifact.center_x - aw / 2.0
        art_right = artifact.center_x + aw / 2.0
        art_top = artifact.center_y + ah / 2.0
        # Marges
        margin_x = 6.0
        margin_y = 12.0
        horizontal_ok = (hero_right >= art_left - margin_x) and (hero_left <= art_right + margin_x)
        vertical_ok = (hero_bottom <= art_top + margin_y)
        return horizontal_ok and vertical_ok
