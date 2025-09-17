import arcade
import math
import random

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
TILE_SIZE = 120
GRID_SIZE = 3  # Grille 3x3 pour rester simple

# Types de circuits
CIRCUIT_SHAPES = {
    "line": [[(0,1),(0,-1)], [(1,0),(-1,0)]],  # vertical / horizontal
    "corner": [[(0,1),(1,0)], [(1,0),(0,-1)], [(0,-1),(-1,0)], [(-1,0),(0,1)]]
}

class Circuit:
    def __init__(self, x, y, shape="line"):
        self.x = x
        self.y = y
        self.shape = shape
        self.rotation = 0
        self.powered = False
        self.animation_timer = 0
        self.correct_position = False
    
    def rotate(self):
        self.rotation = (self.rotation + 1) % len(CIRCUIT_SHAPES[self.shape])
        return self.rotation
    
    def get_connections(self):
        return CIRCUIT_SHAPES[self.shape][self.rotation]
    
    def update(self, delta_time):
        self.animation_timer += delta_time * 60
    
    def draw(self, selected=False):
        cx = self.x * TILE_SIZE + TILE_SIZE // 2 + 50
        cy = self.y * TILE_SIZE + TILE_SIZE // 2 + 100
        
        # Couleurs futuristes
        if selected:
            pulse = 150 + 100 * math.sin(self.animation_timer * 0.1)
            base_color = (85, 106, 161)
            glow_alpha = int(pulse)
        elif self.correct_position:
            base_color = (50, 168, 82)  # Vert pour position correcte
            glow_alpha = 150
        else:
            base_color = (44, 86, 110)
            glow_alpha = 100
        
        panel_size = TILE_SIZE - 10
        half_panel = panel_size // 2
        
        # Glow sélection ou position correcte
        if selected or self.correct_position:
            arcade.draw_circle_filled(cx, cy, half_panel + 15, (*base_color, glow_alpha//3))
        
        # Bordures
        corners = [
            (cx - half_panel, cy - half_panel),
            (cx + half_panel, cy - half_panel),
            (cx + half_panel, cy + half_panel),
            (cx - half_panel, cy + half_panel)
        ]
        for i in range(4):
            start = corners[i]
            end = corners[(i + 1) % 4]
            arcade.draw_line(start[0], start[1], end[0], end[1], base_color, 3)
        
        # Coins décoratifs
        for corner_x, corner_y in corners:
            arcade.draw_circle_filled(corner_x, corner_y, 6, (0, 255, 220))
        
        # Connexions
        for dx, dy in self.get_connections():
            end_x = cx + dx * (TILE_SIZE//2 - 10)
            end_y = cy + dy * (TILE_SIZE//2 - 10)
            if self.powered:
                line_color = (0, 255, 220)
                thickness = 6
            else:
                line_color = (147, 150, 185)
                thickness = 4
            arcade.draw_line(cx, cy, end_x, end_y, line_color, thickness)
            arcade.draw_circle_filled(end_x, end_y, 4, line_color)
        
        # Centre
        center_color = (255, 255, 0) if self.powered else (100, 100, 100)
        arcade.draw_circle_filled(cx, cy, 6, center_color)
        
        # Indicateur de rotation
        if selected:
            arcade.draw_text("↻", cx, cy - 40, (200, 200, 255), 20, anchor_x="center")

class SpaceCircuitPuzzle(arcade.View):
    def __init__(self, on_complete=None):
        super().__init__()
        self.bg_color = arcade.color.BLACK
        self.title_color = (0, 255, 220)
        self.text_color = (180, 180, 255)
        
        # Configuration prédéfinie pour un chemin simple
        self.correct_rotations = {
            (0, 0): 1,  # Coin pointant vers droite et bas
            (0, 1): 0,  # Ligne verticale
            (0, 2): 1,  # Coin pointant vers droite et haut
            (1, 0): 1,  # Ligne horizontale
            (1, 1): 0,  # Ligne verticale (centre)
            (1, 2): 1,  # Ligne horizontale
            (2, 0): 2,  # Coin pointant vers gauche et bas
            (2, 1): 0,  # Ligne verticale
            (2, 2): 3,  # Coin pointant vers gauche et haut
        }
        
        # Grille avec configuration simple
        self.grid = []
        for y in range(GRID_SIZE):
            row = []
            for x in range(GRID_SIZE):
                # Déterminer le type de pièce
                is_corner = (x == 0 and y == 0) or (x == 0 and y == 2) or (x == 2 and y == 0) or (x == 2 and y == 2)
                shape = "corner" if is_corner else "line"
                
                circuit = Circuit(x, y, shape)
                
                # Rotation initiale - seulement 40% des pièces commencent dans la bonne direction
                if random.random() < 0.4:  # 40% de chance d'être dans la bonne position
                    circuit.rotation = self.correct_rotations[(x, y)]
                    circuit.correct_position = True
                else:
                    # Mauvaises rotations possibles
                    if shape == "line":
                        wrong_rotations = [r for r in range(len(CIRCUIT_SHAPES[shape])) if r != self.correct_rotations[(x, y)]]
                        circuit.rotation = random.choice(wrong_rotations)
                    else:
                        wrong_rotations = [r for r in range(len(CIRCUIT_SHAPES[shape])) if r != self.correct_rotations[(x, y)]]
                        circuit.rotation = random.choice(wrong_rotations)
                
                row.append(circuit)
            self.grid.append(row)
        
        # Source d'énergie en haut à gauche
        self.grid[0][0].powered = True
        self.source_x, self.source_y = 0, 0
        self.target_x, self.target_y = 2, 2
        
        self.sel_x, self.sel_y = 0, 0
        self.on_complete = on_complete
        self.animation_timer = 0
        self.completed = False
        self.showing_path = False
        self.path_timer = 0
    
    def on_draw(self):
        self.clear(self.bg_color)
        self.draw_space_background()
        
        arcade.draw_text("🛰️ RÉPARATION DE CIRCUITS",
                         SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50,
                         self.title_color, 28, anchor_x="center", bold=True)
        
        arcade.draw_text("Flèches: Déplacement • Espace: Rotation • R: Voir le chemin • Échap: Quitter",
                         SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80,
                         self.text_color, 14, anchor_x="center")
        
        # Dessiner le chemin cible en arrière-plan si demandé
        if self.showing_path:
            self.draw_target_path()
        
        for row in self.grid:
            for circuit in row:
                selected = (circuit.x == self.sel_x and circuit.y == self.sel_y)
                circuit.draw(selected)
        
        # Indicateur source et cible
        source_cx = self.source_x * TILE_SIZE + TILE_SIZE // 2 + 50
        source_cy = self.source_y * TILE_SIZE + TILE_SIZE // 2 + 100
        arcade.draw_circle_filled(source_cx, source_cy, 15, (0, 255, 0))
        arcade.draw_text("SOURCE", source_cx, source_cy - 30, (0, 255, 0), 12, anchor_x="center")
        
        target_cx = self.target_x * TILE_SIZE + TILE_SIZE // 2 + 50
        target_cy = self.target_y * TILE_SIZE + TILE_SIZE // 2 + 100
        arcade.draw_circle_filled(target_cx, target_cy, 15, (255, 100, 100))
        arcade.draw_text("CIBLE", target_cx, target_cy - 30, (255, 100, 100), 12, anchor_x="center")
        
        if self.completed:
            arcade.draw_text("✅ RÉPARATION RÉUSSIE !",
                             SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150,
                             (0, 255, 0), 32, anchor_x="center", bold=True)
            arcade.draw_text("Énergie restaurée dans tout le système",
                             SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 110,
                             self.text_color, 18, anchor_x="center")
            arcade.draw_text("Appuyez sur ÉCHAP pour continuer",
                             SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80,
                             self.text_color, 16, anchor_x="center")
    
    def draw_target_path(self):
        """Dessine le chemin cible en pointillés"""
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                cx = x * TILE_SIZE + TILE_SIZE // 2 + 50
                cy = y * TILE_SIZE + TILE_SIZE // 2 + 100
                
                # Dessiner les connexions du chemin cible
                correct_rotation = self.correct_rotations[(x, y)]
                for dx, dy in CIRCUIT_SHAPES[self.grid[y][x].shape][correct_rotation]:
                    end_x = cx + dx * (TILE_SIZE//2 - 10)
                    end_y = cy + dy * (TILE_SIZE//2 - 10)
                    
                    # Dessiner en pointillés
                    arcade.draw_line(cx, cy, end_x, end_y, (255, 255, 0, 100), 3)
    
    def draw_space_background(self):
        for i in range(100):
            x = (i * 37 + int(self.animation_timer * 1.5)) % SCREEN_WIDTH
            y = (i * 73) % SCREEN_HEIGHT
            size = 1 + (i % 2)
            twinkle = int(128 + 127 * math.sin(self.animation_timer * 0.05 + i))
            color = (twinkle, twinkle, twinkle)
            arcade.draw_circle_filled(x, y, size, color)
    
    def on_key_press(self, key, modifiers):
        if not self.completed:
            if key == arcade.key.RIGHT and self.sel_x < GRID_SIZE - 1:
                self.sel_x += 1
            elif key == arcade.key.LEFT and self.sel_x > 0:
                self.sel_x -= 1
            elif key == arcade.key.UP and self.sel_y < GRID_SIZE - 1:
                self.sel_y += 1
            elif key == arcade.key.DOWN and self.sel_y > 0:
                self.sel_y -= 1
            elif key == arcade.key.SPACE:
                new_rotation = self.grid[self.sel_y][self.sel_x].rotate()
                # Vérifier si la nouvelle rotation est correcte
                correct_rotation = self.correct_rotations[(self.sel_x, self.sel_y)]
                self.grid[self.sel_y][self.sel_x].correct_position = (new_rotation == correct_rotation)
                self.check_completion()
            elif key == arcade.key.R:
                self.showing_path = True
                self.path_timer = 2.0  # Montrer le chemin pendant 2 secondes
        elif key == arcade.key.ESCAPE and self.on_complete:
            self.on_complete()
    
    def check_completion(self):
        """Propagation de l'énergie depuis la source"""
        for row in self.grid:
            for circuit in row:
                circuit.powered = False
        
        visited = set()
        def dfs(x, y):
            if (x, y) in visited:
                return
            visited.add((x, y))
            circuit = self.grid[y][x]
            circuit.powered = True
            
            for dx, dy in circuit.get_connections():
                nx, ny = x + dx, y + dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                    neighbor = self.grid[ny][nx]
                    for ndx, ndy in neighbor.get_connections():
                        if nx + ndx == x and ny + ndy == y:
                            dfs(nx, ny)
        
        dfs(self.source_x, self.source_y)  # Source en haut à gauche
        
        # Victoire si la cible est alimentée
        if self.grid[self.target_y][self.target_x].powered:
            self.completed = True
    
    def on_update(self, delta_time):
        self.animation_timer += delta_time * 60
        
        # Gérer le timer pour afficher le chemin
        if self.showing_path:
            self.path_timer -= delta_time
            if self.path_timer <= 0:
                self.showing_path = False
        
        for row in self.grid:
            for circuit in row:
                circuit.update(delta_time)

# Test direct
def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "Réparation de Circuits Spatiaux")
    puzzle = SpaceCircuitPuzzle(on_complete=window.close)
    window.show_view(puzzle)
    arcade.run()

if __name__ == "__main__":
    main()