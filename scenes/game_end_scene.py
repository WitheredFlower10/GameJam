import arcade
import time


class GameEndScene(arcade.View):
    """Scène d'écran de victoire - affichée quand le boss est vaincu"""
    
    def __init__(self):
        super().__init__()
        self.start_time = time.time()
        self.background_color = arcade.color.BLACK
        
    def on_draw(self):
        """Dessine l'écran de victoire"""
        self.clear()
        
        # Écran noir fullscreen
        arcade.draw_lrbt_rectangle_filled(0, self.window.width, 0, self.window.height, arcade.color.BLACK)
        
        # Texte "WIN" centré
        center_x = self.window.width // 2
        center_y = self.window.height // 2
        
        arcade.draw_text("LE MONDE EST SAUVE", center_x, center_y, 
                        arcade.color.GOLD, 80, bold=True, 
                        anchor_x="center", anchor_y="center")
        
        # Texte explicatif plus petit
        arcade.draw_text("Mais vous, à quoi avez-vous servi ?...", 
                        center_x, center_y - 100, 
                        arcade.color.WHITE, 24, 
                        anchor_x="center", anchor_y="center")

        
        # Instructions pour quitter
        arcade.draw_text("Appuyez sur ÉCHAP pour quitter", 
                        center_x, center_y - 200, 
                        arcade.color.GRAY, 18, 
                        anchor_x="center", anchor_y="center")
    
    def on_key_press(self, key, modifiers):
        """Gère les touches pressées"""
        if key == arcade.key.ESCAPE:
            # Quitter le jeu
            arcade.exit()
    
    def on_update(self, delta_time):
        """Mise à jour de la scène"""
        # La scène reste statique
        pass
