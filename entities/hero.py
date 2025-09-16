import arcade
from utils.constants import HERO_COLOR, SPRITE_SCALING


class Hero(arcade.Sprite):
    
    def __init__(self):
        super().__init__()
        
        self.texture = arcade.make_soft_square_texture(32, HERO_COLOR, outer_alpha=255)
        self.scale = SPRITE_SCALING
        
        self.change_x = 0
        self.change_y = 0
        
        self.assistant = None
        self.health = 100
        self.max_health = 100
    
    def set_assistant(self, assistant):
        self.assistant = assistant
    
    def update(self, delta_time=0):
        super().update()
        self.change_x = 2
        if self.center_x % 200 < 5:
            self.change_y = 12
    
    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0
    
    def heal(self, amount):
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health
