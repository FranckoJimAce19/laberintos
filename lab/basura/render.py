"""
render.py - Renderizado del laberinto usando Pygame
Con visualización mejorada para simetría y Tetris
"""

import pygame
import sys
from geometry import Direction
from mazegen import Maze, CellType, Symmetry


class MazeRenderer:
    """Renderiza el laberinto usando Pygame con soporte para simetría"""
    
    def __init__(self, maze, cell_size=20, wall_thickness=3):
        self.maze = maze
        self.cell_size = cell_size
        self.wall_thickness = wall_thickness
        
        # Colores
        self.bg_color = (0, 0, 0)  # Negro
        self.wall_color = (33, 33, 222)  # Azul Pac-Man
        self.symmetry_color = (255, 100, 100, 100)  # Rojo semitransparente
        self.intersection_color = (100, 255, 100, 50)  # Verde semitransparente
        self.dead_end_color = (255, 100, 100, 50)  # Rojo semitransparente
        self.grid_color = (40, 40, 40)  # Gris oscuro
        self.text_color = (220, 220, 255)  # Azul claro
        self.path_color = (40, 40, 100)  # Azul oscuro para caminos
        
        # Calcular dimensiones de la ventana
        maze_width = maze.width * cell_size + wall_thickness
        maze_height = maze.height * cell_size + wall_thickness
        
        # Espacio para estadísticas
        self.stats_width = 300
        self.width = maze_width + self.stats_width
        self.height = maze_height
        
        # Inicializar Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        
        # Título basado en el tipo de laberinto
        if hasattr(maze, 'tetris_grid'):
            title = "Pac-Man Maze Generator - Algoritmo Tetris"
        else:
            title = f"Pac-Man Maze Generator - {maze.symmetry.name}"
        pygame.display.set_caption(title)
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 22)
        self.title_font = pygame.font.Font(None, 28)
        
        # Variables de estado
        self.show_grid = True
        self.show_analysis = True
        self.show_symmetry = True
        self.show_paths = False
    
    def pos_to_pixel(self, x, y):
        """Convierte coordenadas de celda a píxeles"""
        return (
            x * self.cell_size + self.wall_thickness // 2,
            y * self.cell_size + self.wall_thickness // 2
        )
    
    def draw_walls(self):
        """Dibuja las paredes del laberinto"""
        for x in range(self.maze.width):
            for y in range(self.maze.height):
                cell = self.maze.get_cell(x, y)
                cell_x, cell_y = self.pos_to_pixel(x, y)
                
                # Dibujar pared superior
                if cell.has_wall(Direction.UP):
                    start_pos = (cell_x, cell_y)
                    end_pos = (cell_x + self.cell_size, cell_y)
                    pygame.draw.line(self.screen, self.wall_color, 
                                   start_pos, end_pos, self.wall_thickness)
                
                # Dibujar pared inferior
                if cell.has_wall(Direction.DOWN):
                    start_pos = (cell_x, cell_y + self.cell_size)
                    end_pos = (cell_x + self.cell_size, cell_y + self.cell_size)
                    pygame.draw.line(self.screen, self.wall_color,
                                   start_pos, end_pos, self.wall_thickness)
                
                # Dibujar pared izquierda
                if cell.has_wall(Direction.LEFT):
                    start_pos = (cell_x, cell_y)
                    end_pos = (cell_x, cell_y + self.cell_size)
                    pygame.draw.line(self.screen, self.wall_color,
                                   start_pos, end_pos, self.wall_thickness)
                
                # Dibujar pared derecha
                if cell.has_wall(Direction.RIGHT):
                    start_pos = (cell_x + self.cell_size, cell_y)
                    end_pos = (cell_x + self.cell_size, cell_y + self.cell_size)
                    pygame.draw.line(self.screen, self.wall_color,
                                   start_pos, end_pos, self.wall_thickness)
    
    def draw_paths(self):
        """Dibuja los caminos (espacios vacíos)"""
        if not self.show_paths:
            return
        
        for x in range(self.maze.width):
            for y in range(self.maze.height):
                cell = self.maze.get_cell(x, y)
                if cell.exit_count() > 0:  # Tiene al menos una salida
                    rect = pygame.Rect(
                        x * self.cell_size + self.wall_thickness,
                        y * self.cell_size + self.wall_thickness,
                        self.cell_size - self.wall_thickness,
                        self.cell_size - self.wall_thickness
                    )
                    pygame.draw.rect(self.screen, self.path_color, rect)
    
    def draw_symmetry_lines(self):
        """Dibuja líneas que muestran los ejes de simetría"""
        if not self.show_symmetry or self.maze.symmetry == Symmetry.NONE:
            return
        
        # Crear una superficie semitransparente
        symmetry_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Dibujar línea vertical central para simetría horizontal
        if self.maze.symmetry in [Symmetry.HORIZONTAL, Symmetry.ROTATIONAL, Symmetry.BOTH]:
            center_x = self.maze.width // 2 * self.cell_size + self.wall_thickness // 2
            pygame.draw.line(symmetry_surface, self.symmetry_color,
                           (center_x, 0),
                           (center_x, self.height),
                           2)
        
        # Dibujar línea horizontal central para simetría vertical
        if self.maze.symmetry in [Symmetry.VERTICAL, Symmetry.ROTATIONAL, Symmetry.BOTH]:
            center_y = self.maze.height // 2 * self.cell_size + self.wall_thickness // 2
            pygame.draw.line(symmetry_surface, self.symmetry_color,
                           (0, center_y),
                           (self.maze.width * self.cell_size, center_y),
                           2)
        
        # Dibujar la superficie en la pantalla
        self.screen.blit(symmetry_surface, (0, 0))
    
    def draw_cell_analysis(self):
        """Resalta intersecciones y dead ends"""
        if not self.show_analysis:
            return
        
        # Crear una superficie semitransparente
        analysis_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        for x in range(self.maze.width):
            for y in range(self.maze.height):
                cell = self.maze.get_cell(x, y)
                
                # Determinar color basado en el tipo de celda
                if cell.is_intersection:
                    color = self.intersection_color
                elif cell.is_dead_end:
                    color = self.dead_end_color
                else:
                    continue
                
                # Dibujar rectángulo semitransparente
                rect = pygame.Rect(
                    x * self.cell_size,
                    y * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
                pygame.draw.rect(analysis_surface, color, rect)
        
        # Dibujar la superficie en la pantalla
        self.screen.blit(analysis_surface, (0, 0))
    
    def draw_grid(self):
        """Dibuja la cuadrícula de fondo"""
        # Líneas verticales
        for x in range(self.maze.width + 1):
            pixel_x = x * self.cell_size
            pygame.draw.line(self.screen, self.grid_color,
                           (pixel_x, 0),
                           (pixel_x, self.maze.height * self.cell_size), 1)
        
        # Líneas horizontales
        for y in range(self.maze.height + 1):
            pixel_y = y * self.cell_size
            pygame.draw.line(self.screen, self.grid_color,
                           (0, pixel_y),
                           (self.maze.width * self.cell_size, pixel_y), 1)
    
    def draw_statistics(self):
        """Dibuja estadísticas del laberinto"""
        stats = self.maze.get_statistics()
        
        # Posición inicial para las estadísticas
        stats_x = self.maze.width * self.cell_size + 10
        stats_y = 10
        
        # Título
        if hasattr(self.maze, 'tetris_grid'):
            title = "Pac-Man (Algoritmo Tetris)"
        else:
            title = "Laberinto Simétrico"
        
        title_surface = self.title_font.render(title, True, self.text_color)
        self.screen.blit(title_surface, (stats_x, stats_y))
        stats_y += 40
        
        # Información básica
        info_lines = [
            f"Tamaño: {stats['width']}x{stats['height']}",
            f"Simetría: {stats['symmetry']}",
            f"Wrap: {'Sí' if stats['wrap'] else 'No'}",
            f"",
            f"Celdas totales: {stats['total_cells']}",
            f"Intersecciones: {stats['intersections']}",
            f"Dead ends: {stats['dead_ends']}",
            f"Corredores: {stats['corridors']}",
            f"",
            f"Promedio de salidas: {stats['avg_exits']:.2f}",
            f"Porcentaje de paredes: {stats['wall_percentage']:.1f}%"
        ]
        
        # Añadir información de tipos de paredes si está disponible
        if 'walls_i' in stats:
            info_lines.extend([
                f"",
                f"Tipos de paredes:",
                f"  I: {stats['walls_i']}",
                f"  L: {stats['walls_l']}",
                f"  T: {stats['walls_t']}",
                f"  +: {stats['walls_plus']}"
            ])
        
        for line in info_lines:
            text = self.font.render(line, True, self.text_color)
            self.screen.blit(text, (stats_x, stats_y))
            stats_y += 22
        
        # Controles
        stats_y += 20
        controls = [
            "Controles:",
            "R: Regenerar laberinto",
            "G: Alternar cuadrícula",
            "A: Alternar análisis",
            "S: Alternar simetría",
            "P: Alternar caminos",
            "ESPACIO: Cambiar simetría",
            "T: Cambiar a Tetris/DFS",
            "ESC: Salir"
        ]
        
        for line in controls:
            text = self.font.render(line, True, self.text_color)
            self.screen.blit(text, (stats_x, stats_y))
            stats_y += 22
    
    def draw(self):
        """Dibuja todo el laberinto"""
        # Fondo
        self.screen.fill(self.bg_color)
        
        # Caminos (si están activos)
        self.draw_paths()
        
        # Cuadrícula
        if self.show_grid:
            self.draw_grid()
        
        # Análisis de celdas
        self.draw_cell_analysis()
        
        # Líneas de simetría
        self.draw_symmetry_lines()
        
        # Paredes
        self.draw_walls()
        
        # Estadísticas
        self.draw_statistics()
    
    def run(self, fps=60):
        """Bucle principal de renderizado"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        # Regenerar laberinto
                        self.maze.generate()
                    elif event.key == pygame.K_g:
                        # Alternar cuadrícula
                        self.show_grid = not self.show_grid
                    elif event.key == pygame.K_a:
                        # Alternar análisis
                        self.show_analysis = not self.show_analysis
                    elif event.key == pygame.K_s:
                        # Alternar simetría visible
                        self.show_symmetry = not self.show_symmetry
                    elif event.key == pygame.K_p:
                        # Alternar visualización de caminos
                        self.show_paths = not self.show_paths
                    elif event.key == pygame.K_SPACE:
                        # Cambiar tipo de simetría
                        if hasattr(self.maze, 'tetris_grid'):
                            print("No se puede cambiar simetría en modo Tetris")
                        else:
                            current_index = list(Symmetry).index(self.maze.symmetry)
                            next_index = (current_index + 1) % len(Symmetry)
                            new_symmetry = list(Symmetry)[next_index]
                            
                            # Verificar dimensiones para la nueva simetría
                            try:
                                self.maze.symmetry = new_symmetry
                                self.maze.generate()
                                pygame.display.set_caption(f"Pac-Man Maze Generator - {new_symmetry.name}")
                            except ValueError as e:
                                print(f"No se puede cambiar a {new_symmetry.name}: {e}")
                                # Revertir
                                self.maze.symmetry = list(Symmetry)[current_index]
                    elif event.key == pygame.K_t:
                        # Alternar entre Tetris y DFS
                        print("Cambiando algoritmo...")
                        # Esto requeriría recrear el laberinto, lo omitimos por ahora
                        print("Función no implementada en esta versión")
            
            # Dibujar
            self.draw()
            
            # Actualizar pantalla
            pygame.display.flip()
            self.clock.tick(fps)
        
        pygame.quit()
        sys.exit()