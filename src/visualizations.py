"""Plotly visualizations for the kitchen optimizer."""
from __future__ import annotations

import pandas as pd
import plotly.express as px


def plot_resource_consumption(schedule_df: pd.DataFrame):
    if schedule_df.empty:
        return None
    melted = schedule_df.melt(id_vars=["Prato"], var_name="Período", value_name="Quantidade")
    fig = px.bar(melted, x="Prato", y="Quantidade", color="Período", barmode="group")
    fig.update_layout(title="Produção por período")
    return fig


def plot_equipment_utilization(utilization_df: pd.DataFrame):
    if utilization_df.empty:
        return None
    melted = utilization_df.melt(id_vars=["Equipamento"], var_name="Período", value_name="Minutos")
    fig = px.bar(melted, x="Período", y="Minutos", color="Equipamento", barmode="group")
    fig.update_layout(title="Uso de recursos por período")
    return fig


def plot_production_timeline(schedule_df: pd.DataFrame):
    if schedule_df.empty:
        return None
    rows = []
    for _, row in schedule_df.iterrows():
        for period in schedule_df.columns[1:]:
            qty = row[period]
            if qty <= 0:
                continue
            rows.append({"Tarefa": row["Prato"], "Período": period, "Quantidade": qty})
    timeline_df = pd.DataFrame(rows)
    if timeline_df.empty:
        return None
    fig = px.bar(timeline_df, x="Período", y="Quantidade", color="Tarefa", barmode="stack")
    fig.update_layout(title="Cronograma de produção")
    return fig


def generate_summary_metrics(result):
    if not result.breakdown:
        return []
    return [
        {"label": "Custo Total", "value": f"R$ {result.total_cost:,.2f}"},
        {
            "label": "Custo de Gás",
            "value": f"R$ {result.breakdown.get('gas', 0.0):,.2f}",
        },
        {
            "label": "Custo de Energia",
            "value": f"R$ {result.breakdown.get('energy', 0.0):,.2f}",
        },
        {
            "label": "Custo de Água",
            "value": f"R$ {result.breakdown.get('water', 0.0):,.2f}",
        },
    ]
