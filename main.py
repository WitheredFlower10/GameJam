import arcade
import platform
import random
from scenes.game_end_scene import GameEndScene
from scenes.game_over_scene import GameOverScene
from scenes.menu_scene import MenuScene
from utils.constants import SCREEN_WIDTH,SCREEN_HEIGHT,SCREEN_TITLE,STAR_COUNT,STAR_MIN_SIZE,STAR_MAX_SIZE,STAR_COLORS,BACKGROUND_COLOR


class MissionAgentGame(arcade.Window):
    
    def __init__(self):
        self.is_macos = platform.system() == "Darwin"
        if self.is_macos:
            w,h = arcade.get_display_size()
            super().__init__(w, h, SCREEN_TITLE, resizable=False)            
            # arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)
        else:
            super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, fullscreen=True)
            # arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)
        
        # Initialiser les étoiles pour le fond spatial
        self.stars = []
        self.generate_stars()
        
        
    def generate_stars(self):
        """Génère les étoiles pour le fond spatial"""
        self.stars = []
        # Utiliser les dimensions du monde au lieu de la taille de la fenêtre
        # pour couvrir toute la surface de la grande scène
        world_width = 4000  # Largeur du monde définie dans MainScene
        world_height = 1024  # Hauteur du monde définie dans MainScene
        
        for _ in range(STAR_COUNT):
            x = random.randint(0, world_width)
            y = random.randint(0, world_height)
            size = random.randint(STAR_MIN_SIZE, STAR_MAX_SIZE)
            color = random.choice(STAR_COLORS)
            # Ajouter un léger scintillement (alpha variable)
            alpha = random.randint(150, 255)
            self.stars.append({
                'x': x,
                'y': y,
                'size': size,
                'color': color,
                'alpha': alpha,
                'twinkle_speed': random.uniform(0.01, 0.05),
                'twinkle_phase': random.uniform(0, 2 * 3.14159)
            })
    
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