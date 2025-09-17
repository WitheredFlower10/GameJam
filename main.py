import arcade
from scenes.menu_scene import MenuScene
from utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE


class MissionAgentGame(arcade.Window):
    
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, fullscreen=False)
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)
        
        self.menu_scene = MenuScene()
        self.show_view(self.menu_scene)


def main():
    arcade.load_font("assets/fonts/ByteBounce.ttf")
    game = MissionAgentGame()
    game.run()


if __name__ == "__main__":
    main()