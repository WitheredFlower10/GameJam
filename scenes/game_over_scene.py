import arcade
import time


class GameOverScene(arcade.View):
    """Scène d'écran de défaite - affichée quand le héros meurt"""
    
    def __init__(self):
        super().__init__()
        self.start_time = time.time()
        self.background_color = arcade.color.BLACK
        
    def on_draw(self):
        """Dessine l'écran de défaite"""
        self.clear()
        
        # Écran noir fullscreen
        arcade.draw_lrbt_rectangle_filled(0, self.window.width, 0, self.window.height, arcade.color.BLACK)
        
        center_x = self.window.width // 2
        center_y = self.window.height // 2
        
        arcade.draw_text("LE MONDE EST DETRUIT", center_x, center_y, 
                        arcade.color.RED, 80, bold=True, 
                        anchor_x="center", anchor_y="center")
        
        # Texte explicatif plus petit
        arcade.draw_text("Et vous qu'avez-vous fait ? Simplement regarder et parier, vous êtes bien inutile...", 
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
