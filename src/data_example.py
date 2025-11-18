"""Example data mirroring the PRD specification."""
from __future__ import annotations

from .model import Dish, Period


EXAMPLE_COSTS = {"gas": 4.5, "energy": 0.85, "water": 0.05}

EXAMPLE_DISHES = [
    Dish("Arroz Branco", 100, 30, 0, 5, 0.3, 0, 10),
    Dish("Feijão Preto", 80, 50, 0, 8, 0.4, 0, 15),
    Dish("Frango Grelhado", 60, 20, 30, 10, 0.2, 1.5, 25),
    Dish("Lasanha", 40, 15, 45, 12, 0.1, 2.0, 30),
    Dish("Salada Verde", 90, 0, 0, 15, 0, 0.1, 10),
    Dish("Purê de Batata", 50, 25, 0, 8, 0.25, 0, 12),
    Dish("Bife à Parmegiana", 30, 15, 20, 10, 0.3, 1.2, 35),
    Dish("Sopa de Legumes", 70, 40, 0, 20, 0.35, 0, 18),
    Dish("Macarrão ao Molho", 85, 20, 0, 6, 0.2, 0, 12),
    Dish("Torta de Frango", 35, 10, 40, 8, 0.15, 1.8, 28),
]

EXAMPLE_PERIODS = [
    Period("Manhã (6h-12h)", 240, 180, 720),
    Period("Tarde (12h-18h)", 300, 240, 900),
    Period("Noite (18h-22h)", 180, 120, 480),
]
