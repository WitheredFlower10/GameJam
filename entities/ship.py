import arcade
import os
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
        
        # Charger les textures d'icône pour les points d'intérêt
        self.point_icon_tex = None        # icône par défaut (pixil-frame-0.png)
        self.point_icon_hero_tex = None   # icône spéciale héros (hero-quest.png)
        self.point_icon_terminal_tex = None  # icône spéciale terminal (terminal.png)
        self._load_point_icons()
        
        # SpriteList et mapping pour les icônes de points
        self.point_icon_sprites = arcade.SpriteList()
        self.point_name_to_sprite = {}
        
        self.create_interaction_points()
        # Construire les sprites pour chaque point
        self._build_point_icon_sprites()
    
    def _load_point_icons(self):
        base_candidates = [
            'assets',
            os.path.join(os.path.dirname(__file__), '..', 'assets'),
        ]
        base_candidates = [os.path.normpath(p) for p in base_candidates]
        
        def _find_asset(file_names):
            # file_names: list of acceptable filename variants
            for base in base_candidates:
                if not os.path.isdir(base):
                    continue
                # Recherche directe à la racine
                for name in file_names:
                    candidate = os.path.join(base, name)
                    if os.path.exists(candidate):
                        return candidate
                # Recherche récursive
                for root, _dirs, files in os.walk(base):
                    for fname in files:
                        lower = fname.lower()
                        if lower in [n.lower() for n in file_names]:
                            return os.path.join(root, fname)
            return None
        
        # Charger pixil-frame-0 (icône par défaut des points)
        self.point_icon_tex = None
        pixil_path = _find_asset(['pixil-frame-0.png', 'pixil_frame_0.png'])
        if pixil_path:
            try:
                self.point_icon_tex = arcade.load_texture(pixil_path)
                print(f"Point icon loaded: {pixil_path}")
            except Exception:
                self.point_icon_tex = None
        else:
            print("[INFO] Icone par défaut des points (pixil-frame-0.png) introuvable. Cercles jaunes utilisés.")
        
        # Charger hero-quest (icône spéciale pour Parler au Héros)
        self.point_icon_hero_tex = None
        hero_icon_path = _find_asset(['hero-quest.png', 'hero_quest.png'])
        if hero_icon_path:
            try:
                self.point_icon_hero_tex = arcade.load_texture(hero_icon_path)
                print(f"Hero icon loaded: {hero_icon_path}")
            except Exception:
                self.point_icon_hero_tex = None
        else:
            print("[INFO] Icone 'hero-quest.png' introuvable. Cercle jaune utilisé pour le héros.")
        
        # Charger terminal.png (icône spéciale pour le Terminal)
        self.point_icon_terminal_tex = None
        term_icon_path = _find_asset(['terminal.png'])
        if term_icon_path:
            try:
                self.point_icon_terminal_tex = arcade.load_texture(term_icon_path)
                print(f"Terminal icon loaded: {term_icon_path}")
            except Exception:
                self.point_icon_terminal_tex = None
        else:
            print("[INFO] Icone 'terminal.png' introuvable. Cercle jaune utilisé pour le terminal.")
    
    def create_interaction_points(self):
        
        # Point d'interaction du HÉROS (comme les autres)
        head_offset = (getattr(self.hero_npc, 'height', 40) / 2) + 30
        self.interaction_points.append({
            'x': self.hero_npc.center_x,
            'y': self.hero_npc.center_y + head_offset,
            'type': 'hero_missions',
            'name': 'DONNER LA QUETE',
            'description': 'Donner des missions au héros',
            'range_x': 350.0
        })
        
        # repair 1 (ennemis)
        self.interaction_points.append({
            'x': 1920,
            'y': 330,
            'type': 'repair_screen_enemies',
            'name': 'REPARATION / ENNEMIS',
            'description': 'Réparer l\'écran de surveillance pour les ennemis'
        })

        # repair 2 (vie)
        self.interaction_points.append({
            'x': 820,
            'y': 360,
            'type': 'repair_screen_health',
            'name': 'REPARATION / VIE',
            'description': 'Réparer l\'écran de surveillance pour la vie'
        })
        
        # Station de paris
        self.interaction_points.append({
            'x':2570,
            'y': 330,
            'type': 'betting_station',
            'name': 'PARIER',
            'description': 'Parier sur la réussite du héros'
        })
        

        # Activer le Terminal (inchangé)
        self.interaction_points.append({
            'x': 2220,
            'y': 320,
            'type': 'terminal',
            'name': 'TERMINAL',
            'description': 'Accéder au terminal de communication'
        })
    
    def _build_point_icon_sprites(self):
        """Crée/rafraîchit les sprites d'icônes pour les points d'interaction."""
        self.point_icon_sprites = arcade.SpriteList()
        self.point_name_to_sprite = {}
        for point in self.interaction_points:
            # Choisir texture
            tex = self.point_icon_tex  # par défaut: pixil-frame-0.png
            if point.get('type') == 'hero_missions' and self.point_icon_hero_tex is not None:
                tex = self.point_icon_hero_tex
            elif point.get('type') == 'betting_station' and self.point_icon_hero_tex is not None:
                tex = self.point_icon_hero_tex
            elif point.get('type') == 'terminal' and self.point_icon_terminal_tex is not None:
                tex = self.point_icon_terminal_tex
            sprite = None
            if tex is not None:
                try:
                    sprite = arcade.Sprite()
                    sprite.texture = tex
                    sprite.center_x = float(point.get('x', 0))
                    sprite.center_y = float(point.get('y', 0))
                    sprite.scale = 0.5
                    self.point_icon_sprites.append(sprite)
                    self.point_name_to_sprite[point.get('name','')] = sprite
                except Exception:
                    sprite = None
            if sprite is None:
                dummy = arcade.Sprite()
                dummy.alpha = 0
                self.point_icon_sprites.append(dummy)
                self.point_name_to_sprite[point.get('name','')] = dummy
    
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
                'name': 'DONNER LA QUETE',
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
            if mission_system and hasattr(mission_system, 'is_point_completed'):
                try:
                    if mission_system.is_point_completed(point.get('name','')):
                        continue
                except Exception:
                    pass
            # Cacher le point du héros si mission en cours ou héros invisible
            if point.get('type') == 'hero_missions':
                is_traveling = bool(getattr(mission_system, 'travel_end_time', None)) if mission_system else False
                if (mission_system and (mission_system.current_mission or is_traveling)) or (not self.hero_npc or not self.hero_npc.visible):
                    continue
            # Cacher l'icône de pari si aucune mission n'est en cours
            if point.get('type') == 'betting_station':
                if not (mission_system and mission_system.current_mission):
                    continue
            # Cacher la réparation ENNEMIS tant que la première mission n'est pas réussie
            if point.get('type') == 'repair_screen_enemies':
                if not (mission_system and getattr(mission_system, 'missions_completed_success_count', 0) >= 1):
                    continue
            # Cacher la réparation VIE tant qu'aucune mission n'est lancée
            if point.get('type') == 'repair_screen_health':
                if not (mission_system and getattr(mission_system, 'missions_launched_count', 0) >= 1):
                    continue
            points_to_draw.append(point)

        import math

        # Dessiner points/flèches via sprites (icônes)
        edge_margin_px = 80
        # Espacer davantage verticalement les flèches sur les côtés gauche/droit
        arrow_spacing_px = 60
        arrow_counts = {"left": 0, "right": 0}

        # Mettre à jour position/visibilité de chaque sprite avant dessin
        # Masquer toutes les icônes par défaut, on n'activera que celles à afficher
        try:
            for _spr in self.point_icon_sprites:
                _spr.visible = False
        except Exception:
            pass

        for point in points_to_draw:
            # Position dynamique pour le héros
            if point.get('type') == 'hero_missions' and self.hero_npc:
                px = self.hero_npc.center_x
                py = self.hero_npc.center_y + (getattr(self.hero_npc, 'height', 40) / 2) + 30
            else:
                px, py = point['x'], point['y']

            # Test visibilité monde (pour tous les points)
            on_screen = (left <= px <= right) and (bottom <= py <= top)
            spr = self.point_name_to_sprite.get(point.get('name',''))
            if spr is not None:
                spr.center_x = px
                spr.center_y = py
                spr.visible = on_screen
            # Contours jaunes retirés

            if not on_screen:
                # Flèche au bord
                sx = (px - cam_x) * zoom + (screen_width / 2)
                sy = (py - cam_y) * zoom + (screen_height / 2)
                cx = screen_width / 2
                cy = screen_height / 2
                dx = sx - cx
                dy = sy - cy
                if abs(dx) < 1e-6 and abs(dy) < 1e-6:
                    dx = 0.0
                    dy = 1.0
                left_px = edge_margin_px
                right_px = screen_width - edge_margin_px
                bottom_px = edge_margin_px
                top_px = screen_height - edge_margin_px
                inf = float('inf')
                tx = inf
                ty = inf
                if abs(dx) > 1e-6:
                    tx = (right_px - cx) / dx if dx > 0 else (left_px - cx) / dx
                if abs(dy) > 1e-6:
                    ty = (top_px - cy) / dy if dy > 0 else (bottom_px - cy) / dy
                s = min(t for t in (tx, ty) if t > 0)
                edge_sx = cx + dx * s
                edge_sy = cy + dy * s

                # Déterminer le côté d'intersection et appliquer un décalage vertical
                side = None
                if tx <= ty:
                    side = 'right' if dx > 0 else 'left'
                else:
                    side = 'top' if dy > 0 else 'bottom'
                if side in ('left', 'right'):
                    idx = arrow_counts.get(side, 0)
                    arrow_counts[side] = idx + 1
                    # Décaler edge_sy en pixels écran et le re-clamper
                    edge_sy = max(bottom_px, min(top_px, edge_sy + idx * arrow_spacing_px))
                ex = cam_x + (edge_sx - screen_width / 2) / zoom
                ey = cam_y + (edge_sy - screen_height / 2) / zoom
                angle = math.atan2(dy, dx)
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

        # Dessiner toutes les icônes visibles (sprites)
        self.point_icon_sprites.draw()
    
    def draw_hero_npc(self, mission_system=None):
        """Dessine le sprite du héros NPC"""
        # Ne pas dessiner si une mission est en cours, si le héros est en trajet, ou si le héros est invisible
        if mission_system is not None and (getattr(mission_system, 'current_mission', None) or getattr(mission_system, 'travel_end_time', None)):
            return
        if self.hero_npc_list and self.hero_npc and getattr(self.hero_npc, 'visible', True):
            self.hero_npc_list.draw()
    
    def get_interaction_points(self):
        # Retourner la liste statique (héros inclus)
        return list(self.interaction_points)
