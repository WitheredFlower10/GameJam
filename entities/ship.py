import arcade
from utils.constants import SHIP_COLOR, SCREEN_WIDTH, SCREEN_HEIGHT, SHIP_SECTIONS


class Ship(arcade.SpriteList):
    
    def __init__(self):
        super().__init__()
        
        self.sections = []
        self.interaction_points = []
        
        self.create_ship_sections()
        self.create_interaction_points()
    
    def create_ship_sections(self):
        section_width = SCREEN_WIDTH // SHIP_SECTIONS
        
        for i in range(SHIP_SECTIONS):
            section = arcade.SpriteSolidColor(section_width, SCREEN_HEIGHT, SHIP_COLOR)
            section.center_x = i * section_width + section_width // 2
            section.center_y = SCREEN_HEIGHT // 2
            self.sections.append(section)
            self.append(section)
    
    def create_interaction_points(self):
        # Section Avant - Bureau des missions
        self.interaction_points.append({
            'x': SCREEN_WIDTH // 6,
            'y': 150,
            'type': 'mission_desk',
            'name': 'Bureau des Missions',
            'description': 'Distribuer des missions aux héros'
        })
        
        # Section Centre - Station de surveillance
        self.interaction_points.append({
            'x': SCREEN_WIDTH // 2,
            'y': 200,
            'type': 'surveillance_upgrade',
            'name': 'Amélioration Surveillance',
            'description': 'Améliorer la qualité de surveillance'
        })
        
        # Section Arrière - Station de paris
        self.interaction_points.append({
            'x': 5 * SCREEN_WIDTH // 6,
            'y': 180,
            'type': 'betting_station',
            'name': 'Station de Paris',
            'description': 'Parier sur la réussite du héros'
        })
        
        # Section Arrière - Analyse de données
        self.interaction_points.append({
            'x': 5 * SCREEN_WIDTH // 6,
            'y': 120,
            'type': 'data_analysis',
            'name': 'Analyse de Données',
            'description': 'Analyser les données du héros'
        })
    
    def draw_interaction_points(self):
        for point in self.interaction_points:
            # Dessiner un indicateur d'interaction
            arcade.draw_circle_filled(point['x'], point['y'], 15, arcade.color.ORANGE)
            arcade.draw_circle_outline(point['x'], point['y'], 15, arcade.color.WHITE, 2)
    
    def get_interaction_points(self):
        return self.interaction_points
