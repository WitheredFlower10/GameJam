import arcade
import random
import time
from utils.constants import SURVEILLANCE_SCREEN_WIDTH, SURVEILLANCE_SCREEN_HEIGHT, SURVEILLANCE_SCREEN_X, SURVEILLANCE_SCREEN_Y


class Explosion(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__(arcade.make_circle_texture(15, arcade.color.ORANGE), 0.6)
        self.center_x = x
        self.center_y = y
        self.start_time = time.time()

    def update(self, delta_time=0):
        if time.time() - self.start_time > 0.3:
            self.remove_from_sprite_lists()


class BattleMission:
    def __init__(self):
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.explosion_list = arcade.SpriteList()
        
        self.player_sprite = None
        self.last_enemy_spawn = 0
        self.last_bullet_shot = 0
        self.start_time = time.time()
        self.mission_duration = 20
        self.is_active = False
        self.mission_completed = False
        self.enemies_destroyed = 0
        
        # Contrôles du héros
        self.player_speed = 3
        self.bullet_speed = 5
        self.enemy_speed = 2
        self.spawn_interval = 0.8
        
        
        self.setup_battle()
    
    def setup_battle(self):
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.explosion_list = arcade.SpriteList()
        
        # Créer le vaisseau du héros (plus grand comme dans l'exemple)
        self.player_sprite = arcade.SpriteSolidColor(40, 40, arcade.color.BLUE)
        self.player_sprite.center_x = SURVEILLANCE_SCREEN_X + 60
        self.player_sprite.center_y = SURVEILLANCE_SCREEN_Y + SURVEILLANCE_SCREEN_HEIGHT // 2
        self.player_list.append(self.player_sprite)
        
        self.last_enemy_spawn = 0
        self.last_bullet_shot = 0
        self.start_time = time.time()
        self.enemies_destroyed = 0
        self.mission_completed = False
    
    def start_mission(self):
        self.is_active = True
        self.setup_battle()
        print("Mission de bataille galactique commencée !")
    
    def end_mission(self):
        self.is_active = False
        self.mission_completed = True
        print(f"Mission terminée ! Ennemis détruits : {self.enemies_destroyed}")
    
    def update(self, delta_time):
        if not self.is_active:
            return
        
        current_time = time.time()
        
        if current_time - self.start_time > self.mission_duration:
            self.end_mission()
            return
        
        # Spawn d'ennemis
        if current_time - self.last_enemy_spawn > self.spawn_interval:
            enemy = arcade.SpriteSolidColor(30, 30, arcade.color.RED)
            enemy.center_x = SURVEILLANCE_SCREEN_X + SURVEILLANCE_SCREEN_WIDTH + 20
            enemy.center_y = random.randint(
                SURVEILLANCE_SCREEN_Y + 20, 
                SURVEILLANCE_SCREEN_Y + SURVEILLANCE_SCREEN_HEIGHT - 20
            )
            enemy.change_x = -self.enemy_speed
            self.enemy_list.append(enemy)
            self.last_enemy_spawn = current_time
        
        # Mouvement automatique du héros (histoire principale)
        self.update_hero_ai_movement()
        
        # Tir automatique
        if current_time - self.last_bullet_shot > 0.3:
            bullet = arcade.SpriteSolidColor(10, 4, arcade.color.YELLOW)
            bullet.center_x = self.player_sprite.center_x + 20
            bullet.center_y = self.player_sprite.center_y
            bullet.change_x = self.bullet_speed
            self.bullet_list.append(bullet)
            self.last_bullet_shot = current_time
        
        # Mettre à jour les positions
        self.enemy_list.update()
        self.bullet_list.update()
        self.explosion_list.update()
        
        # Supprimer ennemis/bullets hors écran
        for enemy in self.enemy_list:
            if enemy.center_x < SURVEILLANCE_SCREEN_X - 20:
                enemy.remove_from_sprite_lists()
        
        for bullet in self.bullet_list:
            if bullet.center_x > SURVEILLANCE_SCREEN_X + SURVEILLANCE_SCREEN_WIDTH + 20:
                bullet.remove_from_sprite_lists()
        
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
    
    def update_hero_ai_movement(self):
        # Mouvement automatique du héros (IA de navigation)
        # Le héros navigue librement sur l'écran avec une IA comportementale
        
        # Détecter les ennemis proches
        nearby_enemies = []
        for enemy in self.enemy_list:
            distance = ((enemy.center_x - self.player_sprite.center_x) ** 2 + 
                       (enemy.center_y - self.player_sprite.center_y) ** 2) ** 0.5
            if distance < 80:  # Ennemis à moins de 80 pixels
                nearby_enemies.append(enemy)
        
        # Comportement d'évitement des ennemis
        if nearby_enemies:
            # Calculer la direction d'évitement
            avoid_x = 0
            avoid_y = 0
            
            for enemy in nearby_enemies:
                # Vecteur d'évitement (s'éloigner de l'ennemi)
                dx = self.player_sprite.center_x - enemy.center_x
                dy = self.player_sprite.center_y - enemy.center_y
                distance = (dx**2 + dy**2)**0.5
                
                if distance > 0:
                    # Normaliser et pondérer par la distance
                    weight = 1.0 / (distance + 1)
                    avoid_x += (dx / distance) * weight
                    avoid_y += (dy / distance) * weight
            
            # Appliquer le mouvement d'évitement
            if len(nearby_enemies) > 0:
                avoid_x /= len(nearby_enemies)
                avoid_y /= len(nearby_enemies)
                
                self.player_sprite.center_x += avoid_x * self.player_speed * 0.8
                self.player_sprite.center_y += avoid_y * self.player_speed * 0.8
        else:
            # Comportement de patrouille quand pas d'ennemis proches
            # Mouvement aléatoire mais contrôlé
            import random
            
            # Changer de direction de temps en temps
            if not hasattr(self, 'patrol_timer'):
                self.patrol_timer = 0
                self.patrol_direction = [random.choice([-1, 1]), random.choice([-1, 1])]
            
            self.patrol_timer += 1
            
            # Changer de direction toutes les 60 frames (environ 1 seconde)
            if self.patrol_timer > 60:
                self.patrol_timer = 0
                self.patrol_direction = [random.choice([-1, 1]), random.choice([-1, 1])]
            
            # Mouvement de patrouille
            self.player_sprite.center_x += self.patrol_direction[0] * self.player_speed * 0.4
            self.player_sprite.center_y += self.patrol_direction[1] * self.player_speed * 0.4
        
        # Limiter le mouvement dans l'écran de surveillance
        screen_left = SURVEILLANCE_SCREEN_X + 20
        screen_right = SURVEILLANCE_SCREEN_X + SURVEILLANCE_SCREEN_WIDTH - 20
        screen_bottom = SURVEILLANCE_SCREEN_Y + 20
        screen_top = SURVEILLANCE_SCREEN_Y + SURVEILLANCE_SCREEN_HEIGHT - 20
        
        # Rebondir sur les bords
        if self.player_sprite.center_x <= screen_left or self.player_sprite.center_x >= screen_right:
            if hasattr(self, 'patrol_direction'):
                self.patrol_direction[0] *= -1
        if self.player_sprite.center_y <= screen_bottom or self.player_sprite.center_y >= screen_top:
            if hasattr(self, 'patrol_direction'):
                self.patrol_direction[1] *= -1
        
        self.player_sprite.center_x = max(screen_left, min(screen_right, self.player_sprite.center_x))
        self.player_sprite.center_y = max(screen_bottom, min(screen_top, self.player_sprite.center_y))
    
    
    def draw(self):
        if not self.is_active:
            return
        
        self.player_list.draw()
        self.enemy_list.draw()
        self.bullet_list.draw()
        self.explosion_list.draw()
        
        if self.mission_completed:
            arcade.draw_text(
                f"Mission Terminée! Ennemis: {self.enemies_destroyed}",
                SURVEILLANCE_SCREEN_X + 10,
                SURVEILLANCE_SCREEN_Y + SURVEILLANCE_SCREEN_HEIGHT - 30,
                arcade.color.WHITE,
                12
            )
    
    def get_mission_status(self):
        if not self.is_active:
            return "Inactive"
        elif self.mission_completed:
            return f"Terminée - {self.enemies_destroyed} ennemis détruits"
        else:
            remaining_time = max(0, self.mission_duration - (time.time() - self.start_time))
            return f"En cours - {int(remaining_time)}s restantes"
