import arcade
from utils.constants import SURVEILLANCE_SCREEN_WIDTH, SURVEILLANCE_SCREEN_HEIGHT
from utils.constants import SURVEILLANCE_SCREEN_X, SURVEILLANCE_SCREEN_Y, SCREEN_COLOR


class SurveillanceScreen:
    
    def __init__(self):
        self.hero = None
        self.background_sprites = []
        self.enemy_sprites = []
        
        self.screen_x = SURVEILLANCE_SCREEN_X
        self.screen_y = SURVEILLANCE_SCREEN_Y
        # +20 px (10 à gauche, 10 à droite) par défaut
        self.screen_width = SURVEILLANCE_SCREEN_WIDTH + 20
        self.screen_height = SURVEILLANCE_SCREEN_HEIGHT
        
        self.scroll_speed = 20
        self.background_offset = 0
        
        self.create_background()
    
    def set_hero(self, hero):
        self.hero = hero
    
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
    
    def draw(self):
        # Dessiner l'arrière-plan de l'écran (fond)
        left = self.screen_x
        right = self.screen_x + self.screen_width
        bottom = self.screen_y
        top = self.screen_y + self.screen_height
        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, SCREEN_COLOR)
        
        # Cadre/bords plus épais et plus esthétiques (double contour)
        # Contour extérieur légèrement gris, épaisseur 5 px
        arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, arcade.color.LIGHT_GRAY, 5)
        # Contour intérieur blanc, légèrement en retrait, épaisseur 2 px
        inset = 4
        arcade.draw_lrbt_rectangle_outline(left + inset, right - inset, bottom + inset, top - inset, arcade.color.WHITE, 2)
        
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
                    sprite.draw()
            
            # Dessiner le héros s'il est visible
            if self.hero and self.hero.screen_x < self.screen_width:
                hero_screen_x = self.screen_x + self.hero.screen_x
                hero_screen_y = self.screen_y + self.screen_height // 2
                
                # Dessiner le héros
                arcade.draw_circle_filled(
                    hero_screen_x, hero_screen_y, 8, arcade.color.GOLD
                )
                
                # Dessiner des ennemis occasionnels
                if self.hero.state == "fighting":
                    for i in range(2):
                        enemy_x = hero_screen_x + 30 + i * 20
                        enemy_y = hero_screen_y + (i - 1) * 15
                        arcade.draw_circle_filled(
                            enemy_x, enemy_y, 6, arcade.color.RED
                        )
        
        # Dessiner les informations du héros
        self.draw_hero_info()
    
    def draw_hero_info(self):
        if not self.hero:
            return
        
        info_x = self.screen_x + 10
        info_y = self.screen_y + self.screen_height - 20
        
        # Barre de vie
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
        
        # État du héros
        state_text = f"État: {self.hero.state}"
        arcade.draw_text(state_text, info_x, info_y - 25, arcade.color.WHITE, 12)
        
        # Compteur d'ennemis tués (si mission de bataille active)
        if self.hero.battle_mission and self.hero.battle_mission.is_active:
            kill_text = f"Ennemis: {self.hero.battle_mission.enemies_destroyed}/{self.hero.battle_mission.enemies_to_kill}"
            arcade.draw_text(kill_text, info_x, info_y - 45, arcade.color.YELLOW, 12)
