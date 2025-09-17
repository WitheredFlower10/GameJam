import arcade
import platform
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
                print("Utilisez F11 ou Cmd+F pour basculer en fullscreen")
        
        self.menu_scene = MenuScene()
        self.show_view(self.menu_scene)
    
    def disable_fullscreen_toggle(self):
        """Désactive le toggle fullscreen (appelé quand on quitte le menu)"""
        self.allow_fullscreen_toggle = False
        print("Toggle fullscreen désactivé")
    
    def enable_fullscreen_toggle(self):
        """Active le toggle fullscreen (appelé quand on revient au menu)"""
        self.allow_fullscreen_toggle = True
        print("Toggle fullscreen activé")
    
    def on_resize(self, width, height):
        """Appelé automatiquement par Arcade lors du redimensionnement"""
        super().on_resize(width, height)
        
        # Notifier la vue actuelle
        current_view = getattr(self, 'current_view', None)
        if current_view and hasattr(current_view, 'on_resize_event'):
            current_view.on_resize_event(width, height)
        elif hasattr(self, 'menu_scene') and hasattr(self.menu_scene, 'on_resize_event'):
            self.menu_scene.on_resize_event(width, height)
    
    def on_key_press(self, key, modifiers):
        """Gestion des touches globales"""
        # F11 ou Cmd+F pour basculer fullscreen (seulement si autorisé)
        if (key == arcade.key.F11 or (key == arcade.key.F and modifiers & arcade.key.MOD_ACCEL)) and self.allow_fullscreen_toggle:
            try:
                self.fullscreen_enabled = not self.fullscreen_enabled
                self.set_fullscreen(self.fullscreen_enabled)
                status = "activé" if self.fullscreen_enabled else "désactivé"
                print(f"Fullscreen {status}")
                
                # Notifier la vue actuelle du changement de résolution
                current_view = getattr(self, 'current_view', None)
                if current_view and hasattr(current_view, 'on_resize_event'):
                    current_view.on_resize_event(self.width, self.height)
                # Aussi essayer avec menu_scene si c'est la vue active
                elif hasattr(self, 'menu_scene') and hasattr(self.menu_scene, 'on_resize_event'):
                    self.menu_scene.on_resize_event(self.width, self.height)
                        
            except Exception as e:
                print(f"Erreur changement fullscreen: {e}")
        elif (key == arcade.key.F11 or (key == arcade.key.F and modifiers & arcade.key.MOD_ACCEL)) and not self.allow_fullscreen_toggle:
            print("Changement de fullscreen désactivé - Retournez au menu pour changer")
        
        # Transmettre l'événement à la vue actuelle
        current_view = getattr(self, 'current_view', None)
        if current_view and hasattr(current_view, 'on_key_press'):
            current_view.on_key_press(key, modifiers)
        # Aussi essayer avec menu_scene si c'est la vue active
        elif hasattr(self, 'menu_scene') and hasattr(self.menu_scene, 'on_key_press'):
            self.menu_scene.on_key_press(key, modifiers)


def main():
    arcade.load_font("assets/fonts/ByteBounce.ttf")
    game = MissionAgentGame()
    game.setup()  # Initialiser après la création de la fenêtre
    game.run()


if __name__ == "__main__":
    main()