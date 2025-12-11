"""
geometry.py - Funciones de geometría para el generador de laberintos
Traducción completa del proyecto original
"""

import math
from enum import Enum

class Direction(Enum):
    """Direcciones cardinales"""
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    
    @staticmethod
    def opposite(direction):
        """Devuelve la dirección opuesta"""
        opposites = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT
        }
        return opposites.get(direction)
    
    @staticmethod
    def all():
        """Devuelve todas las direcciones"""
        return [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]
    
    @staticmethod
    def from_vector(dx, dy):
        """Obtiene la dirección desde un vector"""
        if dx == 1 and dy == 0:
            return Direction.RIGHT
        elif dx == -1 and dy == 0:
            return Direction.LEFT
        elif dx == 0 and dy == 1:
            return Direction.DOWN
        elif dx == 0 and dy == -1:
            return Direction.UP
        return None
    
    @staticmethod
    def to_string(direction):
        """Convierte dirección a string"""
        return direction.name.lower()


def vec_add(v1, v2):
    """Suma de vectores"""
    return (v1[0] + v2[0], v1[1] + v2[1])


def vec_sub(v1, v2):
    """Resta de vectores"""
    return (v1[0] - v2[0], v1[1] - v2[1])


def vec_mul(v, scalar):
    """Multiplicación escalar"""
    return (v[0] * scalar, v[1] * scalar)


def vec_equal(v1, v2):
    """Comparación de vectores"""
    return v1[0] == v2[0] and v1[1] == v2[1]


def vec_length(v):
    """Longitud del vector"""
    return math.sqrt(v[0]*v[0] + v[1]*v[1])


def vec_distance(v1, v2):
    """Distancia entre dos puntos"""
    return vec_length(vec_sub(v2, v1))


def vec_dot(v1, v2):
    """Producto punto"""
    return v1[0]*v2[0] + v1[1]*v2[1]