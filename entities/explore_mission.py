import arcade
import random
import time
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

        self.gravity = 0.5
        self.move_speed = 0.7
        self.jump_strength = 8.0
        
        # Système de hauteurs standardisées (divisé par 2) avec plus de niveaux
        self.jump_height = 25  # Hauteur qu'un saut peut atteindre (en pixels)
        self.platform_levels = [
            SURVEILLANCE_SCREEN_Y + 15,  # Niveau sol (0)
            SURVEILLANCE_SCREEN_Y + 15 + self.jump_height,  # Niveau 1
            SURVEILLANCE_SCREEN_Y + 15 + self.jump_height * 2,  # Niveau 2
            SURVEILLANCE_SCREEN_Y + 15 + self.jump_height * 3,  # Niveau 3
            SURVEILLANCE_SCREEN_Y + 15 + self.jump_height * 4,  # Niveau 4
            SURVEILLANCE_SCREEN_Y + 15 + self.jump_height * 5,  # Niveau 5
        ]
        self.last_shot_time = 0
        self.last_enemy_shot = 0  # Pour les tirs d'ennemis
        self.start_time = time.time()
        
        # Système de téléportation et patterns
        self.pattern_generated = False
        self.artifact_chance = 2  # 5% de chance d'apparition d'artefact
        self.evaluated_platforms = set()  # Plateformes déjà évaluées pour le saut

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

        # Réduire la taille du héros pour cette mission seulement
        self.hero.scale = 0.5  # Diviser la taille par 2

        # Positionner le héros au sol côté gauche (niveau 0)
        self.hero.center_x = SURVEILLANCE_SCREEN_X + 20
        self.hero.center_y = self.platform_levels[0]  # Exactement au niveau du sol
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

        # Vérifier si le héros atteint le bord droit de l'écran
        if self.hero.center_x >= SURVEILLANCE_SCREEN_X + SURVEILLANCE_SCREEN_WIDTH - 20:
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
                
                # Déterminer le niveau actuel du héros
                hero_current_level = 0  # Par défaut au sol
                for i, level_y in enumerate(self.platform_levels):
                    if abs(self.hero.center_y - level_y) < 10:  # Tolérance de 10 pixels
                        hero_current_level = i
                        break
                
                # Déterminer le niveau de la plateforme
                platform_level = 0
                for i, level_y in enumerate(self.platform_levels):
                    if abs(platform.center_y - level_y) < 10:  # Tolérance de 10 pixels
                        platform_level = i
                        break
                
                # Conditions pour sauter :
                # 1. Le héros doit être à gauche du côté gauche de la plateforme
                # 2. La plateforme doit être EXACTEMENT 1 niveau au-dessus du héros
                # 3. La plateforme doit être dans une distance raisonnable devant le héros
                hero_distance_to_platform = platform_left - self.hero.center_x
                
                if (self.hero.center_x < platform_left and  # Héros à gauche du côté gauche
                    platform_level == hero_current_level + 1 and  # Exactement 1 niveau au-dessus
                    0 < hero_distance_to_platform < 20):    # Distance raisonnable (0-20 pixels)
                    
                    # Marquer cette plateforme comme évaluée
                    self.evaluated_platforms.add(platform_id)
                    
                    # 50% de chance de sauter (une seule fois par plateforme)
                    if random.random() < 0.8:
                        should_jump = True
                        break
            
            # Saut intelligent seulement (pas de saut aléatoire)
            if (should_jump and current_velocity_y == 0):
                current_velocity_y = self.jump_strength
            
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
                    hero_height = 8  # Héros réduit : 16 * 0.5 = 8 pixels
                    hero_bottom = self.hero.center_y - hero_height / 2
                    hero_top = self.hero.center_y + hero_height / 2
                    
                    # Collision horizontale seulement si :
                    # 1. Le héros est au niveau vertical de la plateforme
                    # 2. Il n'est pas en train de tomber rapidement
                    # 3. Il essaie vraiment de traverser horizontalement
                    if (hero_bottom < platform_top - 5 and hero_top > platform_bottom + 5 and  # Au niveau vertical avec marge
                        abs(current_velocity_y) < 2):  # Pas en train de tomber rapidement
                        hero_width = 8  # Héros réduit : 16 * 0.5 = 8 pixels
                        # Seulement repousser si vraiment sur le côté gauche de la plateforme
                        if self.hero.center_x > platform_left and self.hero.center_x < platform_right:
                            self.hero.center_x = platform_left - hero_width / 2
            
            # Limites écran horizontales
            left_bound = SURVEILLANCE_SCREEN_X + 20
            right_bound = SURVEILLANCE_SCREEN_X + SURVEILLANCE_SCREEN_WIDTH - 20
            if self.hero.center_x > right_bound:
                self.hero.center_x = right_bound
            if self.hero.center_x < left_bound:
                self.hero.center_x = left_bound

            # Mouvement vertical avec collisions plateformes
            self.hero.center_y += current_velocity_y
            hits = arcade.check_for_collision_with_list(self.hero, self.platform_list)
            if hits:
                # Se poser sur la plateforme seulement si on tombe dessus (pas si on la traverse)
                if current_velocity_y <= 0:  # Seulement quand on tombe
                    hero_height = 8  # Héros réduit : 16 * 0.5 = 8 pixels
                    top = max((s.center_y + (s.texture.height if hasattr(s, 'texture') and s.texture else 15) / 2) for s in hits)
                    self.hero.center_y = top + hero_height / 2
                    current_velocity_y = 0
            
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
            if (bullet.center_x > SURVEILLANCE_SCREEN_X + SURVEILLANCE_SCREEN_WIDTH + 20 or
                bullet.center_x < SURVEILLANCE_SCREEN_X - 20):
                bullet.remove_from_sprite_lists()
            
            # Collision balles d'ennemis avec le héros
            if (hasattr(bullet, 'change_x') and bullet.change_x < 0 and  # Balle qui va vers la gauche (ennemi)
                arcade.check_for_collision(bullet, self.hero)):
                bullet.remove_from_sprite_lists()
                self.hero.health = max(0, self.hero.health - 3)  # Moins de dégâts que contact direct
                if self.hero.health <= 0:
                    hero_boom = Explosion(self.hero.center_x, self.hero.center_y)
                    self.explosion_list.append(hero_boom)
                    self.success = False
                    self.end_mission()

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
                
                # Le héros perd de la vie mais continue sa progression
                self.hero.health = max(0, self.hero.health - 5)
                if self.hero.health <= 0:
                    hero_boom = Explosion(self.hero.center_x, self.hero.center_y)
                    self.explosion_list.append(hero_boom)
                    self.success = False  # Mission échouée si le héros meurt
                    self.end_mission()

        self.explosion_list.update()

        # Vérifier récupération de l'artefact
        if len(self.artifact_list) > 0 and arcade.check_for_collision(self.hero, self.artifact_list[0]):
            self.success = True
            # Effet simple
            fx = Explosion(self.artifact_list[0].center_x, self.artifact_list[0].center_y)
            self.explosion_list.append(fx)
            self.artifact_list[0].remove_from_sprite_lists()
            self.end_mission()

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
        # Téléporter le héros au début de l'écran (niveau sol)
        self.hero.center_x = SURVEILLANCE_SCREEN_X + 20
        self.hero.center_y = self.platform_levels[0]  # Exactement au niveau du sol
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
        # Sol de base (divisé par 2)
        ground = arcade.Sprite()
        ground.texture = arcade.make_soft_square_texture(10, (0, 100, 0), outer_alpha=255)  # Vert foncé explicite
        ground.scale_x = SURVEILLANCE_SCREEN_WIDTH / 10
        ground.scale_y = 1
        ground.center_x = SURVEILLANCE_SCREEN_X + SURVEILLANCE_SCREEN_WIDTH // 2
        ground.center_y = SURVEILLANCE_SCREEN_Y + 10
        self.platform_list.append(ground)
        
        # Plateformes à hauteurs standardisées avec génération intelligente
        num_platforms = random.randint(8, 14)
        platforms_info = []  # Pour éviter les superpositions
        
        # Générer une progression logique de niveaux
        max_level = random.randint(3, len(self.platform_levels) - 1)  # Niveau maximum pour ce pattern
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
                width = random.randint(30, 60)  # Largeur divisée par 2
                height = 8  # Hauteur divisée par 2
                x = SURVEILLANCE_SCREEN_X + random.randint(40, SURVEILLANCE_SCREEN_WIDTH - 40)  # Marges divisées par 2
                
                y = self.platform_levels[level]
                
                # Vérifier les superpositions avec les plateformes existantes
                overlap = False
                for existing in platforms_info:
                    # Vérifier seulement la superposition horizontale puisque les hauteurs sont standardisées
                    if (abs(x - existing['x']) < (width + existing['width']) / 2 + 15):  # Espacement divisé par 2
                        overlap = True
                        break
                
                if not overlap:
                    platform = arcade.Sprite()
                    platform.texture = arcade.make_soft_square_texture(8, (139, 69, 19), outer_alpha=255)  # Marron explicite, taille divisée par 2
                    platform.scale_x = width / 8
                    platform.scale_y = height / 8
                    platform.center_x = x
                    platform.center_y = y
                    self.platform_list.append(platform)
                    platforms_info.append({'x': x, 'y': y, 'width': width, 'height': height, 'level': level})
                    break
                
                attempts += 1
        
        # Ennemis statiques (tous en rouge) placés sur des surfaces (2x plus nombreux)
        num_enemies = random.randint(4, 8)
        
        # Créer une liste des surfaces disponibles (niveaux standardisés + plateformes)
        available_surfaces = []
        
        # Sol principal (niveau 0) - marges divisées par 2
        available_surfaces.append({
            'x_min': SURVEILLANCE_SCREEN_X + 20,
            'x_max': SURVEILLANCE_SCREEN_X + SURVEILLANCE_SCREEN_WIDTH - 20,
            'y': self.platform_levels[0] + 4,  # Niveau sol + demi-hauteur ennemi (divisé par 2)
            'level': 0
        })
        
        # Ajouter les plateformes comme surfaces
        for platform_info in platforms_info:
            platform_left = platform_info['x'] - platform_info['width'] / 2
            platform_right = platform_info['x'] + platform_info['width'] / 2
            available_surfaces.append({
                'x_min': platform_left + 5,  # Marge divisée par 2
                'x_max': platform_right - 5,
                'y': platform_info['y'] + 8,  # Surface + demi-hauteur ennemi (divisé par 2)
                'level': platform_info['level']
            })
        
        # Placer les ennemis sur les surfaces disponibles
        for _ in range(num_enemies):
            if available_surfaces:
                surface = random.choice(available_surfaces)
                if surface['x_max'] > surface['x_min']:  # Vérifier qu'il y a de la place
                    enemy = arcade.Sprite()
                    enemy.texture = arcade.make_soft_square_texture(8, (255, 0, 0), outer_alpha=255)  # Rouge explicite, taille divisée par 2
                    enemy.center_x = random.randint(int(surface['x_min']), int(surface['x_max']))
                    enemy.center_y = surface['y']
                    self.enemy_list.append(enemy)
        
        # Artefact (cube jaune, 5% de chance) - TOUJOURS au niveau du sol
        if random.random() < self.artifact_chance:
            artifact = arcade.Sprite()
            artifact.texture = arcade.make_soft_square_texture(8, (255, 215, 0), outer_alpha=255)  # Or explicite, taille divisée par 2
            artifact.center_x = SURVEILLANCE_SCREEN_X + random.randint(SURVEILLANCE_SCREEN_WIDTH//2, SURVEILLANCE_SCREEN_WIDTH - 20)  # Marge divisée par 2
            artifact.center_y = self.platform_levels[0]
            self.artifact_list.append(artifact)


