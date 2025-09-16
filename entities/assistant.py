import arcade
from utils.constants import ASSISTANT_COLOR, SPRITE_SCALING


class Assistant(arcade.Sprite):
    def move_left(self, speed):
        self.change_x = -speed

    def move_right(self, speed):
        self.change_x = speed

    def stop(self):
        self.change_x = 0

    def jump(self, jump_speed):
        if self.change_y == 0:  # 简单防止二段跳，实际可用物理引擎检测是否在地面
            self.change_y = jump_speed
    
    def __init__(self):
        super().__init__()
        
        self.texture = arcade.make_soft_square_texture(32, ASSISTANT_COLOR, outer_alpha=255)
        self.scale = SPRITE_SCALING
        
        self.change_x = 0
        self.change_y = 0

        self.hero = None
        self.following_hero = False
    
    def set_hero(self, hero):
        self.hero = hero
    
    def update(self, delta_time=0):
        super().update()
        if self.hero and self.following_hero:
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
