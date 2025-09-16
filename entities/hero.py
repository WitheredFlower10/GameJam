import arcade
import random
from utils.constants import HERO_COLOR, HERO_HEALTH_MAX, HERO_STAMINA_MAX
from utils.constants import HERO_STATE_TRAVELING, HERO_STATE_FIGHTING, HERO_STATE_RESTING, HERO_STATE_FAILED


class Hero(arcade.Sprite):
    
    def __init__(self):
        super().__init__()
        
        self.texture = arcade.make_soft_square_texture(16, HERO_COLOR, outer_alpha=255)
        self.scale = 1.0
        
        self.screen_x = 0
        self.screen_y = 0
        
        self.health = HERO_HEALTH_MAX
        self.max_health = HERO_HEALTH_MAX
        self.stamina = HERO_STAMINA_MAX
        self.max_stamina = HERO_STAMINA_MAX
        
        self.state = HERO_STATE_TRAVELING
        self.state_timer = 0
        
        self.mission_progress = 0
        self.difficulty_level = 1
        
        self.animation_timer = 0
        self.current_animation_frame = 0
        
        self.events = []
        self.last_event_time = 0
        
        # Mission de bataille
        self.battle_mission = None
    
    def update(self, delta_time):
        super().update()
        
        self.state_timer += delta_time
        self.animation_timer += delta_time
        
        # Mettre à jour la mission de bataille si active
        if self.battle_mission:
            self.battle_mission.update(delta_time)
            if self.battle_mission.mission_completed:
                self.mission_progress = 100
                self.battle_mission = None
        
        if self.state == HERO_STATE_TRAVELING:
            self.update_traveling(delta_time)
        elif self.state == HERO_STATE_FIGHTING:
            self.update_fighting(delta_time)
        elif self.state == HERO_STATE_RESTING:
            self.update_resting(delta_time)
        
        self.generate_random_events(delta_time)
    
    def update_traveling(self, delta_time):
        self.screen_x += 30 * delta_time
        
        self.stamina -= 5 * delta_time
        if self.stamina <= 0:
            self.stamina = 0
            self.state = HERO_STATE_RESTING
            self.state_timer = 0
        
        if random.random() < 0.01:
            self.state = HERO_STATE_FIGHTING
            self.state_timer = 0
    
    def update_fighting(self, delta_time):
        if self.animation_timer > 0.2:
            self.current_animation_frame = (self.current_animation_frame + 1) % 4
            self.animation_timer = 0
        
        self.health -= 10 * delta_time
        if self.health <= 0:
            self.health = 0
            self.state = HERO_STATE_FAILED
            return
        
        if self.state_timer > 3.0:
            if random.random() < 0.7:
                self.state = HERO_STATE_TRAVELING
                self.mission_progress += 20
            else:
                self.state = HERO_STATE_RESTING
            self.state_timer = 0
    
    def update_resting(self, delta_time):
        self.stamina += 20 * delta_time
        if self.stamina >= self.max_stamina:
            self.stamina = self.max_stamina
            self.state = HERO_STATE_TRAVELING
            self.state_timer = 0
    
    def generate_random_events(self, delta_time):
        if self.state_timer - self.last_event_time > 2.0:
            if random.random() < 0.3:
                event = self.create_random_event()
                self.events.append(event)
                self.last_event_time = self.state_timer
    
    def create_random_event(self):
        event_types = [
            "Découverte d'un artefact",
            "Rencontre avec un allié",
            "Obstacle détecté",
            "Signal de détresse",
            "Cachette trouvée"
        ]
        
        return {
            'type': random.choice(event_types),
            'time': self.state_timer,
            'impact': random.choice(['positive', 'neutral', 'negative'])
        }
    
    def start_mission(self, mission_data):
        self.health = self.max_health
        self.stamina = self.max_stamina
        self.mission_progress = 0
        self.state = HERO_STATE_TRAVELING
        self.state_timer = 0
        self.screen_x = 0
        self.difficulty_level = mission_data.get('difficulty', 1)
        
        # Démarrer la mission de bataille si c'est une mission de combat
        if mission_data.get('type') == 'Élimination':
            from entities.battle_mission import BattleMission
            self.battle_mission = BattleMission()
            self.battle_mission.start_mission()
    
    def get_health_percentage(self):
        return (self.health / self.max_health) * 100
    
    def get_stamina_percentage(self):
        return (self.stamina / self.max_stamina) * 100
    
    def get_progress_percentage(self):
        return min(100, self.mission_progress)
    
    def is_mission_complete(self):
        return self.mission_progress >= 100
    
    def is_mission_failed(self):
        return self.health <= 0
