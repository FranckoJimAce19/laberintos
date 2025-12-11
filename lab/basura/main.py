"""
main.py - Punto de entrada principal con soporte para simetría y Tetris
"""

import argparse
import random
from mazegen import Maze, Symmetry
from tetris_maze import TetrisMaze
from render import MazeRenderer


def generate_random_maze():
    """Genera un laberinto con parámetros aleatorios"""
    width = random.choice([10, 12, 14, 16, 18, 20, 22, 24])
    height = random.choice([10, 12, 14, 16, 18, 20, 22, 24])
    wrap = random.choice([True, False])
    symmetry = random.choice(list(Symmetry))
    
    # Ajustar dimensiones para simetría
    if symmetry in [Symmetry.HORIZONTAL, Symmetry.ROTATIONAL, Symmetry.BOTH]:
        width = (width // 2) * 2  # Asegurar par
    if symmetry in [Symmetry.VERTICAL, Symmetry.ROTATIONAL, Symmetry.BOTH]:
        height = (height // 2) * 2  # Asegurar par
    
    maze = Maze(width, height, wrap, symmetry)
    maze.generate()
    
    return maze


def print_maze_info(maze):
    """Imprime información sobre el laberinto"""
    stats = maze.get_statistics()
    
    print("\n" + "="*60)
    print("INFORMACIÓN DEL LABERINTO")
    print("="*60)
    print(f"Dimensiones: {stats['width']}x{stats['height']}")
    print(f"Simetría: {stats['symmetry']}")
    print(f"Wrap: {'Sí' if stats['wrap'] else 'No'}")
    print(f"Total de celdas: {stats['total_cells']}")
    print(f"Intersecciones: {stats['intersections']}")
    print(f"Dead ends: {stats['dead_ends']}")
    print(f"Corredores: {stats['corridors']}")
    print(f"Promedio de salidas por celda: {stats['avg_exits']:.2f}")
    print(f"Porcentaje de paredes: {stats['wall_percentage']:.1f}%")
    
    # Información de tipos de paredes (solo si está disponible)
    if 'walls_i' in stats:
        print(f"Paredes tipo I: {stats['walls_i']}")
        print(f"Paredes tipo L: {stats['walls_l']}")
        print(f"Paredes tipo T: {stats['walls_t']}")
        print(f"Paredes tipo +: {stats['walls_plus']}")
    
    print("="*60)
    
    # Mostrar laberinto en texto
    print("\nREPRESENTACIÓN DEL LABERINTO:")
    print("(# = Pared, . = Corredor, I = Intersección, D = Dead end)")
    print(maze.to_simple_string())


def test_symmetry():
    """Prueba todos los tipos de simetría"""
    print("\n" + "="*60)
    print("PRUEBA DE TODOS LOS TIPOS DE SIMETRÍA")
    print("="*60)
    
    test_cases = [
        (8, 8, False, Symmetry.NONE, "Sin simetría"),
        (8, 8, False, Symmetry.HORIZONTAL, "Simetría horizontal"),
        (8, 8, False, Symmetry.VERTICAL, "Simetría vertical"),
        (8, 8, False, Symmetry.ROTATIONAL, "Simetría rotacional"),
        (8, 8, False, Symmetry.BOTH, "Simetría en ambos ejes"),
    ]
    
    for width, height, wrap, symmetry, description in test_cases:
        print(f"\n{description} ({width}x{height}):")
        try:
            maze = Maze(width, height, wrap, symmetry)
            maze.generate()
            print(maze.to_simple_string())
        except ValueError as e:
            print(f"Error: {e}")


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Generador de laberintos Pac-Man con simetría')
    parser.add_argument('--width', type=int, default=20, help='Ancho del laberinto (par para simetría)')
    parser.add_argument('--height', type=int, default=20, help='Alto del laberinto (par para simetría)')
    parser.add_argument('--wrap', action='store_true', help='Habilitar wrap (túneles)')
    parser.add_argument('--symmetry', type=str, default='NONE', 
                       choices=['NONE', 'HORIZONTAL', 'VERTICAL', 'ROTATIONAL', 'BOTH'],
                       help='Tipo de simetría')
    parser.add_argument('--random', action='store_true', help='Generar laberinto aleatorio')
    parser.add_argument('--tetris', action='store_true', help='Usar algoritmo de Tetris (Pac-Man auténtico)')
    parser.add_argument('--no-gui', action='store_true', help='Solo mostrar en consola')
    parser.add_argument('--seed', type=int, help='Semilla para números aleatorios')
    parser.add_argument('--test', action='store_true', help='Probar todos los tipos de simetría')
    
    args = parser.parse_args()
    
    # Establecer semilla si se proporciona
    if args.seed is not None:
        random.seed(args.seed)
    
    # Ejecutar prueba si se solicita
    if args.test:
        test_symmetry()
        return
    
    # Convertir string de simetría a enum
    symmetry = getattr(Symmetry, args.symmetry.upper())
    
    # Ajustar dimensiones para simetría
    width = args.width
    height = args.height
    
    if symmetry in [Symmetry.HORIZONTAL, Symmetry.ROTATIONAL, Symmetry.BOTH] and width % 2 != 0:
        print(f"Advertencia: Ancho ajustado de {width} a {width + 1} para simetría {symmetry.name}")
        width += 1
    
    if symmetry in [Symmetry.VERTICAL, Symmetry.ROTATIONAL, Symmetry.BOTH] and height % 2 != 0:
        print(f"Advertencia: Alto ajustado de {height} a {height + 1} para simetría {symmetry.name}")
        height += 1
    
    # Generar laberinto
    if args.tetris:
        print("Generando laberinto con algoritmo de Tetris...")
        maze = TetrisMaze()
        maze.generate()
        
        # Mostrar información adicional de Tetris
        if hasattr(maze, 'print_tetris_grid'):
            maze.print_tetris_grid()
        if hasattr(maze, 'print_tile_grid'):
            maze.print_tile_grid()
            
    elif args.random:
        maze = generate_random_maze()
    else:
        maze = Maze(width, height, args.wrap, symmetry)
        maze.generate()
    
    # Mostrar información
    print_maze_info(maze)
    
    # GUI o solo consola
    if not args.no_gui:
        try:
            # Intentar importar pygame
            import pygame
            # Iniciar renderizado
            cell_size = max(15, 800 // max(maze.width, maze.height))
            renderer = MazeRenderer(maze, cell_size=cell_size)
            renderer.run()
        except ImportError:
            print("\nPygame no está instalado. Ejecuta: pip install pygame")
            print("Para usar la interfaz gráfica.")
    else:
        # Mostrar representación detallada en consola
        print("\nREPRESENTACIÓN DETALLADA:")
        print(maze.to_string())


if __name__ == "__main__":
    main()