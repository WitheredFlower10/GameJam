import arcade
from utils.constants import ASSISTANT_COLOR, SPRITE_SCALING


class Assistant(arcade.Sprite):
    
    def __init__(self):
        super().__init__()
        
        self.texture = arcade.make_soft_square_texture(32, ASSISTANT_COLOR, outer_alpha=255)
        self.scale = SPRITE_SCALING
        
        self.change_x = 0
        self.change_y = 0

        self.hero = None
    
    def set_hero(self, hero):
        self.hero = hero
    
    def update(self, delta_time=0):
        super().update()
        if self.hero:
            target_x = self.hero.center_x - 100
            if abs(self.center_y - self.hero.center_y) > 100:
                target_y = self.hero.center_y - 50
                self.center_y = target_y
            self.center_x = target_x
    
    def heal_hero(self):
        if self.hero:
            self.hero.heal(10)
            print("Héros soigné !")
    
    def protect_hero(self):
        if self.hero:
            print("Bouclier activé !")
    
    def attack_enemies(self):
        print("Attaque lancée !")
