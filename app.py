from __future__ import annotations

import time
from typing import List

import pandas as pd
import streamlit as st

from src.data_example import EXAMPLE_COSTS, EXAMPLE_DISHES, EXAMPLE_PERIODS
from src.model import Dish, KitchenOptimizer, Period
from src.visualizations import (
    generate_summary_metrics,
    plot_equipment_utilization,
    plot_production_timeline,
    plot_resource_consumption,
)

st.set_page_config(page_title="Otimização de Cozinha Industrial", layout="wide")

PRIMARY = "#1E3A8A"
SECONDARY = "#10B981"
ACCENT = "#F59E0B"
BACKGROUND = "#F3F4F6"
ERROR = "#EF4444"


def _init_state():
    if "dishes" not in st.session_state:
        st.session_state.dishes = pd.DataFrame(
            [dish.__dict__ for dish in EXAMPLE_DISHES]
        )
    if "periods" not in st.session_state:
        st.session_state.periods = pd.DataFrame(
            [period.__dict__ for period in EXAMPLE_PERIODS]
        )
    if "costs" not in st.session_state:
        st.session_state.costs = EXAMPLE_COSTS.copy()


def _sidebar_controls():
    st.sidebar.header("⚙️ Configurações")
    st.sidebar.markdown("Ajuste os custos unitários e carregue um exemplo.")
    gas = st.sidebar.number_input("Preço do gás (R$/m³)", value=float(st.session_state.costs["gas"]))
    energy = st.sidebar.number_input(
        "Preço da energia (R$/kWh)", value=float(st.session_state.costs["energy"])
    )
    water = st.sidebar.number_input("Preço da água (R$/L)", value=float(st.session_state.costs["water"]))
    st.session_state.costs = {"gas": gas, "energy": energy, "water": water}

    if st.sidebar.button("Carregar Exemplo", use_container_width=True):
        st.session_state.dishes = pd.DataFrame([dish.__dict__ for dish in EXAMPLE_DISHES])
        st.session_state.periods = pd.DataFrame([period.__dict__ for period in EXAMPLE_PERIODS])
        st.session_state.costs = EXAMPLE_COSTS.copy()
        st.sidebar.success("Dados de exemplo carregados.")

    if st.sidebar.button("Limpar Dados", use_container_width=True):
        st.session_state.dishes = pd.DataFrame(columns=st.session_state.dishes.columns)
        st.session_state.periods = pd.DataFrame(columns=st.session_state.periods.columns)
        st.sidebar.info("Tabelas limpas.")


@st.cache_data(show_spinner=False)
def _format_styles():
    return {
        "card": f"background-color: white; padding: 16px; border-radius: 8px; border-left: 5px solid {PRIMARY};",
    }


def _validate_dataframe(df: pd.DataFrame, required: List[str]) -> bool:
    if df.empty:
        st.error("Preencha a tabela antes de otimizar.")
        return False
    for col in required:
        if col not in df.columns:
            st.error(f"Coluna ausente: {col}")
            return False
    if df[required].isnull().any().any():
        st.error("Existem valores vazios nas tabelas.")
        return False
    return True


def _build_optimizer(dishes_df: pd.DataFrame, periods_df: pd.DataFrame) -> KitchenOptimizer:
    optimizer = KitchenOptimizer()
    for _, row in dishes_df.iterrows():
        optimizer.add_dish(
            Dish(
                name=str(row["name"]),
                demand=float(row["demand"]),
                stove_time=float(row["stove_time"]),
                oven_time=float(row["oven_time"]),
                water=float(row["water"]),
                gas=float(row["gas"]),
                energy=float(row["energy"]),
                team_time=float(row["team_time"]),
            )
        )
    for _, row in periods_df.iterrows():
        optimizer.add_period(
            Period(
                name=str(row["name"]),
                stove_capacity=float(row["stove_capacity"]),
                oven_capacity=float(row["oven_capacity"]),
                team_capacity=float(row["team_capacity"]),
            )
        )
    optimizer.set_costs(**st.session_state.costs)
    return optimizer


def _render_results(result, dishes_df: pd.DataFrame, periods_df: pd.DataFrame):
    st.subheader("Resultado")
    if result.status != "Ótimo encontrado":
        st.error(result.status)
        return

    styles = _format_styles()
    cols = st.columns(4)
    for col, metric in zip(cols, generate_summary_metrics(result)):
        col.markdown(
            f"""
            <div style="{styles['card']}">
                <div style="color:{PRIMARY}; font-weight:600;">{metric['label']}</div>
                <div style="font-size:24px; color:{ACCENT};">{metric['value']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    periods = periods_df["name"].tolist()
    data = []
    for _, dish in dishes_df.iterrows():
        row = {"Prato": dish["name"]}
        for period in periods:
            row[period] = result.schedule.get((dish["name"], period), 0.0)
        data.append(row)
    schedule_df = pd.DataFrame(data)
    st.dataframe(schedule_df, use_container_width=True)

    utilization_rows = []
    for equipment in ["stove", "oven", "team"]:
        util_row = {"Equipamento": equipment.capitalize()}
        for period in periods:
            util_row[period] = result.utilization[equipment][period]
        utilization_rows.append(util_row)
    utilization_df = pd.DataFrame(utilization_rows)

    col1, col2 = st.columns(2)
    fig1 = plot_resource_consumption(schedule_df)
    fig2 = plot_equipment_utilization(utilization_df)
    if fig1:
        col1.plotly_chart(fig1, use_container_width=True)
    if fig2:
        col2.plotly_chart(fig2, use_container_width=True)

    fig3 = plot_production_timeline(schedule_df)
    if fig3:
        st.plotly_chart(fig3, use_container_width=True)

    csv = schedule_df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Baixar cronograma (CSV)", csv, "cronograma.csv", "text/csv")


def main():
    _init_state()
    _sidebar_controls()

    st.title("🍳 Sistema de Otimização de Cozinha Industrial")
    st.caption("Minimize recursos, maximize eficiência")

    tab_dishes, tab_periods, tab_opt, tab_visuals = st.tabs(
        ["Pratos", "Restrições", "Otimização", "Visualizações"]
    )

    with tab_dishes:
        st.markdown("Cadastre pratos e demandas mínimos.")
        st.session_state.dishes = st.data_editor(
            st.session_state.dishes,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "name": st.column_config.TextColumn("Prato"),
                "demand": st.column_config.NumberColumn("Demanda mínima"),
                "stove_time": st.column_config.NumberColumn("Tempo fogão (min)", step=1),
                "oven_time": st.column_config.NumberColumn("Tempo forno (min)", step=1),
                "water": st.column_config.NumberColumn("Água (L)", step=0.1),
                "gas": st.column_config.NumberColumn("Gás (m³)", step=0.01),
                "energy": st.column_config.NumberColumn("Energia (kWh)", step=0.01),
                "team_time": st.column_config.NumberColumn("Equipe (min)", step=1),
            },
        )

    with tab_periods:
        st.markdown("Defina as capacidades por período.")
        st.session_state.periods = st.data_editor(
            st.session_state.periods,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "name": st.column_config.TextColumn("Período"),
                "stove_capacity": st.column_config.NumberColumn("Capacidade fogão (min)", step=10),
                "oven_capacity": st.column_config.NumberColumn("Capacidade forno (min)", step=10),
                "team_capacity": st.column_config.NumberColumn("Capacidade equipe (min)", step=10),
            },
        )

    with tab_opt:
        st.markdown("Clique para otimizar a produção.")
        if st.button("🚀 Otimizar", use_container_width=True):
            if not _validate_dataframe(st.session_state.dishes, list(st.session_state.dishes.columns)):
                return
            if not _validate_dataframe(st.session_state.periods, list(st.session_state.periods.columns)):
                return
            start = time.time()
            optimizer = _build_optimizer(st.session_state.dishes, st.session_state.periods)
            result = optimizer.solve()
            elapsed = time.time() - start
            st.info(f"Status: {result.status} | Tempo de execução: {elapsed:.2f}s")
            st.session_state.latest_result = result
            _render_results(result, st.session_state.dishes, st.session_state.periods)

    with tab_visuals:
        st.markdown("Visualize rapidamente recursos e cronograma.")
        if "latest_result" in st.session_state:
            _render_results(st.session_state.latest_result, st.session_state.dishes, st.session_state.periods)
        else:
            st.info("Execute uma otimização para ver os gráficos.")


if __name__ == "__main__":
    main()
