import arcade
import os
from utils.constants import AGENT_COLOR, AGENT_SCALE, AGENT_MOVEMENT_SPEED, AGENT_STATE_IDLE, AGENT_STATE_MOVING, SCREEN_WIDTH


class Agent(arcade.Sprite):
    
    def __init__(self):
        super().__init__()
        
        # Apparence / Textures
        self.scale = AGENT_SCALE
        self.walk_textures = []
        self.walk_textures_left = []
        self.walk_textures_right = []
        self.breathing_textures = []
        self.breathing_textures_left = []
        self.breathing_textures_right = []
        self.animation_index = 0
        self.animation_timer = 0.0
        self.animation_speed = 0.3  # secondes par frame (marche)
        self.animation_speed_idle = 0.6  # secondes par frame (idle / respiration)
        self.idle_time = 0.0
        self.is_breathing = False
        self.facing = 'right'
        self.was_moving = False
        
        # Charger animations/textures standards
        self.load_textures()
        # Fallback si pas de textures disponibles
        if (not self.walk_textures and not self.walk_textures_left and not self.walk_textures_right
            and not self.breathing_textures):
            self.texture = arcade.make_soft_square_texture(32, AGENT_COLOR, outer_alpha=255)
        else:
            first_tex = (
                (self.walk_textures_right[0] if self.walk_textures_right else None)
                or (self.walk_textures_left[0] if self.walk_textures_left else None)
                or (self.walk_textures[0] if self.walk_textures else None)
                or (
                    (self.breathing_textures_right[0] if self.breathing_textures_right else None)
                    or (self.breathing_textures_left[0] if self.breathing_textures_left else None)
                    or (self.breathing_textures[0] if self.breathing_textures else None)
                )
            )
            self.texture = first_tex
        
        # Mouvement
        self.change_x = 0
        self.change_y = 0
        self.speed = AGENT_MOVEMENT_SPEED
        
        # État
        self.state = AGENT_STATE_IDLE
        
        # Systèmes liés
        self.mission_system = None
        self.current_interaction = None
        self.collision_list = None  # Liste des sprites avec lesquels on peut collider
        
        # Contrôles
        self.left_pressed = False
        self.right_pressed = False
        self.interact_pressed = False

        # Bornes du monde (peuvent être mises à jour par la scène)
        self.world_left = 0
        self.world_right = SCREEN_WIDTH
        # Hauteur du sol où le personnage se tient
        self.ground_y = 320  # Ajusté pour le nouveau background
    
    def set_mission_system(self, mission_system):
        self.mission_system = mission_system
        try:
            # Donner une référence de l'agent au mission system (pour les distances)
            setattr(self.mission_system, 'agent_ref', self)
        except Exception:
            pass
    
    def set_collision_list(self, collision_list):
        self.collision_list = collision_list
    
    def _can_move_to(self, new_x):
        """Vérifie si l'agent peut se déplacer à la position new_x sans collision"""
        if not self.collision_list:
            return True
            
        # Sauvegarder la position actuelle
        old_x = self.center_x
        
        # Tester la nouvelle position
        self.center_x = new_x
        
        # Vérifier les collisions
        collisions = arcade.check_for_collision_with_list(self, self.collision_list)
        
        # Restaurer la position
        self.center_x = old_x
        
        # Pas de collision = peut se déplacer
        return len(collisions) == 0
    
    def update(self, delta_time):
        super().update()
        
        # Mettre à jour le mouvement
        self.update_movement()
        # Mettre à jour l'animation
        self.update_animation(delta_time)
        
        # Vérifier les interactions
        self.check_interactions()
    
    def update_movement(self):
        # Calculer la vitesse horizontale
        self.change_x = 0
        
        if self.left_pressed and not self.right_pressed:
            new_x = self.center_x - self.speed
            if self._can_move_to(new_x):
                self.change_x = -self.speed
                self.state = AGENT_STATE_MOVING
                self.facing = 'left'
            else:
                self.change_x = 0
                self.state = AGENT_STATE_IDLE
        elif self.right_pressed and not self.left_pressed:
            new_x = self.center_x + self.speed
            if self._can_move_to(new_x):
                self.change_x = self.speed
                self.state = AGENT_STATE_MOVING
                self.facing = 'right'
            else:
                self.change_x = 0
                self.state = AGENT_STATE_IDLE
        else:
            self.state = AGENT_STATE_IDLE
        
        # Verrouiller sur l'axe vertical au niveau du sol
        self.center_y = self.ground_y

        # Empêcher de sortir des limites du monde (mises par la scène)
        min_x = self.world_left + 50
        max_x = self.world_right - 50
        if self.center_x < min_x:
            self.center_x = min_x
            self.change_x = 0
        elif self.center_x > max_x:
            self.center_x = max_x
            self.change_x = 0

    def update_animation(self, delta_time: float):
        is_moving = (self.state == AGENT_STATE_MOVING and self.change_x != 0)
        # Transition: si on vient d'arrêter de bouger, afficher une frame idle orientée selon facing
        if (not is_moving) and self.was_moving:
            self.animation_index = 0
            self.animation_timer = 0.0
            chosen_idle = None
            if self.facing == 'left':
                if self.breathing_textures_left:
                    chosen_idle = self.breathing_textures_left[0]
                elif self.walk_textures_left:
                    chosen_idle = self.walk_textures_left[0]
            elif self.facing == 'right':
                if self.breathing_textures_right:
                    chosen_idle = self.breathing_textures_right[0]
                elif self.walk_textures_right:
                    chosen_idle = self.walk_textures_right[0]
            if not chosen_idle:
                # Fallback neutre
                chosen_idle = (
                    (self.breathing_textures[0] if self.breathing_textures else None)
                    or (self.walk_textures[0] if self.walk_textures else None)
                    or self.texture
                )
            self.texture = chosen_idle
        if is_moving:
            self.idle_time = 0.0
            self.is_breathing = False
            # Choisir frames selon l'orientation si disponible, sinon fallback à ancien dossier plat
            if self.facing == 'left' and self.walk_textures_left:
                frames = self.walk_textures_left
            elif self.facing == 'right' and self.walk_textures_right:
                frames = self.walk_textures_right
            else:
                frames = self.walk_textures
        else:
            self.idle_time += delta_time
            if self.idle_time >= 2.0 and self.breathing_textures:
                self.is_breathing = True
            if self.is_breathing:
                if self.facing == 'left' and self.breathing_textures_left:
                    frames = self.breathing_textures_left
                elif self.facing == 'right' and self.breathing_textures_right:
                    frames = self.breathing_textures_right
                else:
                    frames = self.breathing_textures
            else:
                frames = None

        if frames:
            # Choisir la vitesse d'animation selon l'état
            current_speed = self.animation_speed if is_moving else self.animation_speed_idle
            self.animation_timer += delta_time
            if self.animation_timer >= current_speed:
                self.animation_timer = 0.0
                self.animation_index = (self.animation_index + 1) % len(frames)
                self.texture = frames[self.animation_index]
        # mémoriser l'état pour la prochaine frame
        self.was_moving = is_moving

    def load_textures(self):
        # Cherche et charge les textures dans assets/walk et assets/breathing
        base_candidates = [
            'assets',
            os.path.join(os.path.dirname(__file__), '..', 'assets'),
        ]
        base_candidates = [os.path.normpath(p) for p in base_candidates]

        def load_folder(frames_dir):
            textures = []
            try:
                files = []
                for fname in os.listdir(frames_dir):
                    lower = fname.lower()
                    if lower.endswith('.png') or lower.endswith('.jpg') or lower.endswith('.jpeg'):
                        files.append(os.path.join(frames_dir, fname))
                # Trier naturellement par nom (1,2,3,4...)
                files.sort(key=lambda x: x)
                for f in files:
                    try:
                        textures.append(arcade.load_texture(f))
                    except Exception:
                        continue
            except Exception:
                pass
            return textures

        # Walk: supporte assets/walk/left et assets/walk/right, sinon fallback assets/walk
        for base in base_candidates:
            walk_dir = os.path.join(base, 'walk')
            if os.path.isdir(walk_dir):
                left_dir = os.path.join(walk_dir, 'left')
                right_dir = os.path.join(walk_dir, 'right')
                has_subdirs = os.path.isdir(left_dir) or os.path.isdir(right_dir)
                if has_subdirs:
                    if os.path.isdir(left_dir):
                        self.walk_textures_left = load_folder(left_dir)
                    if os.path.isdir(right_dir):
                        self.walk_textures_right = load_folder(right_dir)
                    # Si aucun des sous-dossiers n'a chargé, tenter fallback plat
                    if not self.walk_textures_left and not self.walk_textures_right:
                        self.walk_textures = load_folder(walk_dir)
                else:
                    self.walk_textures = load_folder(walk_dir)
                if self.walk_textures or self.walk_textures_left or self.walk_textures_right:
                    break

        # Breathing: support left/right variants in same folder by filename
        for base in base_candidates:
            br_dir = os.path.join(base, 'breathing')
            if os.path.isdir(br_dir):
                try:
                    files = []
                    for fname in os.listdir(br_dir):
                        lower = fname.lower()
                        if lower.endswith('.png') or lower.endswith('.jpg') or lower.endswith('.jpeg'):
                            files.append((fname, lower))
                    files.sort(key=lambda x: x[0])
                    neutral_files = []
                    left_files = []
                    right_files = []
                    for orig, lower in files:
                        full = os.path.join(br_dir, orig)
                        if 'left' in lower and 'right' not in lower:
                            left_files.append(full)
                        elif 'right' in lower and 'left' not in lower:
                            right_files.append(full)
                        else:
                            neutral_files.append(full)
                    # Load
                    for f in left_files:
                        try:
                            self.breathing_textures_left.append(arcade.load_texture(f))
                        except Exception:
                            continue
                    for f in right_files:
                        try:
                            self.breathing_textures_right.append(arcade.load_texture(f))
                        except Exception:
                            continue
                    for f in neutral_files:
                        try:
                            self.breathing_textures.append(arcade.load_texture(f))
                        except Exception:
                            continue
                    # Fallback mapping: if one side missing, use neutral if available
                    if not self.breathing_textures_right and self.breathing_textures:
                        self.breathing_textures_right = list(self.breathing_textures)
                    if not self.breathing_textures_left and self.breathing_textures:
                        self.breathing_textures_left = list(self.breathing_textures)
                except Exception:
                    pass
                # Consider textures loaded if any variant is present
                if (self.breathing_textures_left or self.breathing_textures_right or self.breathing_textures):
                    break
    
    def check_interactions(self):
        # Vérifier s'il y a des points d'interaction à proximité
        if self.mission_system:
            # Récupérer les interactions X-only unifiées
            nearby_interactions = self.mission_system.get_nearby_interactions(self.center_x)
            
            if nearby_interactions and self.interact_pressed:
                # Interagir avec le point le plus proche (X uniquement)
                def _dist_x(p):
                    try:
                        return abs(float(p.get('x', 0)) - float(self.center_x))
                    except Exception:
                        return 1e9
                closest = min(nearby_interactions, key=_dist_x)
                self.interact_with_point(closest)
    
    def interact_with_point(self, interaction_point):
        # Utiliser le système de missions pour gérer l'interaction
        if self.mission_system:
            # Essayer d'obtenir le ship depuis le mission_system si disponible
            ship = getattr(self.mission_system, 'ship', None)
            result = self.mission_system.interact_with_point(interaction_point['name'], ship)
            print(f"Interaction avec {interaction_point['name']}: {result}")
            self.interact_pressed = False
    
    def on_key_press(self, key, modifiers):
        if key == arcade.key.LEFT or key == arcade.key.Q:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True
        elif key == arcade.key.SPACE or key == arcade.key.F:
            self.interact_pressed = True
    
    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT or key == arcade.key.Q:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False
        elif key == arcade.key.SPACE or key == arcade.key.F:
            self.interact_pressed = False
    
