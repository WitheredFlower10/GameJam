import arcade
from utils.constants import AGENT_COLOR, AGENT_SCALE, AGENT_MOVEMENT_SPEED, AGENT_STATE_IDLE, AGENT_STATE_MOVING, SCREEN_WIDTH


class Agent(arcade.Sprite):
    
    def __init__(self):
        super().__init__()
        
        # Apparence
        self.texture = arcade.make_soft_square_texture(32, AGENT_COLOR, outer_alpha=255)
        self.scale = AGENT_SCALE
        
        # S'assurer que le sprite est correctement initialisé
        self.width = 32
        self.height = 32
        
        # Mouvement
        self.change_x = 0
        self.change_y = 0
        self.speed = AGENT_MOVEMENT_SPEED
        
        # État
        self.state = AGENT_STATE_IDLE
        
        # Systèmes liés
        self.mission_system = None
        self.current_interaction = None
        
        # Contrôles
        self.left_pressed = False
        self.right_pressed = False
        self.interact_pressed = False
    
    def set_mission_system(self, mission_system):
        self.mission_system = mission_system
    
    def update(self, delta_time):
        super().update()
        
        # Mettre à jour le mouvement
        self.update_movement()
        
        # Vérifier les interactions
        self.check_interactions()
    
    def update_movement(self):
        # Calculer la vitesse horizontale
        self.change_x = 0
        
        if self.left_pressed and not self.right_pressed:
            self.change_x = -self.speed
            self.state = AGENT_STATE_MOVING
        elif self.right_pressed and not self.left_pressed:
            self.change_x = self.speed
            self.state = AGENT_STATE_MOVING
        else:
            self.state = AGENT_STATE_IDLE
        
        # Empêcher de sortir des limites du vaisseau
        if self.center_x < 50:
            self.center_x = 50
            self.change_x = 0
        elif self.center_x > SCREEN_WIDTH - 50:
            self.center_x = SCREEN_WIDTH - 50
            self.change_x = 0
    
    def check_interactions(self):
        # Vérifier s'il y a des points d'interaction à proximité
        if self.mission_system:
            nearby_interactions = self.mission_system.get_nearby_interactions(self.center_x)
            if nearby_interactions and self.interact_pressed:
                # Interagir avec le point le plus proche
                closest = min(nearby_interactions, key=lambda x: abs(x['x'] - self.center_x))
                self.interact_with_point(closest)
    
    def interact_with_point(self, interaction_point):
        # Utiliser le système de missions pour gérer l'interaction
        if self.mission_system:
            result = self.mission_system.interact_with_point(interaction_point['name'])
            print(f"Interaction avec {interaction_point['name']}: {result}")
            self.interact_pressed = False
    
    def on_key_press(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True
        elif key == arcade.key.SPACE:
            self.interact_pressed = True
    
    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False
        elif key == arcade.key.SPACE:
            self.interact_pressed = False
    
