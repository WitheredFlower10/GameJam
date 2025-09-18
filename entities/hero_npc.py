import arcade
import os
from utils.constants import AGENT_SCALE, SCREEN_WIDTH, SCREEN_HEIGHT


class HeroNPC(arcade.Sprite):
    """Sprite du héros présent sur le vaisseau pour lancer les missions"""
    
    def __init__(self, x, y):
        super().__init__()
        
        # Position
        self.center_x = x
        self.center_y = y
        
        # Apparence
        self.scale = AGENT_SCALE  # Même taille que l'agent
        
        # État
        self.visible = True  # Contrôle la visibilité
        self.is_on_mission = False
        
        # Animation de respiration
        self.breathing_textures = []
        self.animation_index = 0
        self.animation_timer = 0.0
        self.animation_speed = 0.6  # secondes par frame
        
        # Charger les textures du héros
        self.load_hero_textures()
        
        # Point d'interaction au-dessus de la tête
        self.interaction_offset_y = 40  # Pixels au-dessus de la tête
        
    def load_hero_textures(self):
        """Charge les textures du héros pour un affichage animé"""
        # Chercher les textures de respiration du héros
        base_candidates = [
            'assets',
            os.path.join(os.path.dirname(__file__), '..', 'assets'),
        ]
        base_candidates = [os.path.normpath(p) for p in base_candidates]
        
        for base in base_candidates:
            breathing_dir = os.path.join(base, 'breathing', 'hero')
            if os.path.isdir(breathing_dir):
                for i in range(2):  # Charger les frames 0 et 1
                    hero_texture_path = os.path.join(breathing_dir, f'breath-frame-{i}.png')
                    if os.path.exists(hero_texture_path):
                        try:
                            self.breathing_textures.append(arcade.load_texture(hero_texture_path))
                            print(f"Texture respiration héros chargée: {hero_texture_path}")
                        except Exception as e:
                            print(f"Erreur chargement texture {hero_texture_path}: {e}")
        
        # Fallback - carré coloré bleu
        if not self.breathing_textures:
            self.breathing_textures.append(arcade.make_soft_square_texture(32, (0, 150, 255), outer_alpha=255))
            print("Aucune texture breath-frame-*.png trouvée, utilisation du fallback bleu")
        
        # Définir la première texture comme texture actuelle
        self.texture = self.breathing_textures[0]
    
    
    def update(self, delta_time):
        """Mise à jour simple - juste la gestion de visibilité et l'animation de respiration"""
        # Pas d'animation, juste la gestion de visibilité
        self.animation_timer += delta_time
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0.0
            self.animation_index = (self.animation_index + 1) % len(self.breathing_textures)
            self.texture = self.breathing_textures[self.animation_index]
    
    def get_interaction_point(self):
        """Retourne les coordonnées du point d'interaction au-dessus de la tête"""
        if not self.visible:
            return None
            
        return {
            'x': self.center_x,
            'y': self.center_y + self.interaction_offset_y,
            'type': 'hero_missions',
            'name': 'Parler au Héros',
            'description': 'Donner des missions au héros'
        }
    
    def set_on_mission(self, on_mission):
        """Contrôle la visibilité du héros selon s'il est en mission"""
        self.is_on_mission = on_mission
        self.visible = not on_mission
        
        # Utiliser alpha pour la visibilité (comme un sprite normal)
        if not self.visible:
            self.alpha = 0
        else:
            self.alpha = 255
    
    def draw_interaction_point(self, camera=None, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT):
        """Dessine le point d'interaction au-dessus de la tête"""
        if not self.visible or self.alpha == 0:
            return
            
        # Position du point d'interaction
        px = self.center_x
        py = self.center_y + self.interaction_offset_y
        
        # Dessiner directement en coordonnées monde (Arcade gère la caméra)
        arcade.draw_circle_filled(px, py, 8, (255, 255, 0))
        arcade.draw_circle_outline(px, py, 8, (255, 255, 255), 2)
