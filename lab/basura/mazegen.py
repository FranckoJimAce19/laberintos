"""
mazegen.py - Generador de laberintos para Pac-Man
Implementación completa con simetría como en el proyecto original
"""

import random
import math
from enum import Enum
from geometry import Direction, vec_add, vec_sub, vec_distance


class CellType(Enum):
    """Tipos de celdas en el laberinto"""
    EMPTY = 0
    DOT = 1
    POWER_PELLET = 2
    FRUIT = 3


class Symmetry(Enum):
    """Tipos de simetría para el laberinto"""
    NONE = 0
    HORIZONTAL = 1
    VERTICAL = 2
    ROTATIONAL = 3
    BOTH = 4


class Cell:
    """Representa una celda en el laberinto"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.walls = set()  # Direcciones que tienen pared
        self.type = CellType.EMPTY
        self.visited = False
        self.distance = 0
        self.is_intersection = False
        self.is_dead_end = False
        
    def __repr__(self):
        return f"Cell({self.x}, {self.y})"
    
    def pos(self):
        """Devuelve la posición como tupla"""
        return (self.x, self.y)
    
    def has_wall(self, direction):
        """Verifica si hay pared en una dirección"""
        return direction in self.walls
    
    def add_wall(self, direction):
        """Añade una pared en una dirección"""
        self.walls.add(direction)
    
    def remove_wall(self, direction):
        """Elimina una pared en una dirección"""
        self.walls.discard(direction)
    
    def wall_count(self):
        """Cuenta el número de paredes"""
        return len(self.walls)
    
    def exit_count(self):
        """Cuenta el número de salidas (paredes faltantes)"""
        return 4 - len(self.walls)
    
    def is_corner(self):
        """Verifica si es una esquina (2 paredes adyacentes)"""
        if len(self.walls) != 2:
            return False
        
        dirs = list(self.walls)
        # Dos paredes son adyacentes si no son opuestas
        return Direction.opposite(dirs[0]) != dirs[1]


class Maze:
    """Representa el laberinto completo con soporte para simetría"""
    
    # Exponer tipos como atributos de clase
    CellType = CellType
    Symmetry = Symmetry
    
    def __init__(self, width, height, wrap=False, symmetry=Symmetry.NONE):
        self.width = width
        self.height = height
        self.wrap = wrap  # Si el laberinto se envuelve (túneles)
        self.symmetry = symmetry
        self.cells = [[Cell(x, y) for y in range(height)] for x in range(width)]
        self.fruit_pos = None
        self.power_pellet_positions = []
        
        # Validar dimensiones para simetría
        if symmetry in [Symmetry.HORIZONTAL, Symmetry.ROTATIONAL, Symmetry.BOTH] and width % 2 != 0:
            raise ValueError(f"Ancho debe ser par para simetría {symmetry}")
        if symmetry in [Symmetry.VERTICAL, Symmetry.ROTATIONAL, Symmetry.BOTH] and height % 2 != 0:
            raise ValueError(f"Alto debe ser par para simetría {symmetry}")
    
    def get_cell(self, x, y):
        """Obtiene una celda por coordenadas"""
        if self.wrap:
            x = x % self.width
            y = y % self.height
        elif x < 0 or x >= self.width or y < 0 or y >= self.height:
            return None
        return self.cells[x][y]
    
    def get_neighbor(self, cell, direction):
        """Obtiene la celda vecina en una dirección"""
        dx, dy = direction.value
        return self.get_cell(cell.x + dx, cell.y + dy)
    
    def remove_wall_between(self, cell1, cell2):
        """Elimina la pared entre dos celdas adyacentes"""
        # Encuentra la dirección de cell1 a cell2
        dx = cell2.x - cell1.x
        dy = cell2.y - cell1.y
        
        direction = Direction.from_vector(dx, dy)
        if direction is None:
            # Para wrap, verificar si están conectados a través del borde
            if self.wrap:
                if dx == self.width - 1 and dy == 0:
                    direction1 = Direction.LEFT
                    direction2 = Direction.RIGHT
                elif dx == -(self.width - 1) and dy == 0:
                    direction1 = Direction.RIGHT
                    direction2 = Direction.LEFT
                elif dx == 0 and dy == self.height - 1:
                    direction1 = Direction.UP
                    direction2 = Direction.DOWN
                elif dx == 0 and dy == -(self.height - 1):
                    direction1 = Direction.DOWN
                    direction2 = Direction.UP
                else:
                    return
                
                cell1.remove_wall(direction1)
                cell2.remove_wall(direction2)
            return
        
        opposite = Direction.opposite(direction)
        cell1.remove_wall(direction)
        cell2.remove_wall(opposite)
    
    def add_wall_between(self, cell1, cell2):
        """Añade una pared entre dos celdas adyacentes"""
        # Encuentra la dirección de cell1 a cell2
        dx = cell2.x - cell1.x
        dy = cell2.y - cell1.y
        
        direction = Direction.from_vector(dx, dy)
        if direction is None:
            # Para wrap, verificar si están conectados a través del borde
            if self.wrap:
                if dx == self.width - 1 and dy == 0:
                    direction1 = Direction.LEFT
                    direction2 = Direction.RIGHT
                elif dx == -(self.width - 1) and dy == 0:
                    direction1 = Direction.RIGHT
                    direction2 = Direction.LEFT
                elif dx == 0 and dy == self.height - 1:
                    direction1 = Direction.UP
                    direction2 = Direction.DOWN
                elif dx == 0 and dy == -(self.height - 1):
                    direction1 = Direction.DOWN
                    direction2 = Direction.UP
                else:
                    return
                
                cell1.add_wall(direction1)
                cell2.add_wall(direction2)
            return
        
        opposite = Direction.opposite(direction)
        cell1.add_wall(direction)
        cell2.add_wall(opposite)
    
    def _get_symmetric_cell(self, x, y):
        """Obtiene las celdas simétricas para una posición dada"""
        cells = [(x, y)]
        
        if self.symmetry == Symmetry.HORIZONTAL:
            mirror_x = self.width - 1 - x
            if mirror_x != x:
                cells.append((mirror_x, y))
        
        elif self.symmetry == Symmetry.VERTICAL:
            mirror_y = self.height - 1 - y
            if mirror_y != y:
                cells.append((x, mirror_y))
        
        elif self.symmetry == Symmetry.ROTATIONAL:
            mirror_x = self.width - 1 - x
            mirror_y = self.height - 1 - y
            if mirror_x != x or mirror_y != y:
                cells.append((mirror_x, mirror_y))
        
        elif self.symmetry == Symmetry.BOTH:
            mirror_x = self.width - 1 - x
            mirror_y = self.height - 1 - y
            if mirror_x != x:
                cells.append((mirror_x, y))
            if mirror_y != y:
                cells.append((x, mirror_y))
            if mirror_x != x and mirror_y != y:
                cells.append((mirror_x, mirror_y))
        
        return cells
    
    def _apply_symmetric_wall_removal(self, cell, direction):
        """Aplica la eliminación de pared de forma simétrica"""
        # Obtener todas las posiciones simétricas
        symmetric_positions = self._get_symmetric_cell(cell.x, cell.y)
        
        for pos in symmetric_positions:
            base_cell = self.get_cell(pos[0], pos[1])
            if not base_cell:
                continue
            
            # Obtener direcciones simétricas para esta posición
            if pos == (cell.x, cell.y):
                symmetric_directions = [direction]
            else:
                # Calcular la transformación aplicada
                dx_transform = pos[0] - cell.x
                dy_transform = pos[1] - cell.y
                
                # Aplicar transformación a la dirección
                if dx_transform != 0:  # Reflexión horizontal
                    if direction == Direction.LEFT:
                        symmetric_directions = [Direction.RIGHT]
                    elif direction == Direction.RIGHT:
                        symmetric_directions = [Direction.LEFT]
                    else:
                        symmetric_directions = [direction]
                elif dy_transform != 0:  # Reflexión vertical
                    if direction == Direction.UP:
                        symmetric_directions = [Direction.DOWN]
                    elif direction == Direction.DOWN:
                        symmetric_directions = [Direction.UP]
                    else:
                        symmetric_directions = [direction]
                else:
                    symmetric_directions = [direction]
            
            # Aplicar a cada dirección simétrica
            for sym_dir in symmetric_directions:
                neighbor = self.get_neighbor(base_cell, sym_dir)
                if neighbor:
                    self.remove_wall_between(base_cell, neighbor)
    
    def generate(self, start_x=0, start_y=0):
        """Genera el laberinto usando Depth-First Search con simetría"""
        # Ajustar punto de inicio para simetría
        if self.symmetry != Symmetry.NONE:
            start_x = min(start_x, self.width // 2)
            start_y = min(start_y, self.height // 2)
        
        # Inicializa todas las celdas como no visitadas
        for x in range(self.width):
            for y in range(self.height):
                cell = self.cells[x][y]
                cell.visited = False
                # Empieza con todas las paredes
                cell.walls = set(Direction.all())
        
        # Pila para DFS
        stack = []
        start_cell = self.get_cell(start_x, start_y)
        start_cell.visited = True
        stack.append(start_cell)
        
        while stack:
            current = stack[-1]
            
            # Obtener vecinos no visitados
            neighbors = []
            for direction in Direction.all():
                neighbor = self.get_neighbor(current, direction)
                if neighbor and not neighbor.visited:
                    neighbors.append((neighbor, direction))
            
            if neighbors:
                # Elegir un vecino aleatorio
                neighbor, direction = random.choice(neighbors)
                
                # Eliminar pared entre current y neighbor (con simetría)
                self._apply_symmetric_wall_removal(current, direction)
                
                # Marcar como visitado y añadir a la pila
                neighbor.visited = True
                stack.append(neighbor)
            else:
                # Retroceder
                stack.pop()
        
        # Asegurar que todas las celdas simétricas estén visitadas
        if self.symmetry != Symmetry.NONE:
            for x in range(self.width):
                for y in range(self.height):
                    cell = self.cells[x][y]
                    if not cell.visited:
                        # Encontrar la celda base correspondiente
                        if self.symmetry == Symmetry.HORIZONTAL:
                            base_x = x if x < self.width // 2 else self.width - 1 - x
                            base_cell = self.get_cell(base_x, y)
                        elif self.symmetry == Symmetry.VERTICAL:
                            base_y = y if y < self.height // 2 else self.height - 1 - y
                            base_cell = self.get_cell(x, base_y)
                        elif self.symmetry == Symmetry.ROTATIONAL:
                            base_x = x if x < self.width // 2 else self.width - 1 - x
                            base_y = y if y < self.height // 2 else self.height - 1 - y
                            base_cell = self.get_cell(base_x, base_y)
                        elif self.symmetry == Symmetry.BOTH:
                            base_x = x if x < self.width // 2 else self.width - 1 - x
                            base_y = y if y < self.height // 2 else self.height - 1 - y
                            base_cell = self.get_cell(base_x, base_y)
                        
                        if base_cell and base_cell.visited:
                            # Copiar paredes de la celda base
                            cell.walls = base_cell.walls.copy()
                            cell.visited = True
        
        # Identificar intersecciones y dead ends
        self._analyze_cells()
        
        # Eliminar dead ends (como se especifica en las restricciones)
        self._remove_dead_ends()
    
    def _analyze_cells(self):
        """Analiza las celdas para identificar intersecciones y dead ends"""
        for x in range(self.width):
            for y in range(self.height):
                cell = self.cells[x][y]
                exits = cell.exit_count()
                cell.is_intersection = exits > 2
                cell.is_dead_end = exits == 1
    
    def _remove_dead_ends(self):
        """Elimina los dead ends del laberinto (restricción del proyecto)"""
        changed = True
        while changed:
            changed = False
            for x in range(self.width):
                for y in range(self.height):
                    cell = self.cells[x][y]
                    if cell.exit_count() == 1:  # Es un dead end
                        # Encontrar la única salida
                        exit_dir = None
                        for direction in Direction.all():
                            if not cell.has_wall(direction):
                                exit_dir = direction
                                break
                        
                        if exit_dir:
                            # Conectar con un vecino para eliminar el dead end
                            for direction in Direction.all():
                                if direction != exit_dir and cell.has_wall(direction):
                                    neighbor = self.get_neighbor(cell, direction)
                                    if neighbor and neighbor.exit_count() >= 2:
                                        # Eliminar la pared para conectar
                                        self.remove_wall_between(cell, neighbor)
                                        changed = True
                                        break
    
    def to_string(self, show_walls=True):
        """Convierte el laberinto a una representación de texto"""
        result = []
        
        # Paredes superiores
        if show_walls:
            for y in range(self.height):
                line = ""
                for x in range(self.width):
                    cell = self.cells[x][y]
                    line += "+"
                    line += "---" if cell.has_wall(Direction.UP) else "   "
                line += "+"
                result.append(line)
        
        # Celdas y paredes laterales
        for y in range(self.height):
            line = ""
            for x in range(self.width):
                cell = self.cells[x][y]
                
                if show_walls and x == 0:
                    line += "|" if cell.has_wall(Direction.LEFT) else " "
                
                # Contenido de la celda
                if cell.type == CellType.DOT:
                    line += " · "
                elif cell.type == CellType.POWER_PELLET:
                    line += " ○ "
                elif cell.type == CellType.FRUIT:
                    line += " F "
                else:
                    # Mostrar algo para intersecciones y dead ends
                    if cell.is_intersection:
                        line += " I "
                    elif cell.is_dead_end:
                        line += " D "
                    else:
                        line += "   "
                
                if show_walls:
                    line += "|" if cell.has_wall(Direction.RIGHT) else " "
            
            result.append(line)
            
            # Paredes inferiores
            if show_walls:
                line = ""
                for x in range(self.width):
                    cell = self.cells[x][y]
                    line += "+"
                    line += "---" if cell.has_wall(Direction.DOWN) else "   "
                line += "+"
                result.append(line)
        
        return "\n".join(result)
    
    def to_simple_string(self):
        """Representación simple del laberinto"""
        result = []
        for y in range(self.height):
            line = ""
            for x in range(self.width):
                cell = self.cells[x][y]
                if cell.wall_count() == 4:
                    line += "#"
                elif cell.exit_count() == 1:
                    line += "D"  # Dead end
                elif cell.is_intersection:
                    line += "I"  # Intersección
                else:
                    line += "."
            result.append(line)
        return "\n".join(result)
    
    def get_cell_graph(self):
        """Devuelve el grafo de conexiones entre celdas"""
        graph = {}
        for x in range(self.width):
            for y in range(self.height):
                cell = self.cells[x][y]
                neighbors = []
                
                for direction in Direction.all():
                    if not cell.has_wall(direction):
                        neighbor = self.get_neighbor(cell, direction)
                        if neighbor:
                            neighbors.append(neighbor.pos())
                
                graph[cell.pos()] = neighbors
        
        return graph
    
    def get_statistics(self):
        """Obtiene estadísticas del laberinto"""
        stats = {
            'width': self.width,
            'height': self.height,
            'wrap': self.wrap,
            'symmetry': self.symmetry.name,
            'total_cells': self.width * self.height,
            'intersections': 0,
            'dead_ends': 0,
            'corridors': 0,
            'total_walls': 0,
            'walls_i': 0,    # Paredes tipo I
            'walls_l': 0,    # Paredes tipo L
            'walls_t': 0,    # Paredes tipo T
            'walls_plus': 0, # Paredes tipo +
        }
        
        for x in range(self.width):
            for y in range(self.height):
                cell = self.cells[x][y]
                stats['total_walls'] += cell.wall_count()
                
                if cell.is_intersection:
                    stats['intersections'] += 1
                elif cell.is_dead_end:
                    stats['dead_ends'] += 1
                else:
                    stats['corridors'] += 1
                
                # Contar tipos de paredes basados en la forma
                if cell.wall_count() == 4:
                    stats['walls_i'] += 1
                elif cell.is_corner():
                    stats['walls_l'] += 1
                elif cell.is_intersection:
                    if cell.exit_count() == 1:  # T
                        stats['walls_t'] += 1
                    else:  # +
                        stats['walls_plus'] += 1
        
        stats['avg_exits'] = (self.width * self.height * 4 - stats['total_walls']) / stats['total_cells']
        stats['wall_percentage'] = stats['total_walls'] / (stats['total_cells'] * 4) * 100
        
        return stats