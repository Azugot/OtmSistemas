"""Simplex algorithm with two-phase approach for small LP instances.

The solver supports minimization problems with mixed inequality constraints
by converting them to standard form and applying the simplex tableau method.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

import numpy as np


class InfeasibleProblem(Exception):
    """Raised when the LP is infeasible."""


class UnboundedProblem(Exception):
    """Raised when the LP is unbounded."""


@dataclass
class StandardForm:
    tableau: np.ndarray
    basis: List[int]
    var_names: List[str]
    decision_vars: int
    artificial_vars: List[int]
    objective: np.ndarray


class SimplexSolver:
    """Solve linear programs using the two-phase simplex method."""

    def solve(
        self, c: Sequence[float], A: Sequence[Sequence[float]], b: Sequence[float], signs: Sequence[str]
    ) -> np.ndarray:
        """Solve a minimization problem returning the decision variable values.

        Args:
            c: Coefficients of the objective function (minimization).
            A: Constraint coefficient matrix.
            b: Right-hand side vector.
            signs: Constraint signs ("<=", ">=", "=").
        """

        standard = self._to_standard_form(c, A, b, signs)
        tableau, basis = self._phase_one(standard)
        solution = self._phase_two(standard, tableau, basis)
        return solution

    def _to_standard_form(
        self,
        c: Sequence[float],
        A: Sequence[Sequence[float]],
        b: Sequence[float],
        signs: Sequence[str],
    ) -> StandardForm:
        A = np.array(A, dtype=float)
        b = np.array(b, dtype=float)
        c = np.array(c, dtype=float)
        num_constraints, num_vars = A.shape

        var_names: List[str] = [f"x{i+1}" for i in range(num_vars)]
        basis: List[int] = []
        artificial_vars: List[int] = []

        rows: List[List[float]] = []
        for i in range(num_constraints):
            row = list(A[i]) + [0.0] * (len(var_names) - num_vars)
            sign = signs[i]
            if sign == "<=":
                for prev in rows:
                    prev.append(0.0)
                row.append(1.0)
                basis.append(len(var_names))
                var_names.append(f"s{i+1}")
            elif sign == ">=":
                for prev in rows:
                    prev.append(0.0)
                row.append(-1.0)
                var_names.append(f"e{i+1}")
                for prev in rows:
                    prev.append(0.0)
                art_col = len(var_names)
                row.append(1.0)
                basis.append(art_col)
                var_names.append(f"a{i+1}")
                artificial_vars.append(art_col)
            else:  # equality
                for prev in rows:
                    prev.append(0.0)
                row.append(1.0)
                art_col = len(var_names)
                basis.append(art_col)
                var_names.append(f"a{i+1}")
                artificial_vars.append(art_col)
            rows.append(row)

        max_cols = max(len(r) for r in rows)
        normalized_rows = [r + [0.0] * (max_cols - len(r)) + [b[i]] for i, r in enumerate(rows)]
        tableau = np.array(normalized_rows, dtype=float)

        objective = np.concatenate([c, [0.0] * (tableau.shape[1] - len(c))])

        decision_vars = num_vars
        return StandardForm(
            tableau=tableau,
            basis=basis,
            var_names=var_names,
            decision_vars=decision_vars,
            artificial_vars=artificial_vars,
            objective=objective,
        )

    def _phase_one(self, standard: StandardForm):
        tableau = standard.tableau.copy()
        rows, cols = tableau.shape
        obj = np.zeros(cols)

        for art_idx in standard.artificial_vars:
            obj[art_idx] = -1.0

        tableau = np.vstack([tableau, obj])

        for i, var in enumerate(standard.basis):
            if var in standard.artificial_vars:
                tableau[-1] += tableau[i]

        tableau = self._simplex(tableau, standard.basis)

        if abs(tableau[-1, -1]) > 1e-7:
            raise InfeasibleProblem("Não foi encontrada solução viável.")

        return tableau[:-1], standard.basis

    def _phase_two(self, standard: StandardForm, tableau: np.ndarray, basis: List[int]) -> np.ndarray:
        rows, cols = tableau.shape
        objective = np.zeros(cols)
        for j in range(standard.decision_vars):
            objective[j] = -standard.objective[j] if j < len(standard.objective) else 0.0

        full_tableau = np.vstack([tableau, objective])

        for i, var in enumerate(basis):
            coeff = full_tableau[-1, var]
            if abs(coeff) > 1e-9:
                full_tableau[-1] -= coeff * full_tableau[i]

        full_tableau = self._simplex(full_tableau, basis)

        solution = np.zeros(standard.decision_vars)
        for i, var in enumerate(basis):
            if var < standard.decision_vars:
                solution[var] = full_tableau[i, -1]
        return solution

    def _simplex(self, tableau: np.ndarray, basis: List[int]) -> np.ndarray:
        rows, cols = tableau.shape
        while True:
            objective = tableau[-1, :-1]
            entering = int(np.argmax(objective))
            if objective[entering] <= 1e-9:
                break

            ratios = []
            for i in range(rows - 1):
                if tableau[i, entering] > 1e-9:
                    ratios.append(tableau[i, -1] / tableau[i, entering])
                else:
                    ratios.append(np.inf)
            leaving_row = int(np.argmin(ratios))
            if ratios[leaving_row] == np.inf:
                raise UnboundedProblem("Problema ilimitado.")

            pivot = tableau[leaving_row, entering]
            tableau[leaving_row] = tableau[leaving_row] / pivot
            for i in range(rows):
                if i != leaving_row:
                    tableau[i] -= tableau[i, entering] * tableau[leaving_row]
            basis[leaving_row] = entering

        return tableau
