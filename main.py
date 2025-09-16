import arcade
from scenes.game_scene import GameScene
from utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE


class GameJamGame(arcade.Window):
    
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.SKY_BLUE)
        
        self.game_scene = GameScene()
        self.show_view(self.game_scene)


def main():
    game = GameJamGame()
    game.run()


if __name__ == "__main__":
    main()
