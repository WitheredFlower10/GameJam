import arcade
import platform
from scenes.game_end_scene import GameEndScene
from scenes.game_over_scene import GameOverScene
from scenes.menu_scene import MenuScene
from utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE


class MissionAgentGame(arcade.Window):
    
    def __init__(self):
        # Détecter le système d'exploitation
        w,h = arcade.get_display_size()
        self.is_macos = platform.system() == "Darwin"
        self.fullscreen_enabled = False
        self.allow_fullscreen_toggle = True  # Permet le toggle seulement dans le menu
        
        # Initialiser la fenêtre - différent selon l'OS
        try:
            if self.is_macos:
                # Sur macOS, démarrer en fenêtré puis passer en fullscreen
                super().__init__(self.w, self.h, SCREEN_TITLE, resizable=False)
            else:
                # Sur Windows/Linux, fullscreen direct
                super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, fullscreen=True)
                self.fullscreen_enabled = True
                print("Fullscreen activé")
                
        except Exception as e:
            print(f"Erreur fullscreen: {e}")
            # Fallback en mode fenêtré
            super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=True)
            print("Fallback: Mode fenêtré")
            
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)
        
        # Attendre que la fenêtre soit complètement initialisée avant de créer les vues
        
    def setup(self):
        """Initialiser les vues après que la fenêtre soit prête"""
        # Sur macOS, essayer de passer en fullscreen après initialisation
        if self.is_macos and not self.fullscreen_enabled:
            try:
                self.set_fullscreen(True)
                self.fullscreen_enabled = True
                print("Fullscreen activé sur macOS")
            except Exception as e:
                print(f"Impossible d'activer le fullscreen sur macOS: {e}")
        
        self.menu_scene = MenuScene()
        self.show_view(self.menu_scene)

    

def main():
    arcade.load_font("assets/fonts/ByteBounce.ttf")
    game = MissionAgentGame()
    game.setup()  # Initialiser après la création de la fenêtre
    game.run()


if __name__ == "__main__":
    main()