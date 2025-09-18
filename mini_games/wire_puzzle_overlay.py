import arcade
import time
import random

# Configuration du puzzle
GRID_SIZE = 3
WIRE_THICKNESS = 3

class WireTile:
    """Une tuile de circuit simple avec des connexions fixes"""
    
    def __init__(self, x, y, tile_type="straight"):
        self.x = x
        self.y = y
        self.tile_type = tile_type  # "straight", "corner", "half"
        self.rotation = 0  # 0, 1, 2, 3 (0°, 90°, 180°, 270°)
        self.is_powered = False
        self.is_correct = False
        self.correct_rotation = 0  # Rotation correcte pour résoudre le puzzle
        self.is_source = False  # Marque si c'est la source du courant
        self.is_target = False  # Marque si c'est la cible du courant
        
        # Définir les connexions de base pour chaque type
        self._base_connections = self._get_base_connections()
    
    def _get_base_connections(self):
        """Retourne les connexions de base (avant rotation) pour chaque type"""
        if self.tile_type == "straight":
            return [(0, 1), (0, -1)]  # Vertical
        elif self.tile_type == "corner":
            return [(0, 1), (1, 0)]   # Haut et droite
        elif self.tile_type == "half":
            return [(1, 0)]           # Une seule connexion vers la droite
        else:
            return []                 # Pas de connexions
    
    def get_connections(self):
        """Retourne les connexions après rotation"""
        connections = []
        for dx, dy in self._base_connections:
            # Appliquer la rotation
            for _ in range(self.rotation):
                dx, dy = -dy, dx  # Rotation 90° sens horaire
            connections.append((dx, dy))
        return connections
    
    def rotate(self):
        """Faire tourner la tuile de 90° sens horaire"""
        self.rotation = (self.rotation + 1) % 4
    
    def can_connect_to(self, other_tile, direction):
        """Vérifie si cette tuile peut se connecter à une autre dans une direction"""
        my_connections = self.get_connections()
        other_connections = other_tile.get_connections()
        
        # Vérifier si j'ai une connexion dans cette direction
        if direction not in my_connections:
            return False
        
        # Vérifier si l'autre tuile a une connexion vers moi
        reverse_direction = (-direction[0], -direction[1])
        return reverse_direction in other_connections


class WirePuzzleOverlay:
    """Version overlay du puzzle de fils pour l'intégration dans le jeu principal"""
    
    def __init__(self, window, on_exit_callback=None, mission_system=None):
        self.window = window
        self.on_exit_callback = on_exit_callback
        self.mission_system = mission_system
        
        # Dimensions de l'overlay (comme le terminal)
        self.width = 450
        self.height = 300
        
        # Navigation
        self.selected_x = 1
        self.selected_y = 1
        self._nav_cooldown = 0.15
        self._last_nav_time = 0
        
        # Grille et puzzle
        self.grid = []
        self.is_completed = False
        
        # Couleurs
        self.wire_color = arcade.color.CYAN
        self.powered_color = arcade.color.YELLOW
        self.selected_color = arcade.color.WHITE
        
        self._generate_puzzle()
    
    def _generate_puzzle(self):
        """Génère un puzzle avec des fils sur toutes les cases"""
        # Source dans le coin haut-gauche, target dans le coin bas-droite
        source_x, source_y = 0, 2  # Coin haut-gauche
        target_x, target_y = 2, 0  # Coin bas-droite
        
        # Initialiser la grille avec des types prédéfinis
        tile_types = [
            ["corner", "corner", "half"],    # Ligne du haut (source = half)
            ["straight", "corner", "corner"], # Ligne du milieu
            ["half", "straight", "corner"]    # Ligne du bas (target = half)
        ]
        
        # Rotations correctes pour créer un chemin valide avec la nouvelle disposition
        correct_rotations = [
            [2, 3, 1],  # Haut: half bas, corner horizontal, corner gauche-haut  
            [0, 2, 0],  # Milieu: straight vertical, corner bas-gauche, corner vertical
            [3, 1, 0]   # Bas: corner droite-bas, straight horizontal, half gauche
        ]
        
        self.grid = []
        for y in range(GRID_SIZE):
            row = []
            for x in range(GRID_SIZE):
                tile_type = tile_types[y][x]
                tile = WireTile(x, y, tile_type)
                
                # Définir la rotation correcte
                tile.correct_rotation = correct_rotations[y][x]
                
                # Mélanger la rotation initiale
                tile.rotation = random.randint(0, 3)
                
                row.append(tile)
            self.grid.append(row)
        
        # Marquer source et target (mais garder leurs types de base)
        self.grid[source_y][source_x].is_source = True
        self.grid[target_y][target_x].is_target = True
        
        self._update_power_flow()
        
        # Afficher l'état initial
        print("=== PUZZLE WIRE - ÉTAT INITIAL ===")
        self._print_rotation_table()
    
    def _update_power_flow(self):
        """Met à jour quelles tuiles sont alimentées"""
        # Reset
        for row in self.grid:
            for tile in row:
                tile.is_powered = False
        
        # Trouver la source (coin haut-gauche)
        source_tile = None
        for row in self.grid:
            for tile in row:
                if tile.is_source:
                    source_tile = tile
                    tile.is_powered = True
                    break
        
        if not source_tile:
            return
        
        # Propagation du courant
        visited = set()
        stack = [(source_tile.x, source_tile.y)]
        
        while stack:
            x, y = stack.pop()
            if (x, y) in visited:
                continue
            visited.add((x, y))
            
            current_tile = self.grid[y][x]
            current_tile.is_powered = True
            
            # Vérifier les connexions
            for dx, dy in current_tile.get_connections():
                nx, ny = x + dx, y + dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                    neighbor = self.grid[ny][nx]
                    if current_tile.can_connect_to(neighbor, (dx, dy)):
                        if (nx, ny) not in visited:
                            stack.append((nx, ny))
        
        # Vérifier si le puzzle est résolu (target alimenté)
        target_tile = None
        for row in self.grid:
            for tile in row:
                if tile.is_target:
                    target_tile = tile
                    break
        
        if target_tile and target_tile.is_powered:
            self.is_completed = True
            print("🎉 PUZZLE REUSSI! 🎉")
            # Marquer le puzzle comme complété dans le mission_system
            if self.mission_system:
                self.mission_system.wire_puzzle_completed = True
            if self.on_exit_callback:
                # Fermer l'overlay après un court délai
                self.on_exit_callback()
    
    def on_draw(self):
        """Dessiner l'overlay"""
        # Position de l'overlay (centré horizontalement, légèrement en bas)
        overlay_x = (self.window.width - self.width) // 2
        overlay_y = (self.window.height - self.height) // 2 - 80
        
        # Fond de l'overlay
        arcade.draw_lrbt_rectangle_filled(
            overlay_x, overlay_x + self.width,
            overlay_y, overlay_y + self.height,
            (0, 0, 0, 230)
        )
        
        # Bordure
        arcade.draw_lrbt_rectangle_outline(
            overlay_x, overlay_x + self.width,
            overlay_y, overlay_y + self.height,
            (0, 255, 220), 3
        )
        
        # Titre
        arcade.draw_text("🔌 RÉPARATION DE CIRCUITS",
                        overlay_x + 20, overlay_y + self.height - 35,
                        (0, 255, 220), 16, bold=True)
        
        # Instructions
        arcade.draw_text("Flèches: Déplacer  •  Espace: Rotation  •  Échap: Quitter",
                        overlay_x + 20, overlay_y + 15,
                        (180, 180, 255), 11)
        
        # Status
        if self.is_completed:
            arcade.draw_text("CIRCUIT RÉPARÉ!",
                            overlay_x + self.width // 2, overlay_y + 50,
                            arcade.color.GREEN, 14, anchor_x="center")
        
        # Calculer la taille et position de la grille
        grid_margin = 40
        available_width = self.width - 2 * grid_margin
        available_height = self.height - 80  # Espace pour titre et instructions
        tile_size = min(available_width // GRID_SIZE, available_height // GRID_SIZE)
        
        grid_width = GRID_SIZE * tile_size
        grid_height = GRID_SIZE * tile_size
        grid_start_x = overlay_x + (self.width - grid_width) // 2
        grid_start_y = overlay_y + (self.height - grid_height) // 2 + 10
        
        # Dessiner la grille
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                tile = self.grid[y][x]
                
                # Position de la tuile
                tile_x = grid_start_x + x * tile_size
                tile_y = grid_start_y + y * tile_size
                center_x = tile_x + tile_size // 2
                center_y = tile_y + tile_size // 2
                
                # Couleur de fond
                is_selected = (x == self.selected_x and y == self.selected_y)
                bg_color = (60, 60, 90) if is_selected else (30, 30, 50)
                
                # Dessiner le fond de la tuile
                arcade.draw_lrbt_rectangle_filled(
                    tile_x + 2, tile_x + tile_size - 2,
                    tile_y + 2, tile_y + tile_size - 2,
                    bg_color
                )
                
                # Bordure
                border_color = self.selected_color if is_selected else (100, 100, 120)
                arcade.draw_lrbt_rectangle_outline(
                    tile_x + 2, tile_x + tile_size - 2,
                    tile_y + 2, tile_y + tile_size - 2,
                    border_color, 1
                )
                
                # Dessiner les connexions/fils
                self._draw_tile_wires(tile, center_x, center_y, tile_size)
                
                # Indicateur spécial pour source/target
                if tile.is_source:
                    arcade.draw_circle_filled(center_x, center_y, 6, arcade.color.GREEN)
                elif tile.is_target:
                    arcade.draw_circle_filled(center_x, center_y, 6, arcade.color.RED)
    
    def _draw_tile_wires(self, tile, center_x, center_y, tile_size):
        """Dessine les fils d'une tuile"""
        
        wire_color = self.powered_color if tile.is_powered else self.wire_color
        
        # Dessiner les connexions
        for dx, dy in tile.get_connections():
            end_x = center_x + dx * (tile_size // 2 - 8)
            end_y = center_y + dy * (tile_size // 2 - 8)
            
            arcade.draw_line(center_x, center_y, end_x, end_y, wire_color, WIRE_THICKNESS)
            arcade.draw_circle_filled(end_x, end_y, 2, wire_color)
        
        # Point central
        arcade.draw_circle_filled(center_x, center_y, 3, wire_color)
    
    def on_key_press(self, key, modifiers):
        """Gestion des touches"""
        # Debounce pour la navigation ET la rotation
        if key in (arcade.key.LEFT, arcade.key.RIGHT, arcade.key.UP, arcade.key.DOWN, arcade.key.SPACE):
            now = time.time()
            if (now - self._last_nav_time) < self._nav_cooldown:
                return
            self._last_nav_time = now
        
        # Navigation
        if key == arcade.key.LEFT and self.selected_x > 0:
            self.selected_x -= 1
        elif key == arcade.key.RIGHT and self.selected_x < GRID_SIZE - 1:
            self.selected_x += 1
        elif key == arcade.key.UP and self.selected_y < GRID_SIZE - 1:
            self.selected_y += 1
        elif key == arcade.key.DOWN and self.selected_y > 0:
            self.selected_y -= 1
        
        # Rotation
        elif key == arcade.key.SPACE:
            selected_tile = self.grid[self.selected_y][self.selected_x]
            selected_tile.rotate()
            self._update_power_flow()
            self._print_rotation_table()
        
        # Quitter
        elif key == arcade.key.ESCAPE:
            if self.on_exit_callback:
                self.on_exit_callback()
    
    def on_update(self, delta_time):
        """Mise à jour de l'overlay"""
        pass
    
    def _print_rotation_table(self):
        """Affiche le tableau des rotations actuelles dans la console"""
        print("\n=== TABLEAU DES ROTATIONS ===")
        for y in range(GRID_SIZE):
            row_str = ""
            for x in range(GRID_SIZE):
                tile = self.grid[y][x]
                if tile.tile_type == "corner":
                    tile_char = "C"
                elif tile.tile_type == "straight":
                    tile_char = "S"
                elif tile.tile_type == "half":
                    tile_char = "H"
                else:
                    tile_char = "?"
                power_char = "⚡" if tile.is_powered else " "
                source_char = "🟢" if tile.is_source else ""
                target_char = "🔴" if tile.is_target else ""
                row_str += f"[{tile_char}{tile.rotation}{power_char}{source_char}{target_char}] "
            print(f"Ligne {2-y}: {row_str}")
        print("C=Corner, S=Straight, H=Half, ⚡=Powered, 🟢=Source, 🔴=Target")
        print("===========================\n")
