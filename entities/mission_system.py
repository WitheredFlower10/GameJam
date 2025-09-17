import random
from utils.constants import MISSION_DURATION, CREDIT_INITIAL
from mini_games.terminal import MainTerminal


class MissionSystem:
    
    def __init__(self):
        self.current_mission = None
        self.mission_timer = 0
        self.available_missions = []
        self.ship_interaction_points = []
        
        # Système de paris
        self.betting_active = False
        self.bet_amount = 0
        self.bet_type = None  # "success" ou "failure"
        self.bet_placed = False
        self.bet_result = None
        
        # Économie
        self.gold=CREDIT_INITIAL
        
        # État temporaire pour l'UI de pari
        self.temp_bet_type = None
        self.temp_bet_amount = 100

        # Ordonnancement des missions
        self.missions_assigned_count = 0

        self.terminal_on = False

        
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
                'name': 'Exploration Planétaire',
                'description': "Explorer une planète et trouver un artefact",
                'type': 'Exploration',
                'difficulty': 2,
                'duration': 60,
                'reward': 150
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
            # Première interaction: Exploration, seconde: Élimination (mission finale)
            if self.missions_assigned_count == 0:
                exploration = [m for m in self.available_missions if m.get('type') == 'Exploration']
                mission_template = exploration[0] if exploration else random.choice(self.available_missions)
            else:
                elimination = [m for m in self.available_missions if m.get('type') == 'Élimination']
                mission_template = elimination[0] if elimination else random.choice(self.available_missions)
            
            self.current_mission = mission_template.copy()
            self.current_mission['progress'] = 0
            self.current_mission['start_time'] = self.mission_timer
            
            if self.hero:
                self.hero.start_mission(mission_template)
            
            # Récompense immédiate de vente de mission
            self.gold += 100
            self.missions_assigned_count += 1
            
            print(f"Mission '{self.current_mission['name']}' assignée au héros!")
    
    def update(self, delta_time):
        self.mission_timer += delta_time
        
        if self.current_mission:
            # Mettre à jour la progression de la mission
            if self.hero:
                self.current_mission['progress'] = self.hero.get_progress_percentage()
                
                # Vérifier si la mission de bataille est terminée
                if (self.hero.battle_mission and 
                    self.hero.battle_mission.mission_completed):
                    self.complete_mission()
                # Vérifier si la mission est terminée normalement
                elif self.hero.is_mission_complete():
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
    
    def interact_with_point(self, point_name):
        # Gérer les interactions avec les points d'intérêt
        if point_name == "Bureau des Missions":
            if not self.current_mission:
                self.start_random_mission()
                return "Mission assignée au héros !"
            else:
                return "Une mission est déjà en cours."
        elif point_name == "Amélioration Surveillance":
            return "Surveillance améliorée !"
        elif point_name == "Station de Paris":
            if not self.current_mission:
                return "Aucune mission active pour parier."
            elif self.bet_placed:
                return "Un pari est déjà placé sur cette mission."
            else:
                self.betting_active = True
                self.temp_bet_type = None
                self.temp_bet_amount = min(100, max(10, self.gold)) if self.gold > 0 else 0
                return "Interface de paris ouverte !"
        elif point_name == "Analyse de Données":
            return "Données analysées !"
        elif point_name == "Terminal":
            self.terminal_on = True
        else:
            return "Interaction effectuée."
    
    def set_ship_interaction_points(self, points):
        self.ship_interaction_points = points
    
    def place_bet(self, bet_type, amount):
        # Placer un pari sur la mission
        if not self.current_mission:
            return "Aucune mission active."
        if self.bet_placed:
            return "Un pari est déjà placé."
        if amount <= 0:
            return "Montant invalide."
        if amount > self.gold:
            return "Fonds insuffisants."
        
        self.bet_type = bet_type  # "success" ou "failure"
        self.bet_amount = amount
        self.bet_placed = True
        self.betting_active = False
        # Débiter immédiatement les fonds pariés
        self.gold -= amount
        
        return f"Pari de {amount} crédits placé sur {bet_type} !"
    
    def calculate_bet_result(self):
        # Calculer le résultat du pari
        if not self.bet_placed:
            return None
        
        # Déterminer si la MISSION DE BATAILLE (mission principale du héros) a réussi
        # C'est sur cette mission qu'on parie
        mission_success = False
        
        if self.hero and self.hero.battle_mission:
            # La mission de bataille est réussie si des ennemis ont été détruits
            mission_success = self.hero.battle_mission.enemies_destroyed > 0
            print(f"Debug - Mission de bataille du héros:")
            print(f"Debug - Ennemis détruits: {self.hero.battle_mission.enemies_destroyed}")
            print(f"Debug - Mission de bataille réussie: {mission_success}")
        else:
            # Fallback pour d'autres types de missions
            mission_success = self.hero.is_mission_complete() if self.hero else False
            print(f"Debug - Mission réussie (autre type): {mission_success}")
        
        # Créer un résultat détaillé
        self.bet_result = {
            'bet_type': self.bet_type,
            'bet_amount': self.bet_amount,
            'mission_success': mission_success,
            'won': False,
            'winnings': 0,
            'message': ""
        }
        
        # Calculer les gains/pertes
        if self.bet_type == "success" and mission_success:
            # Pari gagné sur la réussite de la MISSION DE BATAILLE
            self.bet_result['won'] = True
            self.bet_result['winnings'] = self.bet_amount * 2
            self.bet_result['message'] = f"🎉 PARI GAGNÉ ! 🎉\nVous aviez parié sur la RÉUSSITE\nMission de bataille du héros: RÉUSSIE ✅\nGains: +{self.bet_result['winnings']} crédits"
            # Créditer l'or (double du montant misé)
            self.gold += self.bet_result['winnings']
        elif self.bet_type == "failure" and not mission_success:
            # Pari gagné sur l'échec de la MISSION DE BATAILLE
            self.bet_result['won'] = True
            self.bet_result['winnings'] = self.bet_amount * 2
            self.bet_result['message'] = f"🎉 PARI GAGNÉ ! 🎉\nVous aviez parié sur l'ÉCHEC\nMission de bataille du héros: ÉCHOUÉE ❌\nGains: +{self.bet_result['winnings']} crédits"
            # Créditer l'or (double du montant misé)
            self.gold += self.bet_result['winnings']
        else:
            # Pari perdu
            self.bet_result['won'] = False
            self.bet_result['winnings'] = -self.bet_amount
            if self.bet_type == "success":
                self.bet_result['message'] = f"💸 PARI PERDU 💸\nVous aviez parié sur la RÉUSSITE\nMission de bataille du héros: ÉCHOUÉE ❌\nPertes: -{self.bet_amount} crédits"
            else:
                self.bet_result['message'] = f"💸 PARI PERDU 💸\nVous aviez parié sur l'ÉCHEC\nMission de bataille du héros: RÉUSSIE ✅\nPertes: -{self.bet_amount} crédits"
        
        return self.bet_result
    
    def close_betting_interface(self):
        self.betting_active = False
    
    def get_betting_info(self):
        if not self.betting_active:
            return None
        
        return {
            'mission_name': self.current_mission['name'] if self.current_mission else "Aucune",
            'mission_progress': self.hero.get_progress_percentage() if self.hero else 0,
            'hero_health': self.hero.get_health_percentage() if self.hero else 0,
            'gold': self.gold,
            'temp_bet_type': self.temp_bet_type,
            'temp_bet_amount': self.temp_bet_amount
        }
    
    def is_mission_finished(self):
        # Vérifier si la mission est terminée
        if not self.current_mission:
            return False
        
        if self.hero and self.hero.battle_mission:
            return self.hero.battle_mission.is_mission_finished()
        
        return False
