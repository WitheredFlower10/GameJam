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
        self.background_music_player = None

        
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
        
        # Créer les objets Text pour de meilleures performances
        self.create_text_objects()
        
        # Démarrer la musique de fond
        self.start_background_music()
    
    def create_text_objects(self):
        """Crée les objets Text pour de meilleures performances"""
        # Titre principal (valeurs initiales, seront mises à jour dans draw_title)
        self.title_text = arcade.Text(
            "The Observer Protocol",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 120,
            (0, 0, 255), 54,
            anchor_x="center", bold=True
        )
        
        # Sous-titre
        self.subtitle_text = arcade.Text(
            "Centre de Commande Intergalactique",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 180,
            self.subtitle_color, 20,
            anchor_x="center"
        )
        
        # Contrôles
        self.controls_text = arcade.Text(
            "Naviguez avec ↑↓  |  Validez avec ENTRÉE",
            SCREEN_WIDTH // 2, 120,
            (180, 180, 180), 16,
            anchor_x="center"
        )
        
        # Options du menu (créées dynamiquement)
        self.menu_text_objects = []
        self.update_menu_text_objects()
        
        # Version du jeu
        self.version_text = arcade.Text(
            "Version 1.0 - Game Jam 2025",
            10, 10,
            (150, 150, 150), 12
        )
    
    def update_menu_text_objects(self):
        """Crée les objets Text du menu (valeurs initiales)"""
        self.menu_text_objects.clear()
        
        for i, option in enumerate(self.menu_options):
            text_obj = arcade.Text(
                option,
                SCREEN_WIDTH // 2, 0,  # Position sera mise à jour dans draw_menu_options
                self.option_color, 26,
                anchor_x="center",
                bold=False
            )
            self.menu_text_objects.append(text_obj)
    
    def start_background_music(self):
        """Démarre la musique de fond en boucle"""
        if self.sound_enabled and self.sound_back:
            try:
                # Jouer avec un volume réduit (sans looping pour compatibilité)
                self.background_music_player = arcade.play_sound(
                    self.sound_back, volume=0.3
                )
                print("Musique de fond démarrée")
            except Exception as e:
                print(f"Erreur lors du démarrage de la musique: {e}")
                self.sound_enabled = False
    
    def stop_background_music(self):
        """Arrête la musique de fond"""
        if self.background_music_player:
            try:
                self.background_music_player.pause()
                self.background_music_player = None
                print("Musique de fond arrêtée")
            except Exception as e:
                print(f"Erreur lors de l'arrêt de la musique: {e}")
    
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
        
        # Version (objet Text)
        self.version_text.draw()
        
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
        
        # Zoom + oscillation pour l'animation
        scale = 1.0 + 0.08 * math.sin(self.animation_timer * 0.05)
        glow = 0
        
        # Mettre à jour les objets Text avec les animations
        # Titre principal avec animation de taille et couleur
        self.title_text.x = title_x
        self.title_text.y = title_y
        self.title_text.font_size = int(54 * scale)  # Animation de zoom
        self.title_text.color = (0, glow, 255)  # Animation de couleur
        self.title_text.draw()
        
        # Sous-titre (position fixe)
        self.subtitle_text.x = title_x
        self.subtitle_text.y = title_y - 60
        self.subtitle_text.draw()
    
    def draw_menu_options(self):
        start_y = SCREEN_HEIGHT // 2 + 50
        option_height = 70
        
        for i, option in enumerate(self.menu_options):
            y_pos = start_y - (i * option_height)
            
            if i == self.selected_option:
                # Pulsation néon pour le fond
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
            
            # Utiliser l'objet Text avec les animations
            text_obj = self.menu_text_objects[i]
            text_obj.x = SCREEN_WIDTH // 2
            text_obj.y = y_pos
            text_obj.color = color
            text_obj.bold = (i == self.selected_option)
            text_obj.draw()
    
    def draw_controls(self):
        # Utiliser l'objet Text pour les contrôles (pas d'animation nécessaire)
        self.controls_text.draw()
    
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
        """Gère la sélection d'une option du menu"""
        if self.selected_option == 0:  # Démarrer l'Opération
            # Arrêter la musique de fond
            self.stop_background_music()
            
            # Lancer le jeu principal
            from scenes.main_scene import MainScene
            main_scene = MainScene()
            self.window.show_view(main_scene)
            
        elif self.selected_option == 1:  # Manuel Galactique
            # Garder la musique pour les instructions
            instructions = InstructionsView()
            self.window.show_view(instructions)
            
        elif self.selected_option == 2:  # Éjecter du Système
            arcade.exit()
    
    def show_instructions(self):
        instructions_view = InstructionsView()
        self.window.show_view(instructions_view)
    
    def on_update(self, delta_time):
        self.animation_timer += delta_time * 60
        if self.fade_alpha > 0:
            self.fade_alpha -= delta_time * 200
        
        # Gérer la boucle de musique manuellement
        if (self.sound_enabled and self.sound_back and 
            self.background_music_player and 
            not self.background_music_player.playing):
            # Redémarrer la musique quand elle se termine
            try:
                self.background_music_player = arcade.play_sound(
                    self.sound_back, volume=0.3
                )
            except Exception as e:
                print(f"Erreur lors du redémarrage de la musique: {e}")
                self.sound_enabled = False


class InstructionsView(arcade.View):
    
    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.BLACK
        
        # Créer les objets Text pour de meilleures performances
        self.create_instruction_texts()
    
    def create_instruction_texts(self):
        """Crée tous les objets Text pour les instructions"""
        # Titre
        self.title_text = arcade.Text(
            "📜 MANUEL GALACTIQUE",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100,
            arcade.color.GOLD, 32,
            anchor_x="center", bold=True
        )
        
        # Instructions de retour
        self.return_text = arcade.Text(
            "⟵ ÉCHAP pour retourner au menu",
            SCREEN_WIDTH // 2, 50,
            (180, 180, 180), 16,
            anchor_x="center"
        )
        
        # Contenu du manuel (créé dynamiquement)
        self.content_texts = []
        instructions = [
            "🚀 NAVIGATION SPATIALE",
            "",
            "• Utilisez les FLÈCHES pour déplacer votre agent",
            "• Appuyez sur ESPACE pour interagir avec les consoles",
            "• Visitez le Bureau des Missions pour recevoir des quêtes",
            "",
            "🎯 SYSTÈME DE MISSIONS",
            "",
            "• Mission d'Exploration: Contrôlez votre héros automatiquement",
            "• Mission de Combat: Bataille spatiale intense",
            "• Gagnez de l'or et pariez sur les résultats",
            "",
            "💰 ÉCONOMIE GALACTIQUE",
            "",
            "• Chaque mission rapporte 100 crédits",
            "• Pariez sur le succès ou l'échec des missions",
            "• Doublez vos mises en cas de prédiction correcte",
            "",
            "⚡ CONSEILS STRATÉGIQUES",
            "",
            "• Observez la santé de votre héros avant de parier",
            "• Les missions deviennent plus difficiles avec le temps",
            "• Gérez vos ressources avec prudence"
        ]
        
        y_pos = SCREEN_HEIGHT - 160
        for line in instructions:
            if line.startswith("🚀") or line.startswith("🎯") or line.startswith("💰") or line.startswith("⚡"):
                color = arcade.color.CYAN
                size = 20
            elif line == "":
                color = arcade.color.WHITE
                size = 16
            else:
                color = arcade.color.LIGHT_GRAY
                size = 18
            
            text_obj = arcade.Text(line, 60, y_pos, color, size)
            self.content_texts.append(text_obj)
            y_pos -= 25
    
    def on_draw(self):
        self.clear()
        
        # Dessiner tous les textes avec les objets Text (plus performant)
        self.title_text.draw()
        
        # Dessiner tout le contenu du manuel
        for text_obj in self.content_texts:
            text_obj.draw()
        
        # Instructions de retour
        self.return_text.draw()
    
    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            menu_scene = MenuScene()
            self.window.show_view(menu_scene)
