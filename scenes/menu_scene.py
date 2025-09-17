import arcade
import math
from utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE


class MenuScene(arcade.View):
    
    def __init__(self):
        super().__init__()
        
        # Couleurs et styles
        self.title_color = arcade.color.GOLD
        self.subtitle_color = arcade.color.WHITE
        self.button_color = arcade.color.BLUE
        self.button_hover_color = arcade.color.LIGHT_BLUE
        self.background_color = arcade.color.BLACK
        
        # État du menu
        self.selected_option = 0
        self.menu_options = [
            "Commencer la Mission",
            "Instructions",
            "Quitter"
        ]
        
        # Animation
        self.animation_timer = 0
        self.title_scale = 1.0
        self.title_scale_direction = 1
        
        # Sons (optionnel)
        self.sound_enabled = True
    
    def on_draw(self):
        self.clear()
        
        # Fond étoilé
        self.draw_starfield()
        
        # Titre du jeu
        self.draw_title()
        
        # Options du menu
        self.draw_menu_options()
        
        # Instructions de contrôle
        self.draw_controls()
        
        # Version
        arcade.draw_text("Version 1.0 - Game Jam 2025", 
                        10, 10, arcade.color.GRAY, 12)
    
    def draw_starfield(self):
        # Dessiner un champ d'étoiles animé
        import random
        random.seed(42)  # Pour des étoiles fixes
        
        for i in range(100):
            x = (i * 37) % SCREEN_WIDTH
            y = (i * 73) % SCREEN_HEIGHT
            brightness = (i * 17) % 255
            
            # Animation des étoiles
            twinkle = int(128 + 127 * math.sin(self.animation_timer * 0.01 + i * 0.1))
            color = (twinkle, twinkle, twinkle)
            
            arcade.draw_circle_filled(x, y, 1, color)
    
    def draw_title(self):
        # Titre principal avec animation
        title_x = SCREEN_WIDTH // 2
        title_y = SCREEN_HEIGHT - 150
        
        # Animation de pulsation
        self.animation_timer += 1
        if self.animation_timer % 60 == 0:
            self.title_scale_direction *= -1
        
        self.title_scale += self.title_scale_direction * 0.01
        self.title_scale = max(0.9, min(1.1, self.title_scale))
        
        # Titre principal
        arcade.draw_text(
            "THE OBSERVER PROTOCOL",
            title_x, title_y,
            self.title_color, 48,
            anchor_x="center",
            bold=True
        )
    
    def draw_menu_options(self):
        start_y = SCREEN_HEIGHT // 2 + 50
        option_height = 60
        
        for i, option in enumerate(self.menu_options):
            y_pos = start_y - (i * option_height)
            
            # Couleur de l'option sélectionnée
            if i == self.selected_option:
                color = self.button_hover_color
                # Effet de surbrillance
                arcade.draw_lrbt_rectangle_filled(
                    SCREEN_WIDTH // 2 - 150, SCREEN_WIDTH // 2 + 150,
                    y_pos - 20, y_pos + 20,
                    (color[0], color[1], color[2], 50)
                )
            else:
                color = self.subtitle_color
            
            # Texte de l'option
            arcade.draw_text(
                option,
                SCREEN_WIDTH // 2, y_pos,
                color, 24,
                anchor_x="center",
                bold=(i == self.selected_option)
            )
            
            # Indicateur de sélection
            if i == self.selected_option:
                arcade.draw_text(
                    ">",
                    SCREEN_WIDTH // 2 - 150, y_pos,
                    self.button_color, 24,
                    anchor_x="center"
                )
                arcade.draw_text(
                    "<",
                    SCREEN_WIDTH // 2 + 150, y_pos,
                    self.button_color, 24,
                    anchor_x="center"
                )
    
    def draw_controls(self):
        # Instructions de contrôle
        controls_y = 120
        
        arcade.draw_text(
            "Contrôles:",
            SCREEN_WIDTH // 2, controls_y,
            arcade.color.WHITE, 18,
            anchor_x="center",
            bold=True
        )
        
        arcade.draw_text(
            "↑↓ - Naviguer dans le menu",
            SCREEN_WIDTH // 2, controls_y - 25,
            arcade.color.LIGHT_GRAY, 14,
            anchor_x="center"
        )
        
        arcade.draw_text(
            "ENTRÉE - Sélectionner",
            SCREEN_WIDTH // 2, controls_y - 45,
            arcade.color.LIGHT_GRAY, 14,
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
        if self.selected_option == 0:  # Commencer la Mission
            from scenes.main_scene import MainScene
            game_scene = MainScene()
            self.window.show_view(game_scene)
        elif self.selected_option == 1:  # Instructions
            self.show_instructions()
        elif self.selected_option == 2:  # Quitter
            arcade.exit()
    
    def show_instructions(self):
        # Créer une vue d'instructions
        instructions_view = InstructionsView()
        self.window.show_view(instructions_view)
    
    def on_update(self, delta_time):
        # Mettre à jour l'animation
        self.animation_timer += delta_time * 60


class InstructionsView(arcade.View):
    
    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.BLACK
    
    def on_draw(self):
        self.clear()
        
        # Titre
        arcade.draw_text(
            "INSTRUCTIONS",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100,
            arcade.color.GOLD, 36,
            anchor_x="center",
            bold=True
        )
        
        # Instructions
        instructions = [
            "Vous êtes un Agent de Missions galactique.",
            "",
            "Votre rôle:",
            "• Distribuer des missions aux héros",
            "• Surveiller leur progression",
            "• Gérer les interactions dans le vaisseau",
            "",
            "Contrôles:",
            "• FLÈCHES: Se déplacer dans le vaisseau",
            "• ESPACE: Interagir avec les points d'intérêt",
            "",
            "Surveillance:",
            "• L'écran central montre la mission du héros",
            "• Les héros agissent automatiquement",
            "• Vous pouvez améliorer la surveillance",
            "",
            "Objectif:",
            "• Remplir vos tâches administratives",
            "• Surveiller les héros en mission",
            "• Parier sur leur réussite"
        ]
        
        y_pos = SCREEN_HEIGHT - 150
        for instruction in instructions:
            if instruction == "":
                y_pos -= 20
                continue
            
            color = arcade.color.WHITE
            size = 16
            
            if instruction.startswith("•"):
                color = arcade.color.LIGHT_BLUE
                size = 14
            elif instruction.endswith(":"):
                color = arcade.color.YELLOW
                size = 18
                instruction = instruction.upper()
            
            arcade.draw_text(
                instruction,
                50, y_pos,
                color, size
            )
            y_pos -= 25
        
        # Retour au menu
        arcade.draw_text(
            "Appuyez sur ÉCHAP pour retourner au menu",
            SCREEN_WIDTH // 2, 50,
            arcade.color.LIGHT_GRAY, 16,
            anchor_x="center"
        )
    
    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            menu_scene = MenuScene()
            self.window.show_view(menu_scene)
