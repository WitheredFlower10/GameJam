import arcade
from utils.constants import SHIP_COLOR, SCREEN_WIDTH, SCREEN_HEIGHT
from entities.hero_npc import HeroNPC


class Ship(arcade.SpriteList):
    
    def __init__(self):
        super().__init__()
        
        self.interaction_points = []
        
        # Créer le héros NPC au même niveau que l'agent
        self.hero_npc = HeroNPC(SCREEN_WIDTH // 6, 320)  # Même hauteur que l'agent (ground_y = 320)
        
        # Ajouter le héros NPC à une sprite list pour le dessiner facilement
        self.hero_npc_list = arcade.SpriteList()
        self.hero_npc_list.append(self.hero_npc)
        
        self.create_interaction_points()
    
    def create_interaction_points(self):
        # Remplacé par le HeroNPC - plus besoin du "Bureau des Missions"
        
        # Point d'interaction du HÉROS (comme les autres)
        head_offset = (getattr(self.hero_npc, 'height', 40) / 2) + 30
        self.interaction_points.append({
            'x': self.hero_npc.center_x,
            'y': self.hero_npc.center_y + head_offset,
            'type': 'hero_missions',
            'name': 'Parler au Héros',
            'description': 'Donner des missions au héros',
            'range_x': 350.0
        })
        
        # Station de surveillance
        self.interaction_points.append({
            'x': SCREEN_WIDTH // 2 + 100,
            'y': 200,
            'type': 'surveillance_upgrade',
            'name': 'Amélioration Surveillance',
            'description': 'Améliorer la qualité de surveillance'
        })
        
        # Station de paris
        self.interaction_points.append({
            'x': 5 * SCREEN_WIDTH // 6 + 100,
            'y': 180,
            'type': 'betting_station',
            'name': 'Station de Paris',
            'description': 'Parier sur la réussite du héros'
        })
        
        # Analyse de données
        self.interaction_points.append({
            'x': 5 * SCREEN_WIDTH // 6 + 100,
            'y': 120,
            'type': 'data_analysis',
            'name': 'Analyse de Données',
            'description': 'Analyser les données du héros'
        })

        # Activer le Terminal (inchangé)
        self.interaction_points.append({
            'x': 2200,
            'y': 250,
            'type': 'terminal',
            'name': 'Terminal',
            'description': 'Accéder au terminal de communication'
        })
    
    def update_hero_npc(self, delta_time):
        """Met à jour le héros NPC"""
        if self.hero_npc_list:
            self.hero_npc_list.update()
    
    def set_hero_on_mission(self, on_mission):
        """Contrôle la visibilité du héros selon s'il est en mission"""
        if self.hero_npc:
            self.hero_npc.set_on_mission(on_mission)
    
    def get_hero_interaction_point(self):
        """Retourne le point d'interaction du héros s'il est visible"""
        if self.hero_npc and self.hero_npc.visible:
            # Placer le point bien au-dessus de la tête: hauteur du sprite / 2 + marge
            head_offset = (getattr(self.hero_npc, 'height', 40) / 2) + 30
            return {
                'x': self.hero_npc.center_x,
                'y': self.hero_npc.center_y + head_offset,
                'type': 'hero_missions',
                'name': 'Parler au Héros',
                'description': 'Donner des missions au héros',
                # Portée X-only (comme les autres), mais plus large
                'range_x': 200.0
            }
        return None
    
    def draw_interaction_points(self, camera=None, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT, mission_system=None):
        # Utiliser la taille réelle de la fenêtre pour éviter les erreurs liées au fullscreen/zoom
        try:
            wnd = arcade.get_window()
            if wnd is not None and hasattr(wnd, 'width') and hasattr(wnd, 'height'):
                screen_width = wnd.width
                screen_height = wnd.height
        except Exception:
            pass

        # Obtenir paramètres caméra
        if camera is not None:
            cam_x, cam_y = camera.position
            zoom = getattr(camera, 'zoom', 1.0)
        else:
            cam_x, cam_y = screen_width // 2, screen_height // 2
            zoom = 1.0

        # Limites de l'écran (en coordonnées monde)
        left = cam_x - (screen_width / 2) / zoom
        right = cam_x + (screen_width / 2) / zoom
        bottom = cam_y - (screen_height / 2) / zoom
        top = cam_y + (screen_height / 2) / zoom

        # Préparer largeurs pour les portées X-only
        agent_sprite = getattr(mission_system, 'agent_ref', None) if mission_system is not None else None
        try:
            agent_w = float(getattr(agent_sprite, 'width', 50.0)) if agent_sprite is not None else 50.0
        except Exception:
            agent_w = 50.0
        try:
            hero_w = float(getattr(self.hero_npc, 'width', 40.0)) if self.hero_npc is not None else 40.0
        except Exception:
            hero_w = 40.0

        # Construire la liste complète des points (incluant le héros)
        base_points = self.get_interaction_points()
        points_to_draw = []
        for point in base_points:
            # Filtrer "Amélioration Surveillance" si déjà complété
            if mission_system and point['name'] == "Amélioration Surveillance" and mission_system.wire_puzzle_completed:
                continue
            # Cacher le point du héros si mission en cours ou héros invisible
            if point.get('type') == 'hero_missions':
                if (mission_system and mission_system.current_mission) or (not self.hero_npc or not self.hero_npc.visible):
                    continue
            points_to_draw.append(point)

        import math

        # Visualiser la portée X-only pour chaque point
        for point in points_to_draw:
            # Position dynamique pour le héros
            if point.get('type') == 'hero_missions' and self.hero_npc:
                px = self.hero_npc.center_x
                py = self.hero_npc.center_y + (getattr(self.hero_npc, 'height', 40) / 2) + 30
            else:
                px, py = point['x'], point['y']
            # Lire la portée X depuis le point (comme pour tous)
            try:
                activation_range_x = float(point.get('range_x', 50.0))
            except Exception:
                activation_range_x = 50.0
            # Lignes verticales aux bornes de la portée X
            arcade.draw_line(px - activation_range_x, bottom, px - activation_range_x, top, arcade.color.RED, 2)
            arcade.draw_line(px + activation_range_x, bottom, px + activation_range_x, top, arcade.color.RED, 2)

        # Dessiner points/flèches
        # Marge côté écran pour les flèches (en pixels)
        edge_margin_px = 50
        # Rayon à l'intérieur de l'écran en pixels
        radius_px = min(screen_width, screen_height) / 2 - edge_margin_px

        for point in points_to_draw:
            # Position dynamique pour le héros
            if point.get('type') == 'hero_missions' and self.hero_npc:
                px = self.hero_npc.center_x
                py = self.hero_npc.center_y + (getattr(self.hero_npc, 'height', 40) / 2) + 30
            else:
                px, py = point['x'], point['y']

            # Test de visibilité en coordonnées monde
            on_screen = (left <= px <= right) and (bottom <= py <= top)

            if on_screen:
                # Dessiner le point en coordonnées monde
                arcade.draw_circle_filled(px, py, 15, arcade.color.ORANGE)
                arcade.draw_circle_outline(px, py, 15, arcade.color.WHITE, 2)
            else:
                # Calculer la position écran du point (sx, sy)
                sx = (px - cam_x) * zoom + (screen_width / 2)
                sy = (py - cam_y) * zoom + (screen_height / 2)

                # Centre de l'écran
                cx = screen_width / 2
                cy = screen_height / 2

                # Vecteur direction centre -> point
                dx = sx - cx
                dy = sy - cy

                # Si le vecteur est nul, éviter division par zéro (placer au haut-centre)
                if abs(dx) < 1e-6 and abs(dy) < 1e-6:
                    dx = 0.0
                    dy = 1.0

                # Marges près des bords
                left_px = edge_margin_px
                right_px = screen_width - edge_margin_px
                bottom_px = edge_margin_px
                top_px = screen_height - edge_margin_px

                inf = float('inf')
                # Facteurs d'intersection avec les côtés du rectangle (écran)
                tx = inf
                ty = inf
                if abs(dx) > 1e-6:
                    tx = (right_px - cx) / dx if dx > 0 else (left_px - cx) / dx
                if abs(dy) > 1e-6:
                    ty = (top_px - cy) / dy if dy > 0 else (bottom_px - cy) / dy

                s = min(t for t in (tx, ty) if t > 0)

                edge_sx = cx + dx * s
                edge_sy = cy + dy * s

                # Convertir en coordonnées monde pour dessiner avec la caméra monde active
                ex = cam_x + (edge_sx - screen_width / 2) / zoom
                ey = cam_y + (edge_sy - screen_height / 2) / zoom

                # Angle pour la flèche (utiliser vecteur direction)
                angle = math.atan2(dy, dx)

                # Taille de la flèche et du texte en unités monde pour rester ~constants visuellement
                tri_len = 15.0 / max(zoom, 0.0001)
                x1, y1 = ex, ey
                x2 = ex - tri_len * math.cos(angle - 0.3)
                y2 = ey - tri_len * math.sin(angle - 0.3)
                x3 = ex - tri_len * math.cos(angle + 0.3)
                y3 = ey - tri_len * math.sin(angle + 0.3)

                arcade.draw_triangle_filled(x1, y1, x2, y2, x3, y3, arcade.color.YELLOW)
                arcade.draw_text(
                    point['name'],
                    ex, ey + (20.0 / max(zoom, 0.0001)),
                    arcade.color.WHITE, 12 / max(zoom, 0.0001),
                    anchor_x="center"
                )
    
    def draw_hero_npc(self, mission_system=None):
        """Dessine le sprite du héros NPC"""
        # Ne pas dessiner si une mission est en cours ou si le héros est invisible
        if mission_system is not None and getattr(mission_system, 'current_mission', None):
            return
        if self.hero_npc_list and self.hero_npc and getattr(self.hero_npc, 'visible', True):
            self.hero_npc_list.draw()
    
    def get_interaction_points(self):
        # Retourner la liste statique (héros inclus)
        return list(self.interaction_points)
