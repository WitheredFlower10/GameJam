import arcade
from utils.constants import SHIP_COLOR, SCREEN_WIDTH, SCREEN_HEIGHT


class Ship(arcade.SpriteList):
    
    def __init__(self):
        super().__init__()
        
        self.interaction_points = []
        
        self.create_interaction_points()
    
    def create_interaction_points(self):
        # Bureau des missions
        self.interaction_points.append({
            'x': SCREEN_WIDTH // 6,
            'y': 150,
            'type': 'mission_desk',
            'name': 'Bureau des Missions',
            'description': 'Distribuer des missions aux héros'
        })
        
        # Station de surveillance
        self.interaction_points.append({
            'x': SCREEN_WIDTH // 2,
            'y': 200,
            'type': 'surveillance_upgrade',
            'name': 'Amélioration Surveillance',
            'description': 'Améliorer la qualité de surveillance'
        })
        
        # Station de paris
        self.interaction_points.append({
            'x': 5 * SCREEN_WIDTH // 6,
            'y': 180,
            'type': 'betting_station',
            'name': 'Station de Paris',
            'description': 'Parier sur la réussite du héros'
        })
        
        # Analyse de données
        self.interaction_points.append({
            'x': 5 * SCREEN_WIDTH // 6,
            'y': 120,
            'type': 'data_analysis',
            'name': 'Analyse de Données',
            'description': 'Analyser les données du héros'
        })

        # Activer le Terminal
        self.interaction_points.append({
            'x': 2200,
            'y': 250,
            'type': 'terminal',
            'name': 'Terminal',
            'description': 'Accéder au terminal de communication'
        })
    
    def draw_interaction_points(self, camera=None, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT):
        # Obtenir le centre et le zoom de la caméra
        if camera is not None:
            cam_x, cam_y = camera.position
            zoom = getattr(camera, 'zoom', 1.0)
        else:
            cam_x, cam_y = screen_width // 2, screen_height // 2
            zoom = 1.0

        # Limites de l'écran (coordonnées du monde)
        left = cam_x - (screen_width / 2) / zoom
        right = cam_x + (screen_width / 2) / zoom
        bottom = cam_y - (screen_height / 2) / zoom
        top = cam_y + (screen_height / 2) / zoom

        for point in self.interaction_points:
            px, py = point['x'], point['y']
            # Vérifier si le point est dans la vue
            if left <= px <= right and bottom <= py <= top:
                # Dans l'écran, dessiner normalement
                arcade.draw_circle_filled(px, py, 15, arcade.color.ORANGE)
                arcade.draw_circle_outline(px, py, 15, arcade.color.WHITE, 2)
            else:
                # Hors écran, calculer la direction
                dx = px - cam_x
                dy = py - cam_y
                import math
                angle = math.atan2(dy, dx)
                # Afficher la flèche sur le bord de l'écran
                edge_x = cam_x + math.cos(angle) * (screen_width / 2 - 30) / zoom
                edge_y = cam_y + math.sin(angle) * (screen_height / 2 - 30) / zoom
                # Dessiner la flèche
                arcade.draw_triangle_filled(
                    edge_x,
                    edge_y,
                    edge_x - 15 * math.cos(angle - 0.3), edge_y - 15 * math.sin(angle - 0.3),
                    edge_x - 15 * math.cos(angle + 0.3), edge_y - 15 * math.sin(angle + 0.3),
                    arcade.color.YELLOW
                )
                # Afficher le nom du point
                arcade.draw_text(
                    point['name'],
                    edge_x, edge_y + 20,
                    arcade.color.WHITE, 12,
                    anchor_x="center"
                )
    
    def get_interaction_points(self):
        return self.interaction_points
