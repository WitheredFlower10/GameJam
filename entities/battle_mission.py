import arcade
import random
import time
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


class BattleMission:
    def __init__(self, hero, enemies_to_kill=None):
        # Listes de sprites
        self.player_list = None
        self.enemy_list = None
        self.bullet_list = None
        self.enemy_bullet_list = None
        self.explosion_list = None

        self.hero = hero
        self.player_sprite = None
        self.last_enemy_spawn = 0
        self.last_bullet_shot = 0
        self.start_time = time.time()
        self.mission_duration = GAME_DURATION
        self.is_active = False
        self.mission_completed = False
        self.enemies_destroyed = 0
        # Nombre d'ennemis choisi aléatoirement entre 20 et 30
        self.enemies_to_kill = enemies_to_kill if enemies_to_kill is not None else random.randint(25, 45)
        
        # Boss
        self.boss_active = False
        self.boss_sprite = None
        self.boss_list = None
        self.boss_health = 40
        self.boss_max_health = 40
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

        # Héros de la mission (utilise l'instance Hero passée)
        self.player_sprite = self.hero
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
        self.boss_health = 40
        self.boss_max_health = 40
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
    
    def update(self, delta_time):
        if not self.is_active:
            return
        
        # Déclencher le boss quand le quota est atteint
        if (not self.boss_active) and (self.enemies_destroyed >= self.enemies_to_kill):
            self.spawn_boss()

        # Spawn d'ennemis (désactivé quand le boss est présent)
        if (not self.boss_active) and (time.time() - self.last_enemy_spawn > SPAWN_INTERVAL):
            enemy = arcade.SpriteSolidColor(30, 30, arcade.color.RED)
            # Spawn encore 20px plus à gauche (désormais à l'intérieur de l'overlay)
            enemy.center_x = self.overlay_x + self.overlay_w - 20
            enemy.center_y = random.randint(
                self.overlay_y + 20, 
                self.overlay_y + self.overlay_h - 20
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
                    explosion = Explosion(enemy.center_x, enemy.center_y)
                    self.explosion_list.append(explosion)
                    enemy.remove_from_sprite_lists()
                    self.enemies_destroyed += 1

        # Collision balles/boss
        if self.boss_active and self.boss_sprite is not None:
            for bullet in list(self.bullet_list):
                if arcade.check_for_collision(bullet, self.boss_sprite):
                    bullet.remove_from_sprite_lists()
                    self.boss_health -= 2
                    impact = Explosion(bullet.center_x, bullet.center_y)
                    self.explosion_list.append(impact)
                    if self.boss_health <= 0:
                        boss_explosion = Explosion(self.boss_sprite.center_x, self.boss_sprite.center_y)
                        self.explosion_list.append(boss_explosion)
                        self.boss_sprite.remove_from_sprite_lists()
                        self.boss_active = False
                        self.success = True
                        self.end_mission()

        # Collision ennemis / héros (le héros prend des dégâts)
        for enemy in list(self.enemy_list):
            if arcade.check_for_collision(enemy, self.player_sprite):
                # L'ennemi explose (il est détruit)
                explosion = Explosion(enemy.center_x, enemy.center_y)
                self.explosion_list.append(explosion)
                enemy.remove_from_sprite_lists()
                # Appliquer des dégâts au héros
                damage = 5
                self.hero.health = max(0, self.hero.health - damage)
                # Mettre à jour l'état du héros
                if self.hero.health <= 0:
                    # Le héros explose aussi (il meurt)
                    hero_explosion = Explosion(self.hero.center_x, self.hero.center_y)
                    self.explosion_list.append(hero_explosion)
                    self.success = False
                    self.hero.state = HERO_STATE_FAILED
                    self.end_mission()
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
                    # Le héros explose aussi (il meurt)
                    hero_explosion = Explosion(self.hero.center_x, self.hero.center_y)
                    self.explosion_list.append(hero_explosion)
                    self.success = False
                    self.hero.state = HERO_STATE_FAILED
                    self.end_mission()
                else:
                    # Le héros reste en état de combat (pas d'explosion)
                    self.hero.state = HERO_STATE_FIGHTING

        # Collision balles du boss / héros
        for boss_bullet in list(self.boss_bullet_list):
            if arcade.check_for_collision(boss_bullet, self.player_sprite):
                boss_bullet.remove_from_sprite_lists()
                damage = 8
                self.hero.health = max(0, self.hero.health - damage)
                if self.hero.health <= 0:
                    hero_explosion = Explosion(self.hero.center_x, self.hero.center_y)
                    self.explosion_list.append(hero_explosion)
                    self.hero.state = HERO_STATE_FAILED
                    self.end_mission()
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

    def spawn_boss(self):
        # Créer un grand ennemi fixe sur la droite
        self.boss_sprite = arcade.SpriteSolidColor(100, 240, arcade.color.DARK_RED)
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
