import arcade
import platform
from scenes.game_end_scene import GameEndScene
from scenes.game_over_scene import GameOverScene
from scenes.menu_scene import MenuScene
from utils.constants import SCREEN_WIDTH,SCREEN_HEIGHT,SCREEN_TITLE


class MissionAgentGame(arcade.Window):
    
    def __init__(self):
        self.is_macos = platform.system() == "Darwin"
        if self.is_macos:
            w,h = arcade.get_display_size()
            super().__init__(w, h, SCREEN_TITLE, resizable=False)            
            arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)
        else:
            super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=False)
        
        
    def setup(self):
        """Initialiser les vues après que la fenêtre soit prête"""    
        self.menu_scene = MenuScene()
        self.show_view(self.menu_scene)

    

def main():
    arcade.load_font("assets/fonts/ByteBounce.ttf")
    game = MissionAgentGame()
    game.setup()  # Initialiser après la création de la fenêtre
    game.run()


if __name__ == "__main__":
    main()