"""Domain objects and orchestration for the kitchen optimization problem."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import numpy as np

from .simplex import InfeasibleProblem, SimplexSolver, UnboundedProblem


@dataclass
class Dish:
    name: str
    demand: float
    stove_time: float
    oven_time: float
    water: float
    gas: float
    energy: float
    team_time: float


@dataclass
class Period:
    name: str
    stove_capacity: float
    oven_capacity: float
    team_capacity: float


@dataclass
class OptimizationResult:
    status: str
    schedule: Dict[Tuple[str, str], float] = field(default_factory=dict)
    total_cost: float = 0.0
    breakdown: Dict[str, float] = field(default_factory=dict)
    utilization: Dict[str, Dict[str, float]] = field(default_factory=dict)


class KitchenOptimizer:
    def __init__(self) -> None:
        self.dishes: List[Dish] = []
        self.periods: List[Period] = []
        self.costs = {"gas": 0.0, "energy": 0.0, "water": 0.0}

    def add_dish(self, dish: Dish) -> None:
        self.dishes.append(dish)

    def add_period(self, period: Period) -> None:
        self.periods.append(period)

    def set_costs(self, gas: float, energy: float, water: float) -> None:
        self.costs = {"gas": gas, "energy": energy, "water": water}

    def build_problem(self):
        num_vars = len(self.dishes) * len(self.periods)
        c = np.zeros(num_vars)

        for i, dish in enumerate(self.dishes):
            for t, _ in enumerate(self.periods):
                idx = i * len(self.periods) + t
                c[idx] = (
                    self.costs["gas"] * dish.gas
                    + self.costs["energy"] * dish.energy
                    + self.costs["water"] * dish.water
                )

        A = []
        b = []
        signs: List[str] = []

        # Demand constraints: sum_t x_{i,t} >= D_i
        for i, dish in enumerate(self.dishes):
            row = np.zeros(num_vars)
            for t in range(len(self.periods)):
                row[i * len(self.periods) + t] = 1.0
            A.append(row)
            b.append(dish.demand)
            signs.append(">=")

        # Stove capacity per period
        for t, _ in enumerate(self.periods):
            row = np.zeros(num_vars)
            for i, dish in enumerate(self.dishes):
                row[i * len(self.periods) + t] = dish.stove_time
            A.append(row)
            b.append(self.periods[t].stove_capacity)
            signs.append("<=")

        # Oven capacity per period
        for t, _ in enumerate(self.periods):
            row = np.zeros(num_vars)
            for i, dish in enumerate(self.dishes):
                row[i * len(self.periods) + t] = dish.oven_time
            A.append(row)
            b.append(self.periods[t].oven_capacity)
            signs.append("<=")

        # Team capacity per period
        for t, _ in enumerate(self.periods):
            row = np.zeros(num_vars)
            for i, dish in enumerate(self.dishes):
                row[i * len(self.periods) + t] = dish.team_time
            A.append(row)
            b.append(self.periods[t].team_capacity)
            signs.append("<=")

        return c, np.array(A), np.array(b), signs

    def solve(self) -> OptimizationResult:
        if not self.dishes or not self.periods:
            return OptimizationResult(status="Dados incompletos")

        c, A, b, signs = self.build_problem()

        solver = SimplexSolver()
        try:
            solution = solver.solve(c, A, b, signs)
        except InfeasibleProblem:
            return OptimizationResult(status="Problema inviável")
        except UnboundedProblem:
            return OptimizationResult(status="Problema ilimitado")

        schedule: Dict[Tuple[str, str], float] = {}
        breakdown = {"gas": 0.0, "energy": 0.0, "water": 0.0}
        utilization = {
            "stove": {period.name: 0.0 for period in self.periods},
            "oven": {period.name: 0.0 for period in self.periods},
            "team": {period.name: 0.0 for period in self.periods},
        }

        for i, dish in enumerate(self.dishes):
            for t, period in enumerate(self.periods):
                idx = i * len(self.periods) + t
                qty = max(0.0, float(solution[idx]))
                schedule[(dish.name, period.name)] = qty
                breakdown["gas"] += qty * dish.gas * self.costs["gas"]
                breakdown["energy"] += qty * dish.energy * self.costs["energy"]
                breakdown["water"] += qty * dish.water * self.costs["water"]
                utilization["stove"][period.name] += qty * dish.stove_time
                utilization["oven"][period.name] += qty * dish.oven_time
                utilization["team"][period.name] += qty * dish.team_time

        total_cost = sum(breakdown.values())
        return OptimizationResult(
            status="Ótimo encontrado",
            schedule=schedule,
            total_cost=total_cost,
            breakdown=breakdown,
            utilization=utilization,
        )
