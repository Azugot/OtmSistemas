from __future__ import annotations

from typing import List, TypedDict

import pulp
import streamlit as st


class FoodRow(TypedDict):
    name: str
    cost: float
    calories: float
    protein: float
    carb: float
    vitamins: float


def initialize_foods() -> None:
    if "foods" not in st.session_state:
        st.session_state.foods = [
            FoodRow(name="Arroz", cost=1.5, calories=200, protein=4, carb=45, vitamins=1),
            FoodRow(name="Feijão", cost=2.0, calories=180, protein=9, carb=30, vitamins=2),
            FoodRow(name="Frango", cost=4.5, calories=250, protein=30, carb=0, vitamins=3),
        ]


def render_inputs() -> tuple[List[FoodRow], dict[str, float]]:
    st.subheader("Cadastro de Alimentos")
    foods = st.data_editor(
        st.session_state.foods,
        column_config={
            "name": "Alimento",
            "cost": st.column_config.NumberColumn("Custo", format="%.2f"),
            "calories": st.column_config.NumberColumn("Calorias", format="%.0f"),
            "protein": st.column_config.NumberColumn("Proteína", format="%.0f"),
            "carb": st.column_config.NumberColumn("Carboidrato", format="%.0f"),
            "vitamins": st.column_config.NumberColumn("Vitaminas", format="%.0f"),
        },
        width="stretch",
        hide_index=True,
        num_rows="dynamic",
    )
    st.session_state.foods = foods

    st.subheader("Metas Nutricionais")
    cols = st.columns(4)
    goals = {
        "calories": cols[0].number_input("Calorias mínimas", value=2000, step=50.0, min_value=0.0),
        "protein": cols[1].number_input("Proteína mínima", value=60.0, step=5.0, min_value=0.0),
        "carb": cols[2].number_input("Carboidrato mínimo", value=250.0, step=10.0, min_value=0.0),
        "vitamins": cols[3].number_input("Vitaminas mínimas", value=10.0, step=1.0, min_value=0.0),
    }
    return foods, goals


def optimize_diet(foods: List[FoodRow], goals: dict[str, float]) -> dict[str, float] | None:
    if not foods:
        st.error("Adicione ao menos um alimento com todos os campos preenchidos.")
        return None

    if all(value <= 0 for value in goals.values()):
        st.error("Defina metas nutricionais maiores que zero.")
        return None

    problem = pulp.LpProblem("diet", pulp.LpMinimize)
    portions = {food["name"]: pulp.LpVariable(food["name"], lowBound=0) for food in foods}

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
        st.error("Nenhuma solução viável foi encontrada para as restrições.")
        return None

    return {food["name"]: portions[food["name"]].value() for food in foods}


def render_results(solution: dict[str, float], foods: List[FoodRow]) -> None:
    results = [
        {
            "Alimento": name,
            "Porções": amount,
            "Custo": next(food["cost"] for food in foods if food["name"] == name) * amount,
        }
        for name, amount in solution.items()
        if amount and amount > 0
    ]
    st.subheader("Resultados")
    st.dataframe(results, width="stretch", hide_index=True)

    total_cost = sum(row["Custo"] for row in results)
    st.metric(label="Custo total", value=f"R$ {total_cost:,.2f}")


st.set_page_config(page_title="Planejador de Dieta", layout="wide")
st.title("Planejador de Dieta com Restrições Nutricionais")
initialize_foods()

foods, goals = render_inputs()

if st.button("Calcular Dieta Otimizada", type="primary"):
    solution = optimize_diet(foods, goals)
    if solution:
        render_results(solution, foods)
