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
        self.music_should_loop = True  # Flag pour contrôler la boucle

        
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
        
        # Marquer que les textes doivent être créés au premier draw
        self.text_objects_created = False
        self.use_fallback_text = False
        
        # Démarrer la musique de fond
        self.start_background_music()
    
    def create_text_objects(self):
        """Crée les objets Text pour de meilleures performances - adapté au fullscreen"""
        try:
            # Obtenir la taille réelle de l'écran
            screen_w = self.window.width
            screen_h = self.window.height
            
            # Titre principal (fixe, sans zoom) - adapté à la taille d'écran
            title_size = max(54, int(screen_h * 0.08))  # Taille proportionnelle
            self.title_text = arcade.Text(
                "The Observer Protocol",
                screen_w // 2, screen_h - int(screen_h * 0.15),
                (0, 0, 255), title_size,
                anchor_x="center", bold=True
            )
        
            # Sous-titre
            subtitle_size = max(20, int(screen_h * 0.03))
            self.subtitle_text = arcade.Text(
                "Centre de Commande Intergalactique",
                screen_w // 2, screen_h - int(screen_h * 0.25),
                self.subtitle_color, subtitle_size,
                anchor_x="center"
            )
            
            # Contrôles
            controls_size = max(16, int(screen_h * 0.025))
            
            # Texte des contrôles adapté selon l'OS
            import platform
            if platform.system() == "Darwin":  # macOS
                controls_text = "Naviguez avec ↑↓  |  Validez avec ENTRÉE  |  Cmd+F: Fullscreen (menu uniquement)"
            else:
                controls_text = "Naviguez avec ↑↓  |  Validez avec ENTRÉE  |  F11: Fullscreen (menu uniquement)"
                
            self.controls_text = arcade.Text(
                controls_text,
                screen_w // 2, int(screen_h * 0.15),
                (180, 180, 180), controls_size,
                anchor_x="center"
            )
            
            # Version du jeu
            version_size = max(12, int(screen_h * 0.02))
            self.version_text = arcade.Text(
                "Version 1.0 - Game Jam 2025",
                10, 10,
                (150, 150, 150), version_size
            )
            
            # Options du menu (créées dynamiquement)
            self.menu_text_objects = []
            self.update_menu_text_objects()
            
        except Exception as e:
            print(f"Erreur création objets Text: {e}")
            # Fallback: utiliser draw_text classique
            self.text_objects_created = False
            self.use_fallback_text = True
    
    def update_menu_text_objects(self):
        """Crée les objets Text du menu (valeurs initiales) - adaptatif"""
        self.menu_text_objects.clear()
        
        screen_h = self.window.height
        menu_font_size = max(26, int(screen_h * 0.035))  # Taille adaptative
        
        for i, option in enumerate(self.menu_options):
            text_obj = arcade.Text(
                option,
                self.window.width // 2, 0,  # Position sera mise à jour dans draw_menu_options
                self.option_color, menu_font_size,
                anchor_x="center",
                bold=False
            )
            self.menu_text_objects.append(text_obj)
    
    def on_resize_event(self, width, height):
        """Appelé quand la fenêtre change de taille (toggle fullscreen)"""
        print(f"Redimensionnement détecté: {width}x{height}")
        # Forcer la recréation des objets Text avec les nouvelles dimensions
        self.text_objects_created = False
        self.use_fallback_text = False
    
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
        # Désactiver la boucle automatique
        self.music_should_loop = False
        
        if self.background_music_player:
            try:
                self.background_music_player.delete() 
                self.background_music_player = None
                print("Musique de fond arrêtée")
            except Exception as e:
                print(f"Erreur lors de l'arrêt de la musique: {e}")
                # Forcer l'arrêt en supprimant la référence
                self.background_music_player = None
    
    def on_draw(self):
        self.clear()
        
        # Créer les objets Text au premier draw (quand le canvas est attaché)
        if not self.text_objects_created:
            self.create_text_objects()
            self.text_objects_created = True
        
        # Fond spatial
        self.draw_space_background()
        
        # Dessiner tous les textes avec les objets Text (plus performant)
        if not self.use_fallback_text:
            try:
                self.title_text.draw()
                self.subtitle_text.draw()
                self.controls_text.draw()
                self.version_text.draw()
                
                # Dessiner les options du menu avec effets
                self.draw_menu_options()
            except Exception as e:
                print(f"Erreur draw Text objects: {e}")
                self.use_fallback_text = True
        
        if self.use_fallback_text:
            self.draw_fallback_text()
        
        # Effet fondu - adaptatif au fullscreen
        if self.fade_alpha > 0:
            screen_w = self.window.width
            screen_h = self.window.height
            arcade.draw_lrbt_rectangle_filled(
                0, screen_w, 0, screen_h,
                (0, 0, 0, int(self.fade_alpha))
            )
    
    def draw_space_background(self):
        """ Fond étoilé coloré avec effet galaxie - adapté au fullscreen """
        screen_w = self.window.width
        screen_h = self.window.height
        
        for i in range(200):
            x = (i * 37 + int(self.animation_timer * 1.5)) % screen_w
            y = (i * 73) % screen_h
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
        
        # Effet "scanlines" rétro adaptatif
        for y in range(0, screen_h, 4):
            arcade.draw_line(0, y, screen_w, y, (0, 0, 0, 40), 1)
    
    def draw_fallback_text(self):
        """Méthode fallback en cas de problème avec les objets Text"""
        screen_w = self.window.width
        screen_h = self.window.height
        
        # Titre avec draw_text classique
        arcade.draw_text("The Observer Protocol", 
                        screen_w // 2, screen_h - int(screen_h * 0.15),
                        (0, 0, 255), max(54, int(screen_h * 0.08)),
                        anchor_x="center")
        
        # Sous-titre
        arcade.draw_text("Centre de Commande Intergalactique",
                        screen_w // 2, screen_h - int(screen_h * 0.25),
                        self.subtitle_color, max(20, int(screen_h * 0.03)),
                        anchor_x="center")
        
        # Contrôles
        import platform
        if platform.system() == "Darwin":  # macOS
            controls_text = "Naviguez avec ↑↓  |  Validez avec ENTRÉE  |  Cmd+F: Fullscreen (menu uniquement)"
        else:
            controls_text = "Naviguez avec ↑↓  |  Validez avec ENTRÉE  |  F11: Fullscreen (menu uniquement)"
            
        arcade.draw_text(controls_text,
                        screen_w // 2, int(screen_h * 0.15),
                        (180, 180, 180), max(16, int(screen_h * 0.025)),
                        anchor_x="center")
        
        # Version
        arcade.draw_text("Version 1.0 - Game Jam 2025",
                        10, 10, (150, 150, 150), max(12, int(screen_h * 0.02)))
        
        # Options du menu
        start_y = screen_h // 2 + int(screen_h * 0.07)
        option_height = int(screen_h * 0.09)
        
        for i, option in enumerate(self.menu_options):
            y_pos = start_y - (i * option_height)
            color = self.option_hover_color if i == self.selected_option else self.option_color
            
            arcade.draw_text(option, screen_w // 2, y_pos, color,
                           max(26, int(screen_h * 0.035)), anchor_x="center")
    
    
    def draw_menu_options(self):
        screen_w = self.window.width
        screen_h = self.window.height
        start_y = screen_h // 2 + int(screen_h * 0.07)
        option_height = int(screen_h * 0.09)
        
        for i, option in enumerate(self.menu_options):
            y_pos = start_y - (i * option_height)
            
            if i == self.selected_option:
                # Pulsation néon pour le fond - adaptatif
                pulse = 150 + 100 * math.sin(self.animation_timer * 0.1)
                color = self.option_hover_color
                glow_color = (color[0], color[1], color[2], int(pulse))
                glow_width = int(screen_w * 0.4)
                glow_height = int(screen_h * 0.04)
                arcade.draw_lrbt_rectangle_filled(
                    screen_w // 2 - glow_width, screen_w // 2 + glow_width,
                    y_pos - glow_height, y_pos + glow_height,
                    glow_color
                )
            else:
                color = self.option_color
            
            # Utiliser l'objet Text avec les animations - adaptatif
            text_obj = self.menu_text_objects[i]
            text_obj.x = screen_w // 2
            text_obj.y = y_pos
            text_obj.color = color
            text_obj.bold = (i == self.selected_option)
            text_obj.draw()
    
    
    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP or key == arcade.key.Z:
            self.selected_option = (self.selected_option - 1) % len(self.menu_options)
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.selected_option = (self.selected_option + 1) % len(self.menu_options)
        elif key == arcade.key.ENTER or key == arcade.key.SPACE or key == arcade.key.F:
            self.select_option()
        elif key == arcade.key.ESCAPE:
            arcade.exit()
    
    def select_option(self):
        """Gère la sélection d'une option du menu"""
        if self.selected_option == 0:  # Démarrer l'Opération
            # Arrêter la musique de fond
            self.stop_background_music()
            
            # Désactiver le toggle fullscreen
            if hasattr(self.window, 'disable_fullscreen_toggle'):
                self.window.disable_fullscreen_toggle()
            
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
        
        # Gérer la boucle de musique manuellement (seulement si autorisée)
        if (self.music_should_loop and self.sound_enabled and self.sound_back and 
            self.background_music_player and 
            not self.background_music_player.playing):
            # Redémarrer la musique quand elle se termine
            try:
                self.background_music_player = arcade.play_sound(
                    self.sound_back, volume=0.3
                )
                print("Musique de fond redémarrée")
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
            (0, 255, 220), 32,
            anchor_x="center", bold=True
        )
        
        # Instructions de retour
        self.return_text = arcade.Text(
            "⟵ ÉCHAP pour retourner au menu",
            SCREEN_WIDTH // 2, 50,
            (180, 180, 180), 16,
            anchor_x="center"
        )
        
        self.content_texts = []
        instructions = [
            "Bienvenue Agent ! Voici vos directives :",
            "",
            "🎯 Votre mission :",
            "• Donner les quêtes aux héros interstellaires",
            "• Superviser leur progression depuis la base",
            "• Faire la maintenance du vaisseau",
            "",
            "🎮 Contrôles :",
            "• FLÈCHES : Déplacer votre avatar",
            "• ESPACE : Interagir avec un terminal",
            "",
            "🛰️ Surveillance :",
            "• L'écran central affiche la mission en cours",
            "• Les héros agissent seuls, mais vous pouvez parier sur leur réussite",
            "",
            "🏆 Objectif final :",
            "• Accomplir vos tâches pour mieux voir le héros",
            "• Maximiser la réussite de vos paris",
            "• Gagner le plus d'argent possible"
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
