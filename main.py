import arcade
from scenes.main_scene import MainScene
from utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE


class MissionAgentGame(arcade.Window):
    
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)
        
        self.main_scene = MainScene()
        self.show_view(self.main_scene)


def main():
    game = MissionAgentGame()
    game.run()


if __name__ == "__main__":
    main()