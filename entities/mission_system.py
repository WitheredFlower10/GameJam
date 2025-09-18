import random
import math
import time
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
        self.bet_type = None  # "success" ou "echec"
        self.bet_placed = False
        self.bet_result = None
        
        # Économie
        self.gold=CREDIT_INITIAL
        
        # État temporaire pour l'UI de pari
        self.temp_bet_type = None
        self.temp_bet_amount = 100
        
        # Timer de pari forcé
        self.betting_timer = None  # Temps de fin du timer
        self.betting_timer_duration = 5.0  # 30 secondes
        self.betting_forced = False  # Flag pour indiquer si le pari est forcé

        # Ordonnancement des missions
        self.missions_assigned_count = 0
        self.missions_launched_count = 0  # Compteur de missions lancées (pour déblocages)

        self.terminal_on = False
        # Demande d'ouverture du mini-jeu Wire Puzzle
        self.wire_puzzle_requested = False
        # Flag pour marquer si le puzzle wire a été complété
        self.wire_puzzle_completed = False

        # Mini-jeu de réparation (réacteur/écran)
        self.repair_requested = False
        self.repair_completed = False
        
        # Mini-jeu de réparation générale
        self.general_repair_requested = False
        self.general_repair_completed = False

        # Mini-jeu scanner ennemis (débloque compteur ennemis)
        self.enemies_screen_requested = False
        self.enemies_screen_completed = False
        # Délai de départ de mission (affichage écran)
        self.travel_end_time = None
        # Compteur de missions réussies (pour déblocages)
        self.missions_completed_success_count = 0
        
        # Référence au ship pour gérer le HeroNPC
        self.ship = None
        
        
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
            # Vérifier que les missions sont disponibles
            if not self.available_missions:
                print("ERREUR: Aucune mission disponible! Réinitialisation...")
                self.create_mission_templates()
            
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
            self.missions_launched_count += 1  # Incrémenter le compteur de missions lancées
            
            # Démarrer le timer de pari forcé
            self.betting_timer = time.time() + self.betting_timer_duration
            self.betting_forced = False
            print(f"Timer de pari démarré: {self.betting_timer_duration} secondes")
            
            print(f"Mission '{self.current_mission['name']}' assignée au héros!")
    
    def update(self, delta_time, ship=None):
        self.mission_timer += delta_time
        # Démarrer la mission quand le compte à rebours est terminé
        if (self.travel_end_time is not None) and (time.time() >= self.travel_end_time) and (self.current_mission is None):
            # Démarrer la mission maintenant
            self.travel_end_time = None
            # Choisir et assigner la mission
            if not self.available_missions:
                print("ERREUR: Aucune mission disponible! Réinitialisation...")
                self.create_mission_templates()
            
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
            self.gold += 100
            self.missions_assigned_count += 1
            self.missions_launched_count += 1  # Incrémenter le compteur de missions lancées
            
            # Démarrer le timer de pari forcé
            self.betting_timer = time.time() + self.betting_timer_duration
            self.betting_forced = False
            print(f"Timer de pari démarré: {self.betting_timer_duration} secondes")
            
            print(f"Mission '{self.current_mission['name']}' assignée au héros après le trajet!")
        
        if self.current_mission:
            # Vérifier le timer de pari forcé
            if (self.betting_timer is not None and 
                time.time() >= self.betting_timer and 
                not self.betting_forced and 
                not self.bet_placed):
                # Forcer l'ouverture du système de pari
                self.betting_forced = True
                self.betting_active = True
                self.temp_bet_type = None
                self.temp_bet_amount = min(100, max(10, self.gold)) if self.gold > 0 else 0
                print("Timer de pari expiré - Système de pari forcé ouvert!")
            
            # Mettre à jour la progression de la mission
            if self.hero:
                self.current_mission['progress'] = self.hero.get_progress_percentage()
                
                # Vérifier si la mission de bataille est terminée
                if (self.hero.battle_mission and 
                    self.hero.battle_mission.mission_completed):
                    self.complete_mission(ship)
                # Vérifier si la mission est terminée normalement
                elif self.hero.is_mission_complete():
                    self.complete_mission(ship)
                elif self.hero.is_mission_failed():
                    self.fail_mission(ship)
                elif self.mission_timer - self.current_mission['start_time'] > self.current_mission['duration']:
                    self.timeout_mission(ship)
    
    def complete_mission(self, ship=None):
        if self.current_mission:
            print(f"Mission '{self.current_mission['name']}' réussie!")
            
            # Calculer le résultat du pari si un pari a été placé
            if self.bet_placed and not self.bet_result:
                self.calculate_bet_result()
                # Pour la mission d'exploration, terminer la mission dès que le pari est calculé
                if self.hero and hasattr(self.hero, 'explore_mission') and self.hero.explore_mission:
                    self.hero.explore_mission.end_mission()
            
            # Incrémenter le nombre de missions réussies
            try:
                self.missions_completed_success_count += 1
            except Exception:
                self.missions_completed_success_count = 1
            self.current_mission = None
            self.travel_end_time = None
            # Réinitialiser le timer de pari
            self.betting_timer = None
            self.betting_forced = False
            # Faire réapparaître le héros
            if ship:
                ship.set_hero_on_mission(False)
    
    def fail_mission(self, ship=None):
        if self.current_mission:
            print(f"Mission '{self.current_mission['name']}' échouée!")
            
            # Calculer le résultat du pari si un pari a été placé
            if self.bet_placed and not self.bet_result:
                self.calculate_bet_result()
                # Pour la mission d'exploration, terminer la mission dès que le pari est calculé
                if self.hero and hasattr(self.hero, 'explore_mission') and self.hero.explore_mission:
                    self.hero.explore_mission.end_mission()
            
            self.current_mission = None
            self.travel_end_time = None
            # Réinitialiser le timer de pari
            self.betting_timer = None
            self.betting_forced = False
            # Faire réapparaître le héros
            if ship:
                ship.set_hero_on_mission(False)
    
    def timeout_mission(self, ship=None):
        if self.current_mission:
            print(f"Mission '{self.current_mission['name']}' expirée!")
            
            # Calculer le résultat du pari si un pari a été placé
            if self.bet_placed and not self.bet_result:
                self.calculate_bet_result()
                # Pour la mission d'exploration, terminer la mission dès que le pari est calculé
                if self.hero and hasattr(self.hero, 'explore_mission') and self.hero.explore_mission:
                    self.hero.explore_mission.end_mission()
            
            self.current_mission = None
            self.travel_end_time = None
            # Faire réapparaître le héros
            if ship:
                ship.set_hero_on_mission(False)
    
    def get_nearby_interactions(self, agent_x):
        # Retourner les points d'interaction à proximité de l'agent (X-only) en utilisant range_x par point
        nearby = []
        # Utiliser la liste dynamique du ship (héros inclus uniquement si visible), fallback sur la liste statique sinon
        points = []
        ship = getattr(self, 'ship', None)
        if ship is not None and hasattr(ship, 'get_interaction_points'):
            try:
                points = ship.get_interaction_points()
            except Exception:
                points = self.ship_interaction_points
        else:
            points = self.ship_interaction_points
        for point in points:
            try:
                # Filtrer tous les points déjà complétés
                if hasattr(self, 'is_point_completed'):
                    if self.is_point_completed(point.get('name', '')):
                        continue
                # Cacher/ignorer le point du héros si le héros n'est pas présent ou si une mission est en cours
                if point.get('type') == 'hero_missions':
                    if self.current_mission:
                        continue
                    hero_npc = getattr(ship, 'hero_npc', None) if ship is not None else None
                    if (hero_npc is None) or (not getattr(hero_npc, 'visible', False)):
                        continue
                px = float(point.get('x', 0.0))
                threshold = float(point.get('range_x', 50.0))
                if abs(px - float(agent_x)) < threshold:
                    nearby.append(point)
            except Exception:
                continue
        return nearby
    
    def interact_with_point(self, point_name, ship=None):
        # Gérer les interactions avec les points d'intérêt
        if point_name == "DONNER LA QUETE":
            # Déclenche uniquement un compte à rebours de 10s avant le démarrage effectif
            if self.current_mission:
                return "Le héros est déjà en mission."
            if getattr(self, 'travel_end_time', None):
                return "Le héros est déjà en route."
            try:
                # Faire disparaître le héros immédiatement
                if ship:
                    ship.set_hero_on_mission(True)
                # Puis démarrer le compte à rebours
                self.travel_end_time = time.time() + 1  # 10 secondes de délai avant départ
                return "Le héros se dirige à la quête. Départ dans 10s."
            except Exception:
                return "Erreur: impossible de démarrer le trajet."
        elif point_name == "REPARATION / VIE":
            # Lancer le wire puzzle pour débloquer l'affichage de la vie
            if getattr(self, 'missions_launched_count', 0) < 1:
                return "Réparation Santé indisponible: lancez d'abord une mission."
            if self.wire_puzzle_completed:
                return "Réparation Santé déjà effectuée."
            self.wire_puzzle_requested = True
            return "Wire Puzzle lancé !"
        elif point_name == "REPARATION / ENNEMIS":
            # Lancer le mini-jeu spécifique pour débloquer le compteur d'ennemis
            if getattr(self, 'missions_completed_success_count', 0) < 1:
                return "Réparation Scanner indisponible: terminez d'abord une mission."
            if self.enemies_screen_completed:
                return "Réparation Scanner déjà effectuée."
            self.enemies_screen_requested = True
            return "Réparation Scanner lancée !"
        elif point_name == "REPARATION GÉNÉRALE":
            # Lancer le mini-jeu de réparation générale
            if self.general_repair_completed:
                return "Réparation générale déjà effectuée."
            self.general_repair_requested = True
            return "Réparation générale lancée !"
        elif point_name == "PARIER":
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
        elif point_name == "TERMINAL":
            self.terminal_on = True
        else:
            return "Interaction effectuée."
    
    def set_ship_interaction_points(self, points):
        self.ship_interaction_points = points
    
    def set_ship(self, ship):
        """Définir la référence au ship pour gérer le HeroNPC"""
        self.ship = ship

    def is_point_completed(self, point_name):
        """Retourne True si le point d'intérêt nommé est complété et ne doit plus s'afficher."""
        try:
            name = str(point_name)
        except Exception:
            name = point_name
        # Réparations spécifiques: disparaissent après réussite
        if name == "REPARATION / VIE":
            return bool(self.wire_puzzle_completed)
        if name == "REPARATION / ENNEMIS":
            return bool(self.enemies_screen_completed)
        if name == "REPARATION GÉNÉRALE":
            return bool(self.general_repair_completed)
        # Par défaut: non complété (affichage autorisé)
        return False
    
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
        
        self.bet_type = bet_type  # "success" ou "echec"
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
        
        # Déterminer si la mission a réussi
        mission_success = False
        
        # Pour les missions d'exploration (première mission), elle est toujours gagnée
        if self.hero and hasattr(self.hero, 'explore_mission') and self.hero.explore_mission:
            # La mission d'exploration est truquée pour toujours réussir
            mission_success = True
        elif self.hero and hasattr(self.hero, 'battle_mission') and self.hero.battle_mission:
            # La mission de bataille est réussie si elle est marquée comme complétée avec succès
            mission_success = (self.hero.battle_mission.mission_completed and 
                             self.hero.battle_mission.success)
        else:
            # Fallback pour d'autres types de missions
            mission_success = self.hero.is_mission_complete() if self.hero else False
        
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
            self.gold += self.bet_result['winnings']
        elif self.bet_type == "echec" and not mission_success:
            # Pari gagné sur l'échec de la MISSION DE BATAILLE
            self.bet_result['won'] = True
            self.bet_result['winnings'] = self.bet_amount * 2
            self.gold += self.bet_result['winnings']
        else:
            # Pari perdu
            self.bet_result['won'] = False
            self.bet_result['winnings'] = -self.bet_amount
        
        # Créer le message de résultat
        if self.bet_result['won']:
            self.bet_result['message'] = f"🎉 PARI GAGNÉ ! 🎉\nVous avez parié {self.bet_amount} crédits sur {self.bet_type}\nMission {'réussie' if mission_success else 'échouée'}\nGains: +{self.bet_result['winnings']} crédits"
        else:
            self.bet_result['message'] = f"❌ PARI PERDU ❌\nVous avez parié {self.bet_amount} crédits sur {self.bet_type}\nMission {'réussie' if mission_success else 'échouée'}\nPerte: {self.bet_result['winnings']} crédits"
        
        return self.bet_result
    
    def close_betting_interface(self):
        self.betting_active = False
    
    def get_betting_timer_remaining(self):
        """Retourne le temps restant avant le pari forcé en secondes"""
        if self.betting_timer is None:
            return 0
        remaining = self.betting_timer - time.time()
        result = max(0, int(remaining))
        return result
    
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
