import arcade
import random
from utils.constants import HERO_COLOR, HERO_HEALTH_MAX
from utils.constants import HERO_STATE_WAITING_FOR_MISSION, HERO_STATE_FIGHTING, HERO_STATE_FAILED, HERO_STATE_COMPLETED


class Hero(arcade.Sprite):
    
    def __init__(self):
        super().__init__()
        
        self.texture = arcade.make_soft_square_texture(16, HERO_COLOR, outer_alpha=255)
        self.scale = 1.0
        
        self.screen_x = 0
        self.screen_y = 0
        
        self.health = HERO_HEALTH_MAX
        self.max_health = HERO_HEALTH_MAX
        
        self.state = HERO_STATE_WAITING_FOR_MISSION
        self.state_timer = 0
        self.is_in_mission = False  # Booléen pour savoir si le héros est en mission
        
        self.mission_progress = 0
        self.difficulty_level = 1
        
        self.animation_timer = 0
        self.current_animation_frame = 0
        
        self.events = []
        self.last_event_time = 0
        
        # Mission de bataille
        self.battle_mission = None
        # Mission d'exploration
        self.explore_mission = None
    
    def update(self, delta_time):
        super().update()
        
        self.state_timer += delta_time
        self.animation_timer += delta_time
        
        # Mettre à jour la mission de bataille si active
        if self.battle_mission and self.is_in_mission:
            self.battle_mission.update(delta_time)
            if self.battle_mission.mission_completed:
                self.mission_progress = 100
                success = getattr(self.battle_mission, 'success', False)
                self.battle_mission = None
                self.is_in_mission = False
                if self.health <= 0:
                    self.state = HERO_STATE_FAILED
                elif success:
                    self.state = HERO_STATE_COMPLETED
                else:
                    self.state = HERO_STATE_FAILED

        # Mettre à jour la mission d'exploration si active
        if self.explore_mission and self.is_in_mission:
            self.explore_mission.update(delta_time)
            if self.explore_mission.mission_completed:
                self.mission_progress = 100
                success = getattr(self.explore_mission, 'success', False)
                self.explore_mission = None
                self.is_in_mission = False
                if self.health <= 0:
                    self.state = HERO_STATE_FAILED
                elif success:
                    self.state = HERO_STATE_COMPLETED
                else:
                    self.state = HERO_STATE_FAILED
        
        if self.state == HERO_STATE_FIGHTING:
            self.update_fighting(delta_time)
        
        self.generate_random_events(delta_time)
    
    
    def update_fighting(self, delta_time):
        if self.animation_timer > 0.2:
            self.current_animation_frame = (self.current_animation_frame + 1) % 4
            self.animation_timer = 0
        
        # Vérifier si le héros est mort
        if self.health <= 0:
            self.health = 0
            self.state = HERO_STATE_FAILED
            return
    
    
    
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
        self.mission_progress = 0
        self.state = HERO_STATE_FIGHTING
        self.is_in_mission = True
        self.state_timer = 0
        self.screen_x = 0
        self.difficulty_level = mission_data.get('difficulty', 1)
        
        # Démarrer la mission de bataille si c'est une mission de combat
        if mission_data.get('type') == 'Élimination':
            from entities.battle_mission import BattleMission
            import random
            enemies_to_kill = random.randint(5, 6)
            print(f"Mission créée : {enemies_to_kill} ennemis à tuer")
            # Passer l'instance du héros et le nombre d'ennemis à la mission
            self.battle_mission = BattleMission(self, enemies_to_kill)
            self.battle_mission.start_mission()
        elif mission_data.get('type') == 'Exploration':
            from entities.explore_mission import ExploreMission
            self.explore_mission = ExploreMission(self)
            self.explore_mission.start_mission()
    
    def get_health_percentage(self):
        return (self.health / self.max_health) * 100
    
    
    def get_progress_percentage(self):
        return min(100, self.mission_progress)
    
    def is_mission_complete(self):
        return self.mission_progress >= 100
    
    def is_mission_failed(self):
        return self.health <= 0
    
    def get_mission_result(self):
        """Récupère le résultat de la mission (pour les paris)"""
        # Préférer le résultat de la mission active
        if self.battle_mission and self.battle_mission.mission_completed:
            return {
                'success': self.battle_mission.enemies_destroyed >= self.battle_mission.enemies_to_kill,
                'enemies_killed': self.battle_mission.enemies_destroyed,
                'enemies_required': self.battle_mission.enemies_to_kill,
                'hero_health': self.health
            }
        if self.explore_mission and self.explore_mission.mission_completed:
            return {
                'success': getattr(self.explore_mission, 'success', False),
                'hero_health': self.health
            }
        return None
