import random
from utils.constants import MISSION_DURATION


class MissionSystem:
    
    def __init__(self):
        self.current_mission = None
        self.mission_timer = 0
        self.available_missions = []
        self.ship_interaction_points = []
        
        self.create_mission_templates()
    
    def create_mission_templates(self):
        self.available_missions = [
            {
                'name': 'Sauvetage de Colonie',
                'description': 'Sauver une colonie attaquée par des pirates',
                'difficulty': 1,
                'duration': 45,
                'reward': 100
            },
            {
                'name': 'Exploration de Ruines',
                'description': 'Explorer d\'anciennes ruines alien',
                'difficulty': 2,
                'duration': 60,
                'reward': 150
            },
            {
                'name': 'Élimination de Menace',
                'description': 'Éliminer une menace spatiale',
                'type': 'Élimination',
                'difficulty': 3,
                'duration': 90,
                'reward': 250
            },
            {
                'name': 'Livraison Urgente',
                'description': 'Livrer des fournitures médicales',
                'difficulty': 1,
                'duration': 30,
                'reward': 80
            },
            {
                'name': 'Reconnaissance',
                'description': 'Effectuer une reconnaissance en territoire ennemi',
                'difficulty': 2,
                'duration': 75,
                'reward': 200
            }
        ]
    
    def set_hero(self, hero):
        self.hero = hero
    
    def start_random_mission(self):
        if not self.current_mission:
            # Forcer une mission d'élimination pour tester la bataille
            elimination_missions = [m for m in self.available_missions if m.get('type') == 'Élimination']
            if elimination_missions:
                mission_template = elimination_missions[0]
            else:
                mission_template = random.choice(self.available_missions)
            
            self.current_mission = mission_template.copy()
            self.current_mission['progress'] = 0
            self.current_mission['start_time'] = self.mission_timer
            
            if self.hero:
                self.hero.start_mission(mission_template)
            
            print(f"Mission '{self.current_mission['name']}' assignée au héros!")
    
    def update(self, delta_time):
        self.mission_timer += delta_time
        
        if self.current_mission:
            # Mettre à jour la progression de la mission
            if self.hero:
                self.current_mission['progress'] = self.hero.get_progress_percentage()
                
                # Vérifier si la mission est terminée
                if self.hero.is_mission_complete():
                    self.complete_mission()
                elif self.hero.is_mission_failed():
                    self.fail_mission()
                elif self.mission_timer - self.current_mission['start_time'] > self.current_mission['duration']:
                    self.timeout_mission()
    
    def complete_mission(self):
        if self.current_mission:
            print(f"Mission '{self.current_mission['name']}' réussie!")
            self.current_mission = None
    
    def fail_mission(self):
        if self.current_mission:
            print(f"Mission '{self.current_mission['name']}' échouée!")
            self.current_mission = None
    
    def timeout_mission(self):
        if self.current_mission:
            print(f"Mission '{self.current_mission['name']}' expirée!")
            self.current_mission = None
    
    def get_nearby_interactions(self, agent_x):
        # Retourner les points d'interaction à proximité de l'agent
        nearby = []
        for point in self.ship_interaction_points:
            if abs(point['x'] - agent_x) < 50:
                nearby.append(point)
        return nearby
    
    def set_ship_interaction_points(self, points):
        self.ship_interaction_points = points
