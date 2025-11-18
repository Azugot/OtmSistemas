from __future__ import annotations

from typing import List

import pulp
from PySide6 import QtCore, QtWidgets


class DietPlannerWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Planejador de Dieta com Restrições Nutricionais")
        self.resize(980, 720)
        self._setup_ui()
        self._seed_food_rows()

    def _setup_ui(self) -> None:
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)

        main_layout = QtWidgets.QVBoxLayout(central)
        splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        main_layout.addWidget(splitter)

        input_panel = QtWidgets.QWidget()
        input_layout = QtWidgets.QVBoxLayout(input_panel)
        input_layout.setContentsMargins(4, 4, 4, 4)
        splitter.addWidget(input_panel)

        self.food_table = QtWidgets.QTableWidget(0, 6)
        self.food_table.setHorizontalHeaderLabels(
            [
                "Alimento",
                "Custo",
                "Calorias",
                "Proteína",
                "Carboidrato",
                "Vitaminas",
            ]
        )
        self.food_table.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch
        )
        self.food_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.food_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        food_controls = QtWidgets.QHBoxLayout()
        add_button = QtWidgets.QPushButton("+")
        remove_button = QtWidgets.QPushButton("–")
        add_button.setFixedWidth(40)
        remove_button.setFixedWidth(40)
        add_button.clicked.connect(self._add_empty_food_row)
        remove_button.clicked.connect(self._remove_selected_row)
        food_controls.addWidget(add_button)
        food_controls.addWidget(remove_button)
        food_controls.addStretch()

        input_layout.addLayout(food_controls)
        input_layout.addWidget(self.food_table)

        goals_group = QtWidgets.QGroupBox("Metas Nutricionais")
        goals_layout = QtWidgets.QFormLayout(goals_group)
        self.calories_goal = self._build_goal_spinbox()
        self.protein_goal = self._build_goal_spinbox()
        self.carb_goal = self._build_goal_spinbox()
        self.vitamins_goal = self._build_goal_spinbox()
        goals_layout.addRow("Mínimo de Calorias", self.calories_goal)
        goals_layout.addRow("Mínimo de Proteína", self.protein_goal)
        goals_layout.addRow("Mínimo de Carboidrato", self.carb_goal)
        goals_layout.addRow("Mínimo de Vitaminas", self.vitamins_goal)
        input_layout.addWidget(goals_group)

        output_panel = QtWidgets.QWidget()
        output_layout = QtWidgets.QVBoxLayout(output_panel)
        output_layout.setContentsMargins(4, 4, 4, 4)
        splitter.addWidget(output_panel)

        self.calculate_button = QtWidgets.QPushButton("Calcular Dieta Otimizada")
        self.calculate_button.setMinimumHeight(40)
        self.calculate_button.clicked.connect(self.optimize_diet)
        output_layout.addWidget(self.calculate_button)

        results_container = QtWidgets.QHBoxLayout()
        self.result_table = QtWidgets.QTableWidget(0, 2)
        self.result_table.setHorizontalHeaderLabels(["Alimento", "Porções"])
        self.result_table.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch
        )
        results_container.addWidget(self.result_table, 2)

        right_panel = QtWidgets.QVBoxLayout()
        self.cost_label = QtWidgets.QLabel("Custo total: —")
        self.nutrient_summary = QtWidgets.QTextEdit()
        self.nutrient_summary.setReadOnly(True)
        right_panel.addWidget(self.cost_label)
        right_panel.addWidget(self.nutrient_summary)
        results_container.addLayout(right_panel, 1)

        output_layout.addLayout(results_container)

    def _build_goal_spinbox(self) -> QtWidgets.QDoubleSpinBox:
        spin = QtWidgets.QDoubleSpinBox()
        spin.setRange(0.0, 1_000_000.0)
        spin.setDecimals(2)
        spin.setSingleStep(10.0)
        return spin

    def _seed_food_rows(self) -> None:
        defaults = [
            ("Arroz", 1.5, 200, 4, 45, 1),
            ("Feijão", 2.0, 180, 9, 30, 2),
            ("Frango", 4.5, 250, 30, 0, 3),
        ]
        for row in defaults:
            self._add_food_row(row)
        self.calories_goal.setValue(2000)
        self.protein_goal.setValue(60)
        self.carb_goal.setValue(250)
        self.vitamins_goal.setValue(10)

    def _add_empty_food_row(self) -> None:
        self._add_food_row(("", 0.0, 0.0, 0.0, 0.0, 0.0))

    def _add_food_row(self, values: tuple[str, float, float, float, float, float]) -> None:
        row_position = self.food_table.rowCount()
        self.food_table.insertRow(row_position)
        for col, value in enumerate(values):
            item = QtWidgets.QTableWidgetItem(str(value))
            if col > 0:
                item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.food_table.setItem(row_position, col, item)

    def _remove_selected_row(self) -> None:
        row = self.food_table.currentRow()
        if row >= 0:
            self.food_table.removeRow(row)

    def optimize_diet(self) -> None:
        foods = self._collect_food_rows()
        if not foods:
            self._show_error("Adicione ao menos um alimento com todos os campos preenchidos.")
            return

        goals = {
            "calories": self.calories_goal.value(),
            "protein": self.protein_goal.value(),
            "carb": self.carb_goal.value(),
            "vitamins": self.vitamins_goal.value(),
        }

        if all(value <= 0 for value in goals.values()):
            self._show_error("Defina metas nutricionais maiores que zero.")
            return

        problem = pulp.LpProblem("diet", pulp.LpMinimize)
        portions = {
            food["name"]: pulp.LpVariable(food["name"], lowBound=0)
            for food in foods
        }

        problem += pulp.lpSum(food["cost"] * portions[food["name"]] for food in foods)

        problem += (
            pulp.lpSum(food["calories"] * portions[food["name"]] for food in foods)
            >= goals["calories"]
        )
        problem += (
            pulp.lpSum(food["protein"] * portions[food["name"]] for food in foods)
            >= goals["protein"]
        )
        problem += (
            pulp.lpSum(food["carb"] * portions[food["name"]] for food in foods)
            >= goals["carb"]
        )
        problem += (
            pulp.lpSum(food["vitamins"] * portions[food["name"]] for food in foods)
            >= goals["vitamins"]
        )

        status = problem.solve(pulp.PULP_CBC_CMD(msg=False))
        if status != pulp.LpStatusOptimal:
            self._show_error("Nenhuma solução viável foi encontrada para as restrições.")
            return

        self._populate_results(foods, portions)

    def _collect_food_rows(self) -> List[dict]:
        foods: List[dict] = []
        for row in range(self.food_table.rowCount()):
            values: List[str] = []
            for col in range(self.food_table.columnCount()):
                item = self.food_table.item(row, col)
                values.append(item.text().strip() if item else "")

            name, *numeric_values = values
            if not name and not any(v for v in numeric_values):
                continue

            try:
                cost, calories, protein, carb, vitamins = map(float, numeric_values)
            except ValueError:
                self._show_error(
                    "Todos os campos numéricos devem conter valores válidos."
                )
                return []

            if not name:
                self._show_error("Informe o nome de cada alimento.")
                return []

            foods.append(
                {
                    "name": name,
                    "cost": cost,
                    "calories": calories,
                    "protein": protein,
                    "carb": carb,
                    "vitamins": vitamins,
                }
            )
        return foods

    def _populate_results(self, foods: List[dict], portions: dict) -> None:
        self.result_table.setRowCount(0)
        cost_total = 0.0
        totals = {"calories": 0.0, "protein": 0.0, "carb": 0.0, "vitamins": 0.0}

        for food in foods:
            qty = portions[food["name"]].value()
            if qty and qty > 0:
                row = self.result_table.rowCount()
                self.result_table.insertRow(row)
                self.result_table.setItem(row, 0, QtWidgets.QTableWidgetItem(food["name"]))
                qty_item = QtWidgets.QTableWidgetItem(f"{qty:.2f}")
                qty_item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
                self.result_table.setItem(row, 1, qty_item)
                cost_total += food["cost"] * qty
                totals["calories"] += food["calories"] * qty
                totals["protein"] += food["protein"] * qty
                totals["carb"] += food["carb"] * qty
                totals["vitamins"] += food["vitamins"] * qty

        self.cost_label.setText(f"Custo total: R$ {cost_total:.2f}")
        summary_lines = [
            "Nutrientes alcançados:",
            f"Calorias: {totals['calories']:.2f}",
            f"Proteína: {totals['protein']:.2f}",
            f"Carboidrato: {totals['carb']:.2f}",
            f"Vitaminas: {totals['vitamins']:.2f}",
        ]
        self.nutrient_summary.setPlainText("\n".join(summary_lines))

    def _show_error(self, message: str) -> None:
        QtWidgets.QMessageBox.warning(self, "Aviso", message)


def main() -> None:
    app = QtWidgets.QApplication([])
    window = DietPlannerWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
