import arcade
import math
from utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE


class MenuScene(arcade.View):
    
    def __init__(self):
        super().__init__()
        
        # Couleurs futuristes
        self.title_color = (44,86,110)       
        self.subtitle_color = (180, 180, 255)  
        self.option_color = (147,150,185)  
        self.option_hover_color = (85,106,161) 
        self.background_color = arcade.color.BLACK
        
        #Son
        self.sound_back = arcade.load_sound("assets/sounds/menu_back.wav")
        self.sound_enabled = True

        
        # État du menu
        self.selected_option = 0
        self.menu_options = [
            "▶ Démarrer l’Opération",
            "📜 Manuel Galactique",
            "✖ Éjecter du Système"
        ]
        
        # Animation
        self.animation_timer = 0
        self.fade_alpha = 255  # Fondu au démarrage
    
    def on_draw(self):
        self.clear()
        
        # Fond spatial
        self.draw_space_background()
        
        # Titre du jeu
        self.draw_title()
        
        # Options du menu
        self.draw_menu_options()
        
        # Instructions
        self.draw_controls()
        
        # Version
        arcade.draw_text("Version 1.0 - Game Jam 2025", 
                        10, 10, (150, 150, 150), 12)
        
        # Effet fondu
        if self.fade_alpha > 0:
            arcade.draw_lrbt_rectangle_filled(
                0, SCREEN_WIDTH, 0, SCREEN_HEIGHT,
                (0, 0, 0, int(self.fade_alpha))
            )
    
    def draw_space_background(self):
        """ Fond étoilé coloré avec effet galaxie """
        for i in range(200):
            x = (i * 37 + int(self.animation_timer * 1.5)) % SCREEN_WIDTH
            y = (i * 73) % SCREEN_HEIGHT
            size = 1 + (i % 3)
            # Couleurs variées pour un effet cosmique
            if i % 5 == 0:
                color = (200, 200, 255)  # bleu clair
            elif i % 3 == 0:
                color = (255, 150, 255)  # violet
            else:
                twinkle = int(128 + 127 * math.sin(self.animation_timer * 0.05 + i))
                color = (twinkle, twinkle, twinkle)
            arcade.draw_circle_filled(x, y, size, color)
        
        # Effet "scanlines" rétro
        for y in range(0, SCREEN_HEIGHT, 4):
            arcade.draw_line(0, y, SCREEN_WIDTH, y, (0, 0, 0, 40), 1)
    
    def draw_title(self):
        title_x = SCREEN_WIDTH // 2
        title_y = SCREEN_HEIGHT - 120
        
        # Zoom + oscillation
        scale = 1.0 + 0.08 * math.sin(self.animation_timer * 0.05)
        glow = 0
        
        # Titre principal avec halo
        arcade.draw_text(
            "The Observer Protocol",
            title_x, title_y,
            (0, glow, 255), int(54 * scale),
            anchor_x="center",
            bold=True
        )
        
        # Sous-titre
        arcade.draw_text(
            "Centre de Commande Intergalactique",
            title_x, title_y - 60,
            self.subtitle_color, 20,
            anchor_x="center"
        )
    
    def draw_menu_options(self):
        start_y = SCREEN_HEIGHT // 2 + 50
        option_height = 70
        
        for i, option in enumerate(self.menu_options):
            y_pos = start_y - (i * option_height)
            
            if i == self.selected_option:
                # Pulsation néon
                pulse = 150 + 100 * math.sin(self.animation_timer * 0.1)
                color = self.option_hover_color
                glow_color = (color[0], color[1], color[2], int(pulse))
                arcade.draw_lrbt_rectangle_filled(
                    SCREEN_WIDTH // 2 - 220, SCREEN_WIDTH // 2 + 220,
                    y_pos - 30, y_pos + 30,
                    glow_color
                )
            else:
                color = self.option_color
            
            arcade.draw_text(
                option,
                SCREEN_WIDTH // 2, y_pos,
                color, 26,
                anchor_x="center",
                bold=(i == self.selected_option)
            )
    
    def draw_controls(self):
        controls_y = 120
        arcade.draw_text(
            "Naviguez avec ↑↓  |  Validez avec ENTRÉE",
            SCREEN_WIDTH // 2, controls_y,
            (180, 180, 180), 16,
            anchor_x="center"
        )
    
    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP:
            self.selected_option = (self.selected_option - 1) % len(self.menu_options)
        elif key == arcade.key.DOWN:
            self.selected_option = (self.selected_option + 1) % len(self.menu_options)
        elif key == arcade.key.ENTER or key == arcade.key.SPACE:
            self.select_option()
        elif key == arcade.key.ESCAPE:
            arcade.exit()
    
    def select_option(self):
        if self.selected_option == 0:  # Démarrer
            from scenes.main_scene import MainScene
            game_scene = MainScene()
            self.window.show_view(game_scene)
        elif self.selected_option == 1:  # Manuel
            self.show_instructions()
        elif self.selected_option == 2:  # Quitter
            arcade.exit()
    
    def show_instructions(self):
        instructions_view = InstructionsView()
        self.window.show_view(instructions_view)
    
    def on_update(self, delta_time):
        self.animation_timer += delta_time * 60
        if self.fade_alpha > 0:
            self.fade_alpha -= delta_time * 200


class InstructionsView(arcade.View):
    
    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.BLACK
    
    def on_draw(self):
        self.clear()
        
        arcade.draw_text(
            "📜 MANUEL GALACTIQUE",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100,
            (0, 255, 220), 32,
            anchor_x="center",
            bold=True
        )
        
        instructions = [
            "Bienvenue Agent ! Voici vos directives :",
            "",
            "🎯 Votre mission :",
            "• Assigner des quêtes aux héros interstellaires",
            "• Superviser leur progression depuis la base",
            "• Maintenir l’ordre dans le vaisseau",
            "",
            "🎮 Contrôles :",
            "• FLÈCHES : Déplacer votre avatar",
            "• ESPACE : Interagir avec un terminal",
            "",
            "🛰️ Surveillance :",
            "• L’écran central affiche la mission en cours",
            "• Les héros agissent seuls, mais vous pouvez",
            "  influencer leur réussite par vos choix",
            "",
            "🏆 Objectif final :",
            "• Accomplir vos tâches administratives",
            "• Maximiser la réussite des missions",
            "• Devenir l’agent de l’année galactique"
        ]
        
        y_pos = SCREEN_HEIGHT - 160
        for line in instructions:
            if line == "":
                y_pos -= 15
                continue
            
            color = arcade.color.WHITE
            size = 16
            if line.startswith("•"):
                color = (200, 200, 255)
                size = 14
            elif line.startswith("🎯") or line.startswith("🎮") or line.startswith("🛰️") or line.startswith("🏆"):
                color = (255, 200, 0)
                size = 18
            
            arcade.draw_text(line, 60, y_pos, color, size)
            y_pos -= 25
        
        arcade.draw_text(
            "⟵ ÉCHAP pour retourner au menu",
            SCREEN_WIDTH // 2, 50,
            (180, 180, 180), 16,
            anchor_x="center"
        )
    
    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            menu_scene = MenuScene()
            arcade.play_sound(menu_scene.sound_back)
            self.window.show_view(menu_scene)
