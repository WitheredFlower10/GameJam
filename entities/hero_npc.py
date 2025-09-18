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
        
        # Charger une texture simple du héros
        self.load_hero_texture()
        
        # Point d'interaction au-dessus de la tête
        self.interaction_offset_y = 40  # Pixels au-dessus de la tête
        
    def load_hero_texture(self):
        """Charge la première texture du héros pour un affichage statique"""
        # Chercher la première texture hero-walk-frame-0.png
        base_candidates = [
            'assets',
            os.path.join(os.path.dirname(__file__), '..', 'assets'),
        ]
        base_candidates = [os.path.normpath(p) for p in base_candidates]
        
        for base in base_candidates:
            walk_dir = os.path.join(base, 'walk')
            if os.path.isdir(walk_dir):
                hero_texture_path = os.path.join(walk_dir, 'hero-walk-frame-0.png')
                if os.path.exists(hero_texture_path):
                    try:
                        self.texture = arcade.load_texture(hero_texture_path)
                        print(f"Texture héros chargée: {hero_texture_path}")
                        return
                    except Exception as e:
                        print(f"Erreur chargement texture {hero_texture_path}: {e}")
        
        # Fallback - carré coloré bleu
        self.texture = arcade.make_soft_square_texture(32, (0, 150, 255), outer_alpha=255)
        print("Aucune texture hero-walk-frame-0.png trouvée, utilisation du fallback bleu")
    
    
    def update(self, delta_time):
        """Mise à jour simple - juste la gestion de visibilité"""
        # Pas d'animation, juste la gestion de visibilité
        pass
    
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
