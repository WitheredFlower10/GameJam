import arcade
from utils.constants import *
from entities.assistant import Assistant
from entities.hero import Hero


class GameScene(arcade.View):
    
    def __init__(self):
        super().__init__()
        
        self.player_list = None
        self.platform_list = None
        self.hero = None
        self.assistant = None
        
        self.physics_engine = None
        
        self.camera = None
        self.gui_camera = None
        
        self.setup()
    
    def setup(self):
        self.player_list = arcade.SpriteList()
        self.platform_list = arcade.SpriteList()
        
        self.assistant = Assistant()
        self.assistant.center_x = 100
        self.assistant.center_y = 200
        self.player_list.append(self.assistant)
        
        self.hero = Hero()
        self.hero.center_x = 150
        self.hero.center_y = 200
        self.player_list.append(self.hero)
        
        self.assistant.set_hero(self.hero)
        self.hero.set_assistant(self.assistant)
        
        self.create_platforms()
        
        self.assistant_physics = arcade.PhysicsEnginePlatformer(
            self.assistant, self.platform_list, gravity_constant=GRAVITY
        )
        
        self.hero_physics = arcade.PhysicsEnginePlatformer(
            self.hero, self.platform_list, gravity_constant=GRAVITY
        )
        
        self.camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()
    
    def create_platforms(self):
        for x in range(0, SCREEN_WIDTH, 64):
            platform = arcade.SpriteSolidColor(64, 64, PLATFORM_COLOR)
            platform.center_x = x
            platform.center_y = 32
            self.platform_list.append(platform)
        
        platforms_data = [
            (200, 200), (400, 300), (600, 250), (800, 350)
        ]
        
        for x, y in platforms_data:
            platform = arcade.SpriteSolidColor(128, 32, PLATFORM_COLOR)
            platform.center_x = x
            platform.center_y = y
            self.platform_list.append(platform)
    
    def on_draw(self):
        self.clear()
        
        self.camera.use()
        self.platform_list.draw()
        self.player_list.draw()
        
        self.gui_camera.use()
        arcade.draw_text("Assistant du Héros", 10, SCREEN_HEIGHT - 30, 
                        arcade.color.WHITE, 20)
        arcade.draw_text("ESPACE: Soigner | A: Protéger | S: Attaquer", 
                        10, SCREEN_HEIGHT - 60, arcade.color.WHITE, 16)
        arcade.draw_text(f"Vie du héros: {self.hero.health}/{self.hero.max_health}", 
                        10, SCREEN_HEIGHT - 90, arcade.color.WHITE, 16)
    
    def on_update(self, delta_time):
        self.hero_physics.update()
        self.assistant_physics.update()
        self.player_list.update()
        self.center_camera_to_player()
    
    def center_camera_to_player(self):
        self.camera.position = (self.hero.center_x, self.hero.center_y)
    
    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.assistant.heal_hero()
        elif key == arcade.key.A:
            self.assistant.protect_hero()
        elif key == arcade.key.S:
            self.assistant.attack_enemies()
        elif key == arcade.key.LEFT:
            self.assistant.move_left(PLAYER_MOVEMENT_SPEED)
        elif key == arcade.key.RIGHT:
            self.assistant.move_right(PLAYER_MOVEMENT_SPEED)
        elif key == arcade.key.UP:
            self.assistant.jump(PLAYER_JUMP_SPEED)
    
    def on_key_release(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.RIGHT):
            self.assistant.stop()