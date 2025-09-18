import arcade
import random
import time
import os
from utils.constants import (
    SURVEILLANCE_SCREEN_WIDTH, SURVEILLANCE_SCREEN_HEIGHT, SURVEILLANCE_SCREEN_X, SURVEILLANCE_SCREEN_Y,
    PLAYER_SCALING, ENEMY_SCALING, BULLET_SCALING, EXPLOSION_SCALING,
    ENEMY_SPEED, BULLET_SPEED, SPAWN_INTERVAL, GAME_DURATION,
    HERO_STATE_FIGHTING, HERO_STATE_FAILED
)


class Explosion(arcade.Sprite):
    """Sprite d'explosion temporaire"""
    def __init__(self, x, y):
        # Créer une explosion plus grande et plus visible
        super().__init__(arcade.make_circle_texture(50, arcade.color.ORANGE), EXPLOSION_SCALING)
        self.center_x = x
        self.center_y = y
        self.start_time = time.time()
        self.initial_scale = EXPLOSION_SCALING
        self.max_scale = EXPLOSION_SCALING * 2.0  # L'explosion grandit

    def update(self, delta_time=0):
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        # Animation de l'explosion : elle grandit puis rétrécit
        if elapsed < 0.15:  # Première moitié : grandir
            progress = elapsed / 0.15
            self.scale = self.initial_scale + (self.max_scale - self.initial_scale) * progress
        else:  # Deuxième moitié : rétrécir et disparaître
            progress = (elapsed - 0.15) / 0.15
            self.scale = self.max_scale - (self.max_scale - self.initial_scale * 0.1) * progress
            # Changer la couleur vers le rouge à la fin
            if progress > 0.5:
                self.texture = arcade.make_circle_texture(50, arcade.color.RED)
        
        # Disparition après 0.3 secondes
        if elapsed > 0.3:
            self.remove_from_sprite_lists()


class TextureExplosion(arcade.Sprite):
    """Explosion basée sur une image PNG (ex: Circle_explosion3.png)"""
    def __init__(self, x: float, y: float, filename: str = 'Circle_explosion3.png'):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.start_time = time.time()
        self.initial_scale = 0.6
        self.max_scale = 1.1
        # Localiser le fichier dans assets (recherche récursive)
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
        except Exception:
            texture = None
        if texture is not None:
            self.texture = texture
            # Mise à l'échelle automatique vers ~64px de haut
            try:
                raw_h = float(texture.height)
                desired_h = 64.0
                self.scale = desired_h / raw_h if raw_h > 0 else self.initial_scale
            except Exception:
                self.scale = self.initial_scale
        else:
            # Fallback sur explosion simple si image absente
            self.texture = arcade.make_circle_texture(50, arcade.color.ORANGE)
            self.scale = self.initial_scale

    def update(self, delta_time=0):
        elapsed = time.time() - self.start_time
        if elapsed < 0.15:
            progress = elapsed / 0.15
            self.scale = self.initial_scale + (self.max_scale - self.initial_scale) * progress
        else:
            progress = (elapsed - 0.15) / 0.15
            self.scale = self.max_scale - (self.max_scale - self.initial_scale * 0.1) * progress
        if elapsed > 0.3:
            self.remove_from_sprite_lists()


class ShipExplosion(arcade.Sprite):
    """Explosion rapide et grosse pour les explosions du vaisseau"""
    def __init__(self, x: float, y: float, filename: str = 'Circle_explosion3.png'):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.start_time = time.time()
        self.initial_scale = 1.5  # Plus grosse
        self.max_scale = 2.5      # Encore plus grosse
        # Localiser le fichier dans assets (recherche récursive)
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
            # Recherche directe à la racine
            candidate = os.path.join(base, filename)
            if os.path.exists(candidate):
                found = candidate
                break
            # Recherche récursive
            for root, _dirs, files in os.walk(base):
                for fname in files:
                    if fname.lower() == filename.lower():
                        found = os.path.join(root, fname)
                        break
                if found:
                    break
            if found:
                break
        if found:
            try:
                texture = arcade.load_texture(found)
                self.texture = texture
                self.scale = self.initial_scale
            except Exception:
                # Fallback: créer une texture colorée
                self.texture = arcade.make_circle_texture(50, arcade.color.ORANGE)
                self.scale = self.initial_scale
        else:
            # Fallback: créer une texture colorée
            self.texture = arcade.make_circle_texture(50, arcade.color.ORANGE)
            self.scale = self.initial_scale

    def update(self, delta_time=0):
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        # Animation rapide : grandir puis rétrécir en 0.2 secondes
        if elapsed < 0.1:  # Première moitié : grandir
            progress = elapsed / 0.1
            self.scale = self.initial_scale + (self.max_scale - self.initial_scale) * progress
        else:  # Deuxième moitié : rétrécir et disparaître
            progress = (elapsed - 0.1) / 0.1
            self.scale = self.max_scale - (self.max_scale - self.initial_scale * 0.1) * progress
        
        # Disparition après 0.2 secondes
        if elapsed > 0.2:
            self.remove_from_sprite_lists()


class BattleMission:
    def __init__(self, hero, enemies_to_kill=None, on_game_over_callback=None, on_game_end_callback=None):
        # Listes de sprites
        self.player_list = None
        self.enemy_list = None
        self.bullet_list = None
        self.enemy_bullet_list = None
        self.explosion_list = None

        self.hero = hero
        self.player_sprite = None
        
        # Charger les textures pour les ennemis et le héros
        self.enemy_texture = self._load_enemy_texture()
        self.hero_ship_texture = self._load_hero_ship_texture()
        
        # Callbacks pour les scènes de fin de jeu
        self.on_game_over_callback = on_game_over_callback
        self.on_game_end_callback = on_game_end_callback
        self.last_enemy_spawn = 0
        self.last_bullet_shot = 0
        self.start_time = time.time()
        self.mission_duration = GAME_DURATION
        self.is_active = False
        self.mission_completed = False
        self.enemies_destroyed = 0
        # Nombre d'ennemis choisi aléatoirement entre 40 et 60 (le boss compte comme 1 ennemi)
        self.enemies_to_kill = enemies_to_kill if enemies_to_kill is not None else random.randint(20, 40)
        self.boss_counted = False  # Pour s'assurer que le boss n'est compté qu'une fois
        
        # Boss
        self.boss_active = False
        self.boss_sprite = None
        self.boss_list = None
        self.boss_death_time = None  # Pour le délai après la mort du boss
        self.boss_death_x = None  # Position X du boss à sa mort
        self.boss_death_y = None  # Position Y du boss à sa mort
        self.last_continuous_explosion = None  # Dernière explosion continue
        
        # Effet de défaite du héros
        self.hero_death_time = None  # Moment de la mort du héros
        self.hero_death_x = None  # Position X du héros à sa mort
        self.hero_death_y = None  # Position Y du héros à sa mort
        self.screen_red_filter = False  # Filtre rouge sur l'écran
        self.screen_black = False  # Écran noir
        self.final_explosion_time = None  # Moment de l'explosion finale
        self.ship_explosion_list = arcade.SpriteList()  # Explosions sur le vaisseau
        self.boss_health = 100
        self.boss_max_health = 100
        self.boss_bullet_list = None
        self.last_boss_shot = 0
        # Résultat
        self.success = False
        
        # Bounds of the surveillance overlay (can be updated by the scene)
        self.overlay_x = SURVEILLANCE_SCREEN_X
        self.overlay_y = SURVEILLANCE_SCREEN_Y
        self.overlay_w = SURVEILLANCE_SCREEN_WIDTH + 20
        self.overlay_h = SURVEILLANCE_SCREEN_HEIGHT
    
    def setup_battle(self):
        """Initialisation du jeu"""
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.enemy_bullet_list = arcade.SpriteList()
        self.boss_list = arcade.SpriteList()
        self.boss_bullet_list = arcade.SpriteList()
        self.explosion_list = arcade.SpriteList()

        # Héros de la mission (crée un nouveau sprite avec la texture du vaisseau)
        self.player_sprite = arcade.Sprite()
        if self.hero_ship_texture:
            self.player_sprite.texture = self.hero_ship_texture
            self.player_sprite.scale = 0.4  # Ajuster la taille selon l'image
            print("Vaisseau héros créé avec texture PNG")
        else:
            # Fallback si la texture n'est pas chargée
            self.player_sprite.texture = arcade.make_soft_square_texture(40, arcade.color.BLUE, outer_alpha=255)
            print("Vaisseau héros créé avec fallback bleu")
        
        self.player_sprite.center_x = self.overlay_x + 60
        self.player_sprite.center_y = self.overlay_y + self.overlay_h // 2
        self.player_list.append(self.player_sprite)
        
        self.last_enemy_spawn = 0
        self.last_bullet_shot = 0
        self.start_time = time.time()
        self.enemies_destroyed = 0
        self.mission_completed = False
        # Réinitialiser boss
        self.boss_active = False
        self.boss_sprite = None
        self.boss_health = 150
        self.boss_max_health = 150
        self.last_boss_shot = 0
        self.success = False
        # Le nombre d'ennemis est déjà défini dans __init__
    
    def start_mission(self):
        self.is_active = True
        self.setup_battle()
        print("Mission de bataille galactique commencée !")
    
    def end_mission(self):
        self.is_active = False
        self.mission_completed = True
        status = "réussie" if self.success else "échouée"
        print(f"Mission {status} ! Ennemis détruits : {self.enemies_destroyed}/{self.enemies_to_kill}")
        
        print(f"Mission completed flag: {self.mission_completed}")
        print(f"Mission active flag: {self.is_active}")
    
    def end_mission_final(self):
        """Termine la mission finale - le héros ne revient pas au vaisseau (réussite ou défaite)"""
        self.is_active = False
        self.mission_completed = True
        status = "RÉUSSIE" if self.success else "ÉCHOUÉE"
        print(f"MISSION FINALE {status} - Le héros ne reviendra pas au vaisseau")
        print(f"Mission completed flag: {self.mission_completed}")
        print(f"Mission active flag: {self.is_active}")
        
        # Déclencher la scène appropriée
        if self.success and self.on_game_end_callback:
            print("Déclenchement de la scène de victoire")
            self.on_game_end_callback()
        elif not self.success and self.on_game_over_callback:
            print("Déclenchement de la scène de défaite")
            self.on_game_over_callback()
    
    def update(self, delta_time):
        if not self.is_active:
            return
        
        # Vérifier l'effet de défaite du héros
        if hasattr(self, 'hero_death_time') and self.hero_death_time is not None:
            elapsed = time.time() - self.hero_death_time
            
            if elapsed < 0.5:  # 0.5s : explosion du héros
                if elapsed < 0.1 and len(self.explosion_list) == 0:  # Créer l'explosion du héros au début
                    hero_explosion = TextureExplosion(self.hero_death_x, self.hero_death_y, 'Circle_explosion3.png')
                    self.explosion_list.append(hero_explosion)
            elif elapsed < 1.0:  # 0.5-1.0s : écran noir sur la télé
                self.screen_black = True
                self.screen_red_filter = False
            elif elapsed < 2.0:  # 1.0-2.0s : clignotement rouge sur tout l'écran
                self.screen_black = False
                self.screen_red_filter = True
            else:  # 2.0s+ : explosions continues pendant 10 secondes
                if self.final_explosion_time is None:
                    self.final_explosion_time = time.time()
                
                # Créer des explosions continues toutes les 0.1 secondes
                if time.time() - self.final_explosion_time >= 0.1:
                    explosion_textures = ['Circle_explosion3.png', 'Circle_explosion4.png', 'Circle_explosion5.png', 'Circle_explosion6.png']
                    # Créer 3-5 explosions aléatoires à chaque cycle
                    for i in range(random.randint(3, 5)):
                        explosion_x = random.randint(0, 3000)  # Largeur du vaisseau
                        explosion_y = random.randint(0, 1000)  # Hauteur du vaisseau
                        explosion_texture = random.choice(explosion_textures)
                        ship_explosion = ShipExplosion(explosion_x, explosion_y, explosion_texture)
                        self.ship_explosion_list.append(ship_explosion)
                    self.final_explosion_time = time.time()
                
                # Mettre à jour les explosions du vaisseau pour qu'elles disparaissent
                self.ship_explosion_list.update()
                
                if elapsed >= 12.0:  # Terminer après 12 secondes - MISSION FINALE
                    self.end_mission_final()  # Mission finale, le héros ne revient pas
            return  # Ne pas continuer l'update pendant l'effet de défaite
        
        # Vérifier si on doit terminer la mission après la mort du boss
        if hasattr(self, 'boss_death_time') and self.boss_death_time is not None:
            # Créer des explosions continues pendant le délai
            if time.time() - self.last_continuous_explosion >= 0.15:  # Nouvelle explosion toutes les 0.15 secondes
                # Supprimer les anciennes explosions pour éviter l'accumulation
                self.explosion_list.clear()
                
                explosion_textures = ['Circle_explosion3.png', 'Circle_explosion4.png', 'Circle_explosion5.png', 'Circle_explosion6.png']
                # Créer 2-3 explosions aléatoires autour de la position du boss
                for i in range(random.randint(3, 5)):
                    explosion_x = self.boss_death_x + random.uniform(-40, 40)
                    explosion_y = self.boss_death_y + random.uniform(-40, 40)
                    explosion_texture = random.choice(explosion_textures)
                    continuous_explosion = TextureExplosion(explosion_x, explosion_y, explosion_texture)
                    self.explosion_list.append(continuous_explosion)
                self.last_continuous_explosion = time.time()
            
            if time.time() - self.boss_death_time >= 2.0:  # 2 secondes de délai (réduit)
                self.end_mission_final()  # Mission finale réussie - le héros ne revient pas
                self.boss_death_time = None
            return  # Ne pas continuer l'update pendant le délai
        
        # Déclencher le boss quand le quota d'ennemis normaux est atteint
        if (not self.boss_active) and (self.enemies_destroyed >= self.enemies_to_kill - 1):
            self.spawn_boss()
            # Compter le boss comme un ennemi à tuer
            if not self.boss_counted:
                self.boss_counted = True

        # Spawn d'ennemis (désactivé quand le boss est présent)
        if (not self.boss_active) and (time.time() - self.last_enemy_spawn > SPAWN_INTERVAL):
            enemy = arcade.Sprite()
            if self.enemy_texture:
                enemy.texture = self.enemy_texture
                enemy.scale = 0.3  # Ajuster la taille selon l'image
                print("Ennemi volant créé avec texture PNG")
            else:
                # Fallback si la texture n'est pas chargée
                enemy.texture = arcade.make_soft_square_texture(30, arcade.color.RED, outer_alpha=255)
                print("Ennemi volant créé avec fallback rouge")
            
            # Spawn encore 20px plus à gauche (désormais à l'intérieur de l'overlay)
            enemy.center_x = self.overlay_x + self.overlay_w - 20
            enemy.center_y = random.randint(
                int(self.overlay_y + 20), 
                int(self.overlay_y + self.overlay_h - 20)
            )
            enemy.change_x = -ENEMY_SPEED
            self.enemy_list.append(enemy)
            self.last_enemy_spawn = time.time()

        # Mouvement automatique du héros
        self.update_hero_movement()

        # Tir automatique du héros
        if time.time() - self.last_bullet_shot > 0.3:
            bullet = arcade.SpriteSolidColor(10, 4, arcade.color.YELLOW)
            bullet.center_x = self.player_sprite.center_x + 20
            bullet.center_y = self.player_sprite.center_y
            bullet.change_x = BULLET_SPEED
            self.bullet_list.append(bullet)
            self.last_bullet_shot = time.time()

        # Tir des ennemis - chaque ennemi a son propre timing
        current_time = time.time()
        for enemy in self.enemy_list:
            # Initialiser le timing de tir pour chaque ennemi
            if not hasattr(enemy, 'last_shot_time'):
                enemy.last_shot_time = current_time - random.uniform(0.2, 1.2)  # Permettre de tirer immédiatement
                enemy.shot_interval = random.uniform(0.5, 1.0)  # Intervalle fixe pour cet ennemi
                print(f"Ennemi initialisé - intervalle: {enemy.shot_interval:.2f}s")
            
            # Vérifier si cet ennemi peut tirer
            time_since_last_shot = current_time - enemy.last_shot_time
            if time_since_last_shot > enemy.shot_interval:
                print(f"Ennemi tire ! Temps écoulé: {time_since_last_shot:.2f}s, intervalle: {enemy.shot_interval:.2f}s")
                enemy_bullet = arcade.SpriteSolidColor(8, 3, arcade.color.RED)
                enemy_bullet.center_x = enemy.center_x - 15
                enemy_bullet.center_y = enemy.center_y
                enemy_bullet.change_x = -BULLET_SPEED * 0.7  # Plus lent que les balles du héros
                self.enemy_bullet_list.append(enemy_bullet)
                enemy.last_shot_time = current_time
                # Changer l'intervalle pour le prochain tir
                enemy.shot_interval = random.uniform(0.5, 1.2)

        # Tir du boss (salves) si actif
        if self.boss_active and self.boss_sprite is not None:
            if current_time - self.last_boss_shot > 0.4:
                for _ in range(3):
                    boss_bullet = arcade.SpriteSolidColor(10, 4, arcade.color.PURPLE)
                    boss_bullet.center_x = self.boss_sprite.center_x - 25
                    boss_bullet.center_y = self.boss_sprite.center_y + random.randint(-100, 100)
                    boss_bullet.change_x = -BULLET_SPEED * 0.9
                    boss_bullet.change_y = random.uniform(-1.5, 1.5)
                    self.boss_bullet_list.append(boss_bullet)
                self.last_boss_shot = current_time

        # Mettre à jour positions (ne pas appeler update() du héros pour éviter la récursion)
        self.enemy_list.update()
        self.bullet_list.update()
        self.enemy_bullet_list.update()
        self.boss_bullet_list.update()
        self.explosion_list.update()

        # Supprimer ennemis/bullets hors écran
        for enemy in list(self.enemy_list):
            # Despawn encore 20px plus à droite (à l'intérieur de l'overlay)
            if enemy.center_x < self.overlay_x + 20:
                enemy.remove_from_sprite_lists()
        for bullet in list(self.bullet_list):
            # Hero bullets (right-moving) despawn 20px before the right edge
            if bullet.center_x > self.overlay_x + self.overlay_w - 20:
                bullet.remove_from_sprite_lists()
        for enemy_bullet in list(self.enemy_bullet_list):
            # Enemy bullets (left-moving) despawn 20px after the left edge
            if enemy_bullet.center_x < self.overlay_x + 20:
                enemy_bullet.remove_from_sprite_lists()
        for boss_bullet in list(self.boss_bullet_list):
            # Boss bullets (left-moving) despawn 20px after the left edge
            if boss_bullet.center_x < self.overlay_x + 20:
                boss_bullet.remove_from_sprite_lists()

        # Collision balles/ennemis
        for bullet in self.bullet_list:
            hit_list = arcade.check_for_collision_with_list(bullet, self.enemy_list)
            if hit_list:
                bullet.remove_from_sprite_lists()
                for enemy in hit_list:
                    explosion = TextureExplosion(enemy.center_x, enemy.center_y, 'Circle_explosion3.png')
                    self.explosion_list.append(explosion)
                    enemy.remove_from_sprite_lists()
                    self.enemies_destroyed += 1

        # Collision balles/boss
        if self.boss_active and self.boss_sprite is not None:
            for bullet in list(self.bullet_list):
                if arcade.check_for_collision(bullet, self.boss_sprite):
                    bullet.remove_from_sprite_lists()
                    self.boss_health -= 5
                    impact = TextureExplosion(bullet.center_x, bullet.center_y, 'Circle_explosion3.png')
                    self.explosion_list.append(impact)
                    if self.boss_health <= 0:
                        # Créer plusieurs explosions autour du boss
                        boss_x, boss_y = self.boss_sprite.center_x, self.boss_sprite.center_y
                        explosion_textures = ['Circle_explosion3.png', 'Circle_explosion4.png', 'Circle_explosion5.png', 'Circle_explosion6.png']
                        for i in range(6):  # 6 explosions
                            # Position aléatoire autour du boss (rayon de 30-60 pixels)
                            angle = random.uniform(0, 2 * 3.14159)
                            distance = random.uniform(30, 60)
                            explosion_x = boss_x + distance * random.uniform(-1, 1)
                            explosion_y = boss_y + distance * random.uniform(-1, 1)
                            # Choisir une texture d'explosion aléatoire
                            explosion_texture = random.choice(explosion_textures)
                            boss_explosion = TextureExplosion(explosion_x, explosion_y, explosion_texture)
                            self.explosion_list.append(boss_explosion)
                        
                        self.boss_sprite.remove_from_sprite_lists()
                        self.boss_active = False
                        self.enemies_destroyed += 1  # Compter le boss comme un ennemi détruit
                        self.success = True
                        # Délai pour laisser voir les explosions avant de terminer la mission
                        self.boss_death_time = time.time()
                        # Position du boss pour les explosions continues
                        self.boss_death_x = boss_x
                        self.boss_death_y = boss_y
                        self.last_continuous_explosion = time.time()

        # Collision ennemis / héros (le héros prend des dégâts)
        for enemy in list(self.enemy_list):
            if arcade.check_for_collision(enemy, self.player_sprite):
                # L'ennemi explose (il est détruit)
                explosion = TextureExplosion(enemy.center_x, enemy.center_y, 'Circle_explosion3.png')
                self.explosion_list.append(explosion)
                enemy.remove_from_sprite_lists()
                # Appliquer des dégâts au héros
                damage = 3
                self.hero.health = max(0, self.hero.health - damage)
                # Mettre à jour l'état du héros
                if self.hero.health <= 0:
                    # Déclencher l'effet de défaite du héros
                    self.hero_death_time = time.time()
                    self.hero_death_x = self.hero.center_x
                    self.hero_death_y = self.hero.center_y
                    self.screen_black = True
                    self.success = False
                    self.hero.state = HERO_STATE_FAILED
                else:
                    self.hero.state = HERO_STATE_FIGHTING

        # Collision balles ennemies / héros
        for enemy_bullet in list(self.enemy_bullet_list):
            if arcade.check_for_collision(enemy_bullet, self.player_sprite):
                # La balle explose (elle est détruite)
                enemy_bullet.remove_from_sprite_lists()
                # Appliquer des dégâts au héros
                damage = 5  # Moins de dégâts que les collisions directes
                self.hero.health = max(0, self.hero.health - damage)
                # Mettre à jour l'état du héros
                if self.hero.health <= 0:
                    # Déclencher l'effet de défaite du héros (même logique que collision ennemis)
                    self.hero_death_time = time.time()
                    self.hero_death_x = self.hero.center_x
                    self.hero_death_y = self.hero.center_y
                    self.screen_black = True
                    self.success = False
                    self.hero.state = HERO_STATE_FAILED
                else:
                    # Le héros reste en état de combat (pas d'explosion)
                    self.hero.state = HERO_STATE_FIGHTING

        # Collision balles du boss / héros
        for boss_bullet in list(self.boss_bullet_list):
            if arcade.check_for_collision(boss_bullet, self.player_sprite):
                boss_bullet.remove_from_sprite_lists()
                damage = 10
                self.hero.health = max(0, self.hero.health - damage)
                if self.hero.health <= 0:
                    # Déclencher l'effet de défaite du héros (même logique que les autres)
                    self.hero_death_time = time.time()
                    self.hero_death_x = self.hero.center_x
                    self.hero_death_y = self.hero.center_y
                    self.screen_black = True
                    self.success = False
                    self.hero.state = HERO_STATE_FAILED
                else:
                    self.hero.state = HERO_STATE_FIGHTING
    
    def update_hero_movement(self):
        """Mouvement automatique aléatoire du héros"""
        # Initialiser les variables de mouvement aléatoire
        if not hasattr(self, 'hero_timer'):
            self.hero_timer = 0
            self.hero_direction_x = random.choice([-1, 1])
            self.hero_direction_y = random.choice([-1, 1])
            self.hero_speed = random.uniform(0.3, 0.8)
        
        self.hero_timer += 1
        
        # Changer de direction aléatoirement toutes les 30-60 frames
        if self.hero_timer > random.randint(30, 60):
            self.hero_timer = 0
            self.hero_direction_x = random.choice([-1, 1])
            self.hero_direction_y = random.choice([-1, 1])
            self.hero_speed = random.uniform(0.3, 0.8)
        
        # Déplacer le héros dans toutes les directions
        self.player_sprite.center_x += self.hero_direction_x * self.hero_speed
        self.player_sprite.center_y += self.hero_direction_y * self.hero_speed
        
        # Limites de l'écran de surveillance (côté gauche seulement)
        screen_left = self.overlay_x + 20
        screen_right = self.overlay_x + self.overlay_w // 2  # Moitié gauche seulement
        screen_bottom = self.overlay_y + 20
        screen_top = self.overlay_y + self.overlay_h - 20
        
        # Inverser la direction aux bords
        if self.player_sprite.center_x <= screen_left or self.player_sprite.center_x >= screen_right:
            self.hero_direction_x *= -1
        if self.player_sprite.center_y <= screen_bottom or self.player_sprite.center_y >= screen_top:
            self.hero_direction_y *= -1
        
        # Maintenir dans les limites
        self.player_sprite.center_x = max(screen_left, min(screen_right, self.player_sprite.center_x))
        self.player_sprite.center_y = max(screen_bottom, min(screen_top, self.player_sprite.center_y))
    
    def is_mission_finished(self):
        # Vérifier si la mission est vraiment terminée
        result = self.mission_completed and not self.is_active
        print(f"Debug - is_mission_finished: {result} (completed: {self.mission_completed}, active: {self.is_active})")
        return result
    
    
    def draw(self):
        if not self.is_active:
            return
        
        self.player_list.draw()
        self.enemy_list.draw()
        self.bullet_list.draw()
        self.enemy_bullet_list.draw()
        self.boss_list.draw()
        self.boss_bullet_list.draw()
        if len(self.explosion_list) > 0:
            print(f"Affichage de {len(self.explosion_list)} explosion(s)")
        self.explosion_list.draw()
        
        # Barre de vie du boss (clamp pour éviter de dépasser l'overlay)
        if self.boss_active and self.boss_sprite is not None:
            bar_width = 140
            bar_height = 10
            ratio = 0 if self.boss_max_health == 0 else max(0, min(1, self.boss_health / self.boss_max_health))
            bar_center_x = self.boss_sprite.center_x
            bar_center_y = self.boss_sprite.center_y + self.boss_sprite.height // 2 + 16
            left = max(self.overlay_x + 8, bar_center_x - bar_width / 2)
            right = min(self.overlay_x + self.overlay_w - 8, bar_center_x + bar_width / 2)
            bottom = bar_center_y - bar_height / 2
            top = bar_center_y + bar_height / 2
            # Fond
            arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, arcade.color.DARK_GRAY)
            # Remplissage
            effective_width = right - left
            fill_right = left + (effective_width * ratio)
            arcade.draw_lrbt_rectangle_filled(left, fill_right, bottom, top, arcade.color.GREEN)
            # Contour
            arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, arcade.color.WHITE)
        
        # Dessiner les explosions du vaisseau (si elles existent)
        if hasattr(self, 'ship_explosion_list') and len(self.ship_explosion_list) > 0:
            self.ship_explosion_list.draw()
        
        # Effets visuels de défaite du héros
        if hasattr(self, 'hero_death_time') and self.hero_death_time is not None:
            elapsed = time.time() - self.hero_death_time
            
            # Écran noir sur la télé (overlay) - reste noir jusqu'à la fin
            if elapsed >= 0.5:  # Après 0.5s, la télé reste noire
                arcade.draw_lrbt_rectangle_filled(
                    self.overlay_x, self.overlay_x + self.overlay_w,
                    self.overlay_y, self.overlay_y + self.overlay_h,
                    arcade.color.BLACK
                )
            
            # Clignotement rouge sur tout l'écran (seulement pendant 1 seconde)
            if self.screen_red_filter:  # 1.0-2.0s : clignotement rouge sur tout l'écran
                blink_cycle = int(elapsed * 3) % 2  # Clignote 1.5 fois par seconde
                if blink_cycle == 0:  # Phase rouge
                    arcade.draw_lrbt_rectangle_filled(
                        0, 3000,  # Largeur complète du vaisseau
                        0, 1000,  # Hauteur complète du vaisseau
                        (255, 0, 0, 150)  # Rouge semi-transparent
                    )

    def spawn_boss(self):
        # Créer le boss avec la texture finale si disponible
        texture = None
        # Chercher l'image dans plusieurs emplacements possibles
        base_candidates = [
            'assets',
            os.path.join(os.path.dirname(__file__), '..', 'assets'),
        ]
        base_candidates = [os.path.normpath(p) for p in base_candidates]
        for base in base_candidates:
            candidate = os.path.join(base, 'final-boss.png')
            if os.path.exists(candidate):
                try:
                    texture = arcade.load_texture(candidate)
                    break
                except Exception:
                    texture = None
        if texture is not None:
            self.boss_sprite = arcade.Sprite()
            self.boss_sprite.texture = texture
            # Adapter la taille du boss à l'overlay (environ 60% de la hauteur)
            desired_h = self.overlay_h * 0.6
            try:
                raw_h = float(texture.height)
                self.boss_sprite.scale = desired_h / raw_h if raw_h > 0 else 1.0
            except Exception:
                self.boss_sprite.scale = 1.0
        else:
            # Fallback: bloc de couleur si texture manquante
            self.boss_sprite = arcade.SpriteSolidColor(100, 240, arcade.color.DARK_RED)
        # Position sur la droite de l'overlay
        self.boss_sprite.center_x = self.overlay_x + self.overlay_w - 60
        self.boss_sprite.center_y = self.overlay_y + self.overlay_h // 2
        self.boss_list.append(self.boss_sprite)
        self.boss_active = True
    
    def get_mission_status(self):
        if not self.is_active:
            return "Inactive"
        elif self.mission_completed:
            return f"Terminée - {self.enemies_destroyed} ennemis détruits"
        else:
            remaining_time = max(0, self.mission_duration - (time.time() - self.start_time))
            return f"En cours - {int(remaining_time)}s restantes"

    def set_screen_bounds(self, x, y, w, h):
        # Update overlay bounds so mission content follows the overlay
        dx = x - getattr(self, 'overlay_x', x)
        dy = y - getattr(self, 'overlay_y', y)
        self.overlay_x = x
        self.overlay_y = y
        self.overlay_w = w
        self.overlay_h = h
        # Translate existing sprites so they stay aligned with the overlay
        def shift_list(sprite_list, dx, dy):
            if sprite_list:
                for s in list(sprite_list):
                    try:
                        s.center_x += dx
                        s.center_y += dy
                    except Exception:
                        pass
        # Shift all mission entities
        if self.player_sprite is not None:
            try:
                self.player_sprite.center_x += dx
                self.player_sprite.center_y += dy
            except Exception:
                pass
        shift_list(self.enemy_list, dx, dy)
        shift_list(self.bullet_list, dx, dy)
        shift_list(self.enemy_bullet_list, dx, dy)
        shift_list(self.boss_bullet_list, dx, dy)
        shift_list(self.explosion_list, dx, dy)
        if self.boss_sprite is not None:
            try:
                self.boss_sprite.center_x += dx
                self.boss_sprite.center_y += dy
            except Exception:
                pass
    
    def _load_enemy_texture(self):
        """Charge la texture d'ennemi flying_enemie.png"""
        # Cherche les assets dans différents emplacements possibles
        base_candidates = [
            'assets',
            os.path.join(os.path.dirname(__file__), '..', 'assets'),
        ]
        base_candidates = [os.path.normpath(p) for p in base_candidates]
        
        for base in base_candidates:
            # Chercher dans le dossier enemies/
            enemy_path = os.path.join(base, 'enemies', 'flying_enemie.png')
            if os.path.exists(enemy_path):
                try:
                    texture = arcade.load_texture(enemy_path)
                    print(f"Texture ennemis volants chargée: {enemy_path}")
                    return texture
                except Exception as e:
                    print(f"Erreur chargement texture ennemis {enemy_path}: {e}")
        
        print("Texture flying_enemie.png non trouvée, utilisation du fallback")
        return None
    
    def _load_hero_ship_texture(self):
        """Charge la texture du vaisseau du héros hero_ship.png"""
        # Cherche les assets dans différents emplacements possibles
        base_candidates = [
            'assets',
            os.path.join(os.path.dirname(__file__), '..', 'assets'),
        ]
        base_candidates = [os.path.normpath(p) for p in base_candidates]
        
        for base in base_candidates:
            hero_path = os.path.join(base, 'hero_ship.png')
            if os.path.exists(hero_path):
                try:
                    texture = arcade.load_texture(hero_path)
                    print(f"Texture vaisseau héros chargée: {hero_path}")
                    return texture
                except Exception as e:
                    print(f"Erreur chargement texture vaisseau héros {hero_path}: {e}")
        
        print("Texture hero_ship.png non trouvée, utilisation du fallback")
        return None
