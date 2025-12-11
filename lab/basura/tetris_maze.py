"""
tetris_maze.py - Generador de laberintos estilo Tetris para Pac-Man
Basado en el algoritmo descrito en la documentación del proyecto original
"""

import random
import math
from enum import Enum
from geometry import Direction
from mazegen import Maze, Symmetry, CellType


class TetrisPiece(Enum):
    """Piezas de Tetris que pueden formar las paredes"""
    I = 0      # Recta vertical/horizontal
    L = 1      # Esquina
    T = 2      # Intersección T
    PLUS = 3   # Intersección +
    SQUARE = 4 # Bloque cuadrado


class TetrisMaze(Maze):
    """Generador de laberintos usando piezas de Tetris"""
    
    def __init__(self):
        # Dimensiones base del proyecto original: 5x9
        base_width = 5
        base_height = 9
        
        # Dimensiones finales de Pac-Man: 28x31
        final_width = 28
        final_height = 31
        
        # Ajustes de escala: 5x9 -> 15x27 -> 28x31
        # 5 * 3 = 15, 9 * 3 = 27
        # Necesitamos 13 columnas más y 4 filas más
        width = base_width * 3 + 13
        height = base_height * 3 + 4
        
        super().__init__(width, height, wrap=False, symmetry=Symmetry.HORIZONTAL)
        
        # Variables específicas para Tetris
        self.base_width = base_width
        self.base_height = base_height
        self.final_width = final_width
        self.final_height = final_height
        self.tetris_grid = [[None for _ in range(base_height)] 
                           for _ in range(base_width)]
        self.tile_grid = [[0 for _ in range(height)] 
                         for _ in range(width)]
    
    def generate_tetris_grid(self):
        """Genera la cuadrícula de 5x9 con piezas de Tetris"""
        # Inicializar todas las celdas como vacías
        for x in range(self.base_width):
            for y in range(self.base_height):
                self.tetris_grid[x][y] = TetrisPiece.SQUARE
        
        # Definir áreas especiales (basado en el diagrama del proyecto)
        # Área de inicio de Pac-Man y fantasmas (filas 7-8, columna 1)
        if self.base_height > 7 and self.base_width > 1:
            self.tetris_grid[1][6] = TetrisPiece.I  # Entre filas 7 y 8 (índices 6 y 7)
            self.tetris_grid[1][7] = TetrisPiece.I
        
        # Generar piezas aleatorias pero simétricas
        for x in range(self.base_width // 2 + 1):
            for y in range(self.base_height):
                # Evitar sobrescribir áreas especiales
                if (x == 1 and y in [6, 7]):
                    continue
                
                # Elegir pieza aleatoria
                if random.random() < 0.3:  # 30% de probabilidad de no ser SQUARE
                    piece = random.choice([TetrisPiece.I, TetrisPiece.L, 
                                         TetrisPiece.T, TetrisPiece.PLUS])
                else:
                    piece = TetrisPiece.SQUARE
                
                self.tetris_grid[x][y] = piece
                
                # Aplicar simetría horizontal
                if x < self.base_width // 2:
                    mirror_x = self.base_width - 1 - x
                    self.tetris_grid[mirror_x][y] = piece
    
    def tetris_to_tiles(self):
        """Convierte la cuadrícula de Tetris a tiles de 3x3"""
        # Primero, crear una cuadrícula temporal 15x27 (5*3 x 9*3)
        temp_width = self.base_width * 3
        temp_height = self.base_height * 3
        temp_grid = [[0 for _ in range(temp_height)] 
                    for _ in range(temp_width)]
        
        # Convertir cada celda de Tetris a un bloque 3x3
        for tx in range(self.base_width):
            for ty in range(self.base_height):
                piece = self.tetris_grid[tx][ty]
                base_x = tx * 3
                base_y = ty * 3
                
                # Mapear pieza de Tetris a patrón de tiles
                if piece == TetrisPiece.SQUARE:
                    # Bloque completo (todos los tiles son paredes)
                    for dx in range(3):
                        for dy in range(3):
                            if base_x + dx < temp_width and base_y + dy < temp_height:
                                temp_grid[base_x + dx][base_y + dy] = 1
                
                elif piece == TetrisPiece.I:
                    # Pieza I: crea un pasillo vertical u horizontal
                    if random.random() < 0.5:  # Vertical
                        for dy in range(3):
                            if base_x + 1 < temp_width and base_y + dy < temp_height:
                                temp_grid[base_x + 1][base_y + dy] = 0  # Pasillo
                    else:  # Horizontal
                        for dx in range(3):
                            if base_x + dx < temp_width and base_y + 1 < temp_height:
                                temp_grid[base_x + dx][base_y + 1] = 0  # Pasillo
                
                elif piece == TetrisPiece.L:
                    # Pieza L: crea una esquina
                    # Centro vacío
                    if base_x + 1 < temp_width and base_y + 1 < temp_height:
                        temp_grid[base_x + 1][base_y + 1] = 0
                    # Dos lados vacíos dependiendo de la orientación
                    orientation = random.choice(['TL', 'TR', 'BL', 'BR'])
                    if orientation in ['TL', 'TR']:  # Parte superior
                        for dx in range(3):
                            if base_x + dx < temp_width and base_y < temp_height:
                                temp_grid[base_x + dx][base_y] = 0
                    if orientation in ['TL', 'BL']:  # Lado izquierdo
                        for dy in range(3):
                            if base_x < temp_width and base_y + dy < temp_height:
                                temp_grid[base_x][base_y + dy] = 0
                    if orientation in ['TR', 'BR']:  # Lado derecho
                        for dy in range(3):
                            if base_x + 2 < temp_width and base_y + dy < temp_height:
                                temp_grid[base_x + 2][base_y + dy] = 0
                    if orientation in ['BL', 'BR']:  # Parte inferior
                        for dx in range(3):
                            if base_x + dx < temp_width and base_y + 2 < temp_height:
                                temp_grid[base_x + dx][base_y + 2] = 0
                
                elif piece in [TetrisPiece.T, TetrisPiece.PLUS]:
                    # Pieza T o PLUS: crea intersecciones
                    # Centro siempre vacío
                    if base_x + 1 < temp_width and base_y + 1 < temp_height:
                        temp_grid[base_x + 1][base_y + 1] = 0
                    
                    # Para T, elegir 3 direcciones; para PLUS, todas las direcciones
                    directions = []
                    if piece == TetrisPiece.T:
                        directions = random.choice([
                            ['up', 'left', 'right'],
                            ['up', 'left', 'down'],
                            ['up', 'right', 'down'],
                            ['left', 'right', 'down']
                        ])
                    else:  # PLUS
                        directions = ['up', 'down', 'left', 'right']
                    
                    # Aplicar direcciones
                    if 'up' in directions and base_y > 0:
                        temp_grid[base_x + 1][base_y] = 0
                    if 'down' in directions and base_y + 2 < temp_height:
                        temp_grid[base_x + 1][base_y + 2] = 0
                    if 'left' in directions and base_x > 0:
                        temp_grid[base_x][base_y + 1] = 0
                    if 'right' in directions and base_x + 2 < temp_width:
                        temp_grid[base_x + 2][base_y + 1] = 0
        
        return temp_grid, temp_width, temp_height
    
    def apply_size_adjustments(self, temp_grid, temp_width, temp_height):
        """Aplica ajustes de tamaño para llegar a 28x31"""
        # Inicializar la cuadrícula final
        self.tile_grid = [[0 for _ in range(self.height)] 
                         for _ in range(self.width)]
        
        # Mapear de la cuadrícula temporal a la final
        # Estrategia simple: estirar la cuadrícula 15x27 a 28x31
        scale_x = self.width / temp_width
        scale_y = self.height / temp_height
        
        for x in range(self.width):
            for y in range(self.height):
                # Mapear coordenadas
                src_x = int(x / scale_x)
                src_y = int(y / scale_y)
                
                # Asegurar que estamos dentro de los límites
                src_x = min(src_x, temp_width - 1)
                src_y = min(src_y, temp_height - 1)
                
                # Copiar valor
                self.tile_grid[x][y] = temp_grid[src_x][src_y]
        
        # Aplicar ajustes específicos de altura y anchura
        # Aumentar altura en algunas columnas, disminuir anchura en algunas filas
        self._apply_height_adjustments()
        self._apply_width_adjustments()
        
        # Suavizar bordes
        self._smooth_edges()
    
    def _apply_height_adjustments(self):
        """Aumenta la altura de una celda por cada columna (ajustes de altura)"""
        # Identificar columnas candidatas para ajuste
        for x in range(1, self.width - 1):
            # Verificar si esta columna puede ser ajustada sin crear paredes feas
            if self._can_adjust_height(x):
                # Aumentar altura: hacer que los pasillos sean más altos
                for y in range(1, self.height - 1):
                    if self.tile_grid[x][y] == 0:  # Si es pasillo
                        # Asegurar que haya espacio arriba y abajo
                        if y > 0 and y < self.height - 1:
                            self.tile_grid[x][y-1] = 0
                            self.tile_grid[x][y+1] = 0
    
    def _apply_width_adjustments(self):
        """Disminuye el ancho de una celda por cada fila (ajustes de anchura)"""
        # Identificar filas candidatas para ajuste
        for y in range(1, self.height - 1):
            # Verificar si esta fila puede ser ajustada sin crear paredes feas
            if self._can_adjust_width(y):
                # Disminuir ancho: hacer que los pasillos sean más estrechos
                for x in range(1, self.width - 1):
                    if self.tile_grid[x][y] == 0:  # Si es pasillo
                        # Asegurar que haya espacio a izquierda y derecha
                        if x > 0 and x < self.width - 1:
                            self.tile_grid[x-1][y] = 1  # Añadir pared
                            self.tile_grid[x+1][y] = 1  # Añadir pared
    
    def _can_adjust_height(self, x):
        """Verifica si una columna puede ser ajustada en altura"""
        # Verificar que no esté en los bordes
        if x == 0 or x == self.width - 1:
            return False
        
        # Verificar que no cree paredes de grosor no uniforme
        for y in range(1, self.height - 1):
            if (self.tile_grid[x-1][y] == 1 and 
                self.tile_grid[x+1][y] == 1 and
                self.tile_grid[x][y] == 0):
                return False
        
        return True
    
    def _can_adjust_width(self, y):
        """Verifica si una fila puede ser ajustada en anchura"""
        # Verificar que no esté en los bordes
        if y == 0 or y == self.height - 1:
            return False
        
        # Verificar que no cree paredes de grosor no uniforme
        for x in range(1, self.width - 1):
            if (self.tile_grid[x][y-1] == 1 and 
                self.tile_grid[x][y+1] == 1 and
                self.tile_grid[x][y] == 0):
                return False
        
        return True
    
    def _smooth_edges(self):
        """Suaviza los bordes para evitar paredes de grosor no uniforme"""
        for x in range(1, self.width - 1):
            for y in range(1, self.height - 1):
                # Si es una pared, verificar sus vecinos
                if self.tile_grid[x][y] == 1:
                    # Contar vecinos que son paredes
                    wall_neighbors = 0
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if dx == 0 and dy == 0:
                                continue
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < self.width and 0 <= ny < self.height:
                                if self.tile_grid[nx][ny] == 1:
                                    wall_neighbors += 1
                    
                    # Si tiene muy pocos vecinos paredes, convertirlo en pasillo
                    if wall_neighbors < 2:
                        self.tile_grid[x][y] = 0
                    # Si tiene muchos vecinos paredes, asegurar que sea pared
                    elif wall_neighbors > 6:
                        self.tile_grid[x][y] = 1
    
    def create_tunnels(self):
        """Crea túneles en los bordes del laberinto"""
        # Posiciones candidatas para túneles (basado en el diagrama)
        tunnel_candidates = []
        
        # Bordes izquierdo y derecho
        for y in range(self.height // 4, 3 * self.height // 4):
            # Lado izquierdo
            if self.tile_grid[0][y] == 1 and self.tile_grid[1][y] == 0:
                tunnel_candidates.append((0, y))
            # Lado derecho
            if self.tile_grid[self.width-1][y] == 1 and self.tile_grid[self.width-2][y] == 0:
                tunnel_candidates.append((self.width-1, y))
        
        # Elegir 1 o 2 túneles (como en Pac-Man original)
        num_tunnels = random.choice([1, 2])
        selected_tunnels = random.sample(tunnel_candidates, 
                                        min(num_tunnels, len(tunnel_candidates)))
        
        # Crear los túneles
        for x, y in selected_tunnels:
            # Hacer un pasillo a través del borde
            self.tile_grid[x][y] = 0
            # Si es el borde izquierdo, conectar con el derecho (wrap)
            if x == 0:
                self.tile_grid[self.width-1][y] = 0
            # Si es el borde derecho, conectar con el izquierdo (wrap)
            elif x == self.width - 1:
                self.tile_grid[0][y] = 0
    
    def convert_to_paths(self):
        """Convierte los tiles a caminos (shift de bordes a centros)"""
        # Crear una nueva cuadrícula para los caminos
        path_grid = [[0 for _ in range(self.height)] 
                    for _ in range(self.width)]
        
        for x in range(1, self.width - 1):
            for y in range(1, self.height - 1):
                # Si un tile tiene un camino que pasa por su centro
                # (es decir, si alguno de sus vecinos es pasillo)
                has_path = False
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if abs(dx) + abs(dy) != 1:  # Solo vecinos ortogonales
                            continue
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            if self.tile_grid[nx][ny] == 0:
                                has_path = True
                                break
                    if has_path:
                        break
                
                if has_path:
                    path_grid[x][y] = 1  # Camino
        
        self.tile_grid = path_grid
    
    def convert_to_walls(self):
        """Convierte los caminos a paredes finales"""
        # Primero, cualquier tile que sea camino se convierte en espacio vacío
        # Luego, cualquier tile que toque un espacio vacío se convierte en pared
        
        # Crear una nueva cuadrícula para el resultado final
        final_grid = [[1 for _ in range(self.height)]  # Inicializar todo como pared
                     for _ in range(self.width)]
        
        # Marcar caminos como espacios vacíos
        for x in range(self.width):
            for y in range(self.height):
                if self.tile_grid[x][y] == 1:  # Es un camino
                    final_grid[x][y] = 0  # Espacio vacío
        
        # Marcar vecinos de espacios vacíos como paredes
        wall_grid = [[1 for _ in range(self.height)] 
                    for _ in range(self.width)]
        
        for x in range(self.width):
            for y in range(self.height):
                if final_grid[x][y] == 0:  # Espacio vacío
                    # Marcar este tile como espacio vacío en el resultado final
                    wall_grid[x][y] = 0
                    # Marcar todos los vecinos como paredes
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if dx == 0 and dy == 0:
                                continue
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < self.width and 0 <= ny < self.height:
                                wall_grid[nx][ny] = 1
        
        self.tile_grid = wall_grid
    
    def generate(self, start_x=0, start_y=0):
        """Genera el laberinto completo usando el algoritmo de Tetris"""
        print("Generando cuadrícula de Tetris 5x9...")
        self.generate_tetris_grid()
        
        print("Convirtiendo a tiles 15x27...")
        temp_grid, temp_width, temp_height = self.tetris_to_tiles()
        
        print("Aplicando ajustes de tamaño a 28x31...")
        self.apply_size_adjustments(temp_grid, temp_width, temp_height)
        
        print("Creando túneles...")
        self.create_tunnels()
        
        print("Convirtiendo a caminos...")
        self.convert_to_paths()
        
        print("Convirtiendo a paredes finales...")
        self.convert_to_walls()
        
        print("Convirtiendo a estructura de Maze...")
        self._convert_to_maze_structure()
        
        print("Análisis de celdas...")
        self._analyze_cells()
        
        print("¡Laberinto generado!")
    
    def _convert_to_maze_structure(self):
        """Convierte la cuadrícula de tiles a la estructura de Maze"""
        # Limpiar todas las celdas existentes
        for x in range(self.width):
            for y in range(self.height):
                cell = self.get_cell(x, y)
                cell.walls = set(Direction.all())
        
        # Crear pasillos basados en tile_grid
        for x in range(self.width):
            for y in range(self.height):
                if self.tile_grid[x][y] == 0:  # Espacio vacío (pasillo)
                    cell = self.get_cell(x, y)
                    
                    # Verificar vecinos para eliminar paredes
                    for direction in Direction.all():
                        dx, dy = direction.value
                        nx, ny = x + dx, y + dy
                        
                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            neighbor = self.get_cell(nx, ny)
                            if neighbor and self.tile_grid[nx][ny] == 0:
                                # Ambos son pasillos, eliminar pared entre ellos
                                self.remove_wall_between(cell, neighbor)
        
        # Asegurar que los túneles funcionen (wrap)
        if self.wrap:
            for y in range(self.height):
                # Verificar bordes izquierdo y derecho
                if (self.tile_grid[0][y] == 0 and 
                    self.tile_grid[self.width-1][y] == 0):
                    left_cell = self.get_cell(0, y)
                    right_cell = self.get_cell(self.width-1, y)
                    if left_cell and right_cell:
                        self.remove_wall_between(left_cell, right_cell)
    
    def print_tetris_grid(self):
        """Imprime la cuadrícula de Tetris"""
        symbols = {
            TetrisPiece.I: 'I',
            TetrisPiece.L: 'L',
            TetrisPiece.T: 'T',
            TetrisPiece.PLUS: '+',
            TetrisPiece.SQUARE: '■'
        }
        
        print("\nCuadrícula de Tetris (5x9):")
        for y in range(self.base_height):
            line = ""
            for x in range(self.base_width):
                piece = self.tetris_grid[x][y]
                line += symbols.get(piece, '?') + " "
            print(line)
    
    def print_tile_grid(self, symbol='#', empty=' '):
        """Imprime la cuadrícula de tiles"""
        print(f"\nCuadrícula de tiles ({self.width}x{self.height}):")
        for y in range(self.height):
            line = ""
            for x in range(self.width):
                if self.tile_grid[x][y] == 1:
                    line += symbol
                else:
                    line += empty
            print(line)