from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Tuple


@dataclass
class SimplexResult:
    status: str
    objective_value: float | None
    solution: List[float] | None


class TwoPhaseSimplex:
    def __init__(self, c: Sequence[float], A: Sequence[Sequence[float]], b: Sequence[float], signs: Sequence[str]):
        self.c = list(c)
        self.A = [list(row) for row in A]
        self.b = list(b)
        self.signs = list(signs)
        self.tableau: List[List[float]] = []
        self.basis: List[int] = []
        self.artificial_vars: List[int] = []

    def _pad_columns(self, width: int) -> None:
        for row in self.tableau:
            while len(row) < width:
                row.insert(len(row) - 1, 0.0)

    def _append_column(self) -> int:
        new_index = len(self.tableau[0]) - 1
        self._pad_columns(new_index + 2)
        return new_index

    def _to_standard_form(self) -> None:
        self.tableau = []
        self.basis = []
        self.artificial_vars = []

        num_vars = len(self.c)
        for coefficients, sign, rhs in zip(self.A, self.signs, self.b):
            row = list(coefficients)
            b_value = rhs
            inequality = sign

            if b_value < 0:
                row = [-val for val in row]
                b_value = -b_value
                if inequality == '<=':
                    inequality = '>='
                elif inequality == '>=':
                    inequality = '<='

            if not self.tableau:
                self.tableau = [[0.0 for _ in range(num_vars)] + [b_value]]
            else:
                row += [0.0] * (len(self.tableau[0]) - 1 - len(row))
                self.tableau.append(row + [b_value])

            current_index = len(self.tableau) - 1
            if len(self.tableau) <= 1:
                self.tableau[0] = row + [b_value]

            if inequality == '<=':
                slack_col = self._append_column()
                self.tableau[current_index][slack_col] = 1.0
                self.basis.append(slack_col)
            elif inequality == '>=':
                surplus_col = self._append_column()
                self.tableau[current_index][surplus_col] = -1.0

                artificial_col = self._append_column()
                for r_idx, r in enumerate(self.tableau):
                    r[artificial_col] = 1.0 if r_idx == current_index else 0.0
                self.basis.append(artificial_col)
                self.artificial_vars.append(artificial_col)
            else:  # equality
                artificial_col = self._append_column()
                for r_idx, r in enumerate(self.tableau):
                    r[artificial_col] = 1.0 if r_idx == current_index else 0.0
                self.basis.append(artificial_col)
                self.artificial_vars.append(artificial_col)

    def _build_objective_row(self, costs: List[float]) -> List[float]:
        width = len(self.tableau[0])
        costs += [0.0] * (width - 1 - len(costs))
        obj_row = [-c for c in costs] + [0.0]
        for row, basic in zip(self.tableau, self.basis):
            c_basic = costs[basic]
            if c_basic != 0:
                for j in range(width):
                    obj_row[j] += c_basic * row[j]
        return obj_row

    def _pivot(self, row_idx: int, col_idx: int) -> None:
        pivot_val = self.tableau[row_idx][col_idx]
        if abs(pivot_val) < 1e-12:
            raise ZeroDivisionError("Pivot value is too small")

        self.tableau[row_idx] = [v / pivot_val for v in self.tableau[row_idx]]
        for r_idx, row in enumerate(self.tableau):
            if r_idx == row_idx:
                continue
            factor = row[col_idx]
            if factor != 0:
                self.tableau[r_idx] = [row_val - factor * self.tableau[row_idx][c_idx] for c_idx, row_val in enumerate(row)]
        self.basis[row_idx] = col_idx

    def _simplex(self, costs: List[float]) -> Tuple[bool, List[List[float]]]:
        obj_row = self._build_objective_row(costs)
        self.tableau.append(obj_row)

        num_rows = len(self.tableau)
        num_cols = len(self.tableau[0]) - 1

        while True:
            obj = self.tableau[-1]
            entering_col, max_coeff = max(((j, coeff) for j, coeff in enumerate(obj[:-1])), key=lambda t: t[1])
            if max_coeff <= 1e-9:
                return True, self.tableau

            ratios = []
            for i in range(num_rows - 1):
                coeff = self.tableau[i][entering_col]
                if coeff > 1e-9:
                    ratios.append((self.tableau[i][-1] / coeff, i))
            if not ratios:
                return False, self.tableau

            _, pivot_row = min(ratios)
            self._pivot(pivot_row, entering_col)

    def solve(self) -> SimplexResult:
        self._to_standard_form()
        phase_one_costs = [1.0 if idx in self.artificial_vars else 0.0 for idx in range(len(self.tableau[0]) - 1)]
        feasible, tableau = self._simplex(phase_one_costs)
        if not feasible or (-tableau[-1][-1]) > 1e-7:
            return SimplexResult(status="Problema inviável", objective_value=None, solution=None)

        for col in sorted(self.artificial_vars, reverse=True):
            for row in self.tableau:
                del row[col]
        self.c += [0.0] * (len(self.tableau[0]) - 1 - len(self.c))
        self.tableau.pop()
        self.basis = [b - sum(1 for a in self.artificial_vars if a < b) for b in self.basis]

        feasible, tableau = self._simplex(self.c)
        if not feasible:
            return SimplexResult(status="Problema inviável", objective_value=None, solution=None)

        solution = [0.0 for _ in range(len(self.tableau[0]) - 1)]
        for row_idx, basic_col in enumerate(self.basis):
            solution[basic_col] = self.tableau[row_idx][-1]

        optimal_value = self.tableau[-1][-1] * -1
        return SimplexResult(status="Ótimo encontrado", objective_value=optimal_value, solution=solution)


def _example() -> SimplexResult:
    c = [3.0, 2.0]
    A = [
        [1.0, -1.0],
        [-1.0, -1.0],
    ]
    b = [0.0, -4.0]
    signs = ['>=', '=']

    simplex = TwoPhaseSimplex(c, A, b, signs)
    return simplex.solve()


if __name__ == "__main__":
    result = _example()
    print(result)
