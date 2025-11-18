"""
Visualizações para o Sistema de Otimização de Cozinha Industrial

Funções para gerar gráficos interativos com Plotly.

Autor: Victor Colen
Data: 18/11/2025
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List
import numpy as np


# Paleta de cores do projeto
COLORS = {
    'primary': '#1E3A8A',      # Azul escuro
    'secondary': '#10B981',    # Verde esmeralda
    'accent': '#F59E0B',       # Laranja
    'error': '#EF4444',        # Vermelho
    'water': '#3B82F6',        # Azul água
    'gas': '#F59E0B',          # Laranja gás
    'electricity': '#EAB308',  # Amarelo energia
    'stove': '#EF4444',        # Vermelho fogão
    'oven': '#F97316',         # Laranja forno
    'team': '#8B5CF6'          # Roxo equipe
}


def plot_resource_consumption(solution: Dict) -> go.Figure:
    """
    Gráfico de barras mostrando consumo de recursos por prato.

    Args:
        solution: Dicionário com a solução interpretada

    Returns:
        Figura Plotly
    """
    # Extrai dados
    dishes = []
    water_consumption = []
    gas_consumption = []
    electricity_consumption = []

    for dish_name, data in solution['production_schedule'].items():
        total_qty = data['total']
        if total_qty > 0.01:  # Ignora pratos não produzidos
            dishes.append(dish_name)

    # Precisamos recalcular o consumo por prato a partir da solução
    # Por simplicidade, vamos criar um gráfico de custos por categoria

    costs = solution['costs']

    # Gráfico de pizza de custos
    fig = go.Figure(data=[go.Pie(
        labels=['Água', 'Gás', 'Energia Elétrica'],
        values=[costs['water'], costs['gas'], costs['electricity']],
        marker=dict(colors=[COLORS['water'], COLORS['gas'], COLORS['electricity']]),
        hole=0.4,
        textinfo='label+percent+value',
        texttemplate='<b>%{label}</b><br>R$ %{value:.2f}<br>%{percent}',
        hovertemplate='<b>%{label}</b><br>R$ %{value:.2f}<br>%{percent}<extra></extra>'
    )])

    fig.update_layout(
        title={
            'text': '💰 Distribuição de Custos por Recurso',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': COLORS['primary']}
        },
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )

    return fig


def plot_production_timeline(solution: Dict) -> go.Figure:
    """
    Gráfico de barras empilhadas mostrando produção por período.

    Args:
        solution: Dicionário com a solução interpretada

    Returns:
        Figura Plotly
    """
    # Prepara dados
    periods = []
    dishes_data = {}

    # Coleta todos os períodos
    for dish_name, data in solution['production_schedule'].items():
        for period_name in data['periods'].keys():
            if period_name not in periods:
                periods.append(period_name)

    # Coleta quantidades por prato e período
    for dish_name, data in solution['production_schedule'].items():
        quantities = []
        for period in periods:
            qty = data['periods'].get(period, 0)
            quantities.append(qty)

        # Só adiciona se houver produção
        if sum(quantities) > 0.01:
            dishes_data[dish_name] = quantities

    # Cria gráfico de barras empilhadas
    fig = go.Figure()

    colors_palette = px.colors.qualitative.Set3

    for idx, (dish_name, quantities) in enumerate(dishes_data.items()):
        fig.add_trace(go.Bar(
            name=dish_name,
            x=periods,
            y=quantities,
            marker_color=colors_palette[idx % len(colors_palette)],
            text=[f'{q:.1f}' if q > 0.1 else '' for q in quantities],
            textposition='inside',
            hovertemplate='<b>%{fullData.name}</b><br>Período: %{x}<br>Quantidade: %{y:.1f}<extra></extra>'
        ))

    fig.update_layout(
        title={
            'text': '📅 Cronograma de Produção por Período',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': COLORS['primary']}
        },
        xaxis_title='Período',
        yaxis_title='Quantidade Produzida',
        barmode='stack',
        height=500,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        ),
        hovermode='x unified'
    )

    return fig


def plot_equipment_utilization(solution: Dict) -> go.Figure:
    """
    Gráfico de barras mostrando utilização de equipamentos por período.

    Args:
        solution: Dicionário com a solução interpretada

    Returns:
        Figura Plotly
    """
    periods = list(solution['equipment_utilization'].keys())

    stove_util = [solution['equipment_utilization'][p]['stove']['utilization_pct'] for p in periods]
    oven_util = [solution['equipment_utilization'][p]['oven']['utilization_pct'] for p in periods]
    team_util = [solution['equipment_utilization'][p]['team']['utilization_pct'] for p in periods]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name='Fogão',
        x=periods,
        y=stove_util,
        marker_color=COLORS['stove'],
        text=[f'{u:.1f}%' for u in stove_util],
        textposition='outside',
        hovertemplate='<b>Fogão</b><br>Período: %{x}<br>Utilização: %{y:.1f}%<extra></extra>'
    ))

    fig.add_trace(go.Bar(
        name='Forno',
        x=periods,
        y=oven_util,
        marker_color=COLORS['oven'],
        text=[f'{u:.1f}%' for u in oven_util],
        textposition='outside',
        hovertemplate='<b>Forno</b><br>Período: %{x}<br>Utilização: %{y:.1f}%<extra></extra>'
    ))

    fig.add_trace(go.Bar(
        name='Equipe',
        x=periods,
        y=team_util,
        marker_color=COLORS['team'],
        text=[f'{u:.1f}%' for u in team_util],
        textposition='outside',
        hovertemplate='<b>Equipe</b><br>Período: %{x}<br>Utilização: %{y:.1f}%<extra></extra>'
    ))

    fig.update_layout(
        title={
            'text': '⚙️  Utilização de Equipamentos e Equipe',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': COLORS['primary']}
        },
        xaxis_title='Período',
        yaxis_title='Utilização (%)',
        yaxis=dict(range=[0, 110]),
        barmode='group',
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        hovermode='x unified'
    )

    # Adiciona linha de referência em 100%
    fig.add_hline(y=100, line_dash="dash", line_color="red",
                  annotation_text="Capacidade Máxima",
                  annotation_position="right")

    return fig


def plot_production_table(solution: Dict) -> pd.DataFrame:
    """
    Cria tabela formatada com cronograma de produção.

    Args:
        solution: Dicionário com a solução interpretada

    Returns:
        DataFrame do pandas
    """
    data = []

    for dish_name, dish_data in solution['production_schedule'].items():
        row = {'Prato': dish_name}

        for period_name, qty in dish_data['periods'].items():
            row[period_name] = f"{qty:.1f}"

        row['Total'] = f"{dish_data['total']:.1f}"

        # Só adiciona se houver produção
        if dish_data['total'] > 0.01:
            data.append(row)

    df = pd.DataFrame(data)
    return df


def plot_resource_consumption_detailed(solution: Dict, dishes_list: List) -> go.Figure:
    """
    Gráfico de barras agrupadas mostrando consumo detalhado de cada recurso por prato.

    Args:
        solution: Dicionário com a solução interpretada
        dishes_list: Lista de objetos Dish (para obter atributos)

    Returns:
        Figura Plotly
    """
    # Mapeia pratos para seus dados
    dish_map = {dish.name: dish for dish in dishes_list}

    dishes = []
    water = []
    gas = []
    electricity = []

    for dish_name, data in solution['production_schedule'].items():
        total_qty = data['total']
        if total_qty > 0.01 and dish_name in dish_map:
            dish = dish_map[dish_name]
            dishes.append(dish_name)
            water.append(dish.water_consumption * total_qty)
            gas.append(dish.gas_consumption * total_qty)
            electricity.append(dish.electricity_consumption * total_qty)

    # Cria subplots
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=('💧 Água (L)', '🔥 Gás (m³)', '⚡ Energia (kWh)'),
        horizontal_spacing=0.12
    )

    # Água
    fig.add_trace(
        go.Bar(name='Água', x=dishes, y=water, marker_color=COLORS['water'],
               showlegend=False,
               hovertemplate='<b>%{x}</b><br>Água: %{y:.2f} L<extra></extra>'),
        row=1, col=1
    )

    # Gás
    fig.add_trace(
        go.Bar(name='Gás', x=dishes, y=gas, marker_color=COLORS['gas'],
               showlegend=False,
               hovertemplate='<b>%{x}</b><br>Gás: %{y:.2f} m³<extra></extra>'),
        row=1, col=2
    )

    # Energia
    fig.add_trace(
        go.Bar(name='Energia', x=dishes, y=electricity, marker_color=COLORS['electricity'],
               showlegend=False,
               hovertemplate='<b>%{x}</b><br>Energia: %{y:.2f} kWh<extra></extra>'),
        row=1, col=3
    )

    fig.update_xaxes(tickangle=45)
    fig.update_layout(
        title={
            'text': '📊 Consumo Detalhado de Recursos por Prato',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': COLORS['primary']}
        },
        height=500,
        showlegend=False
    )

    return fig


def generate_summary_metrics(solution: Dict, optimization_result: Dict) -> Dict:
    """
    Gera métricas resumidas para exibição.

    Args:
        solution: Dicionário com a solução interpretada
        optimization_result: Resultado bruto da otimização

    Returns:
        Dicionário com métricas formatadas
    """
    costs = solution['costs']
    resources = solution['resource_consumption']

    metrics = {
        'total_cost': f"R$ {costs['total']:.2f}",
        'water_cost': f"R$ {costs['water']:.2f}",
        'gas_cost': f"R$ {costs['gas']:.2f}",
        'electricity_cost': f"R$ {costs['electricity']:.2f}",
        'total_water': f"{resources['water_liters']:.2f} L",
        'total_gas': f"{resources['gas_m3']:.2f} m³",
        'total_electricity': f"{resources['electricity_kwh']:.2f} kWh",
        'iterations': optimization_result['iterations'],
        'status': optimization_result['status'].value
    }

    return metrics


def create_gantt_chart(solution: Dict) -> go.Figure:
    """
    Cria um gráfico de Gantt simplificado para visualizar o cronograma.

    Args:
        solution: Dicionário com a solução interpretada

    Returns:
        Figura Plotly
    """
    periods = []
    for dish_data in solution['production_schedule'].values():
        for period_name in dish_data['periods'].keys():
            if period_name not in periods:
                periods.append(period_name)

    # Mapeia períodos para números (para timeline)
    period_mapping = {name: idx for idx, name in enumerate(periods)}

    tasks = []

    for dish_name, data in solution['production_schedule'].items():
        for period_name, qty in data['periods'].items():
            if qty > 0.01:
                tasks.append({
                    'Task': dish_name,
                    'Start': period_mapping[period_name],
                    'Finish': period_mapping[period_name] + 0.9,
                    'Quantity': qty,
                    'Period': period_name
                })

    if not tasks:
        # Retorna gráfico vazio se não houver tarefas
        return go.Figure()

    df = pd.DataFrame(tasks)

    fig = px.timeline(
        df,
        x_start='Start',
        x_end='Finish',
        y='Task',
        color='Quantity',
        hover_data=['Period', 'Quantity'],
        color_continuous_scale='Viridis'
    )

    fig.update_xaxes(
        ticktext=periods,
        tickvals=[period_mapping[p] + 0.45 for p in periods],
        title='Período'
    )

    fig.update_layout(
        title={
            'text': '📅 Timeline de Produção',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': COLORS['primary']}
        },
        height=max(400, len(df['Task'].unique()) * 40),
        xaxis_title='Período',
        yaxis_title='Prato',
        coloraxis_colorbar=dict(title="Quantidade")
    )

    return fig


# Teste das visualizações
if __name__ == "__main__":
    # Dados de exemplo para teste
    mock_solution = {
        'production_schedule': {
            'Arroz': {'periods': {'Manhã': 50, 'Tarde': 30, 'Noite': 20}, 'total': 100},
            'Feijão': {'periods': {'Manhã': 40, 'Tarde': 40, 'Noite': 0}, 'total': 80},
            'Frango': {'periods': {'Manhã': 20, 'Tarde': 25, 'Noite': 15}, 'total': 60}
        },
        'resource_consumption': {
            'water_liters': 1500,
            'gas_m3': 25,
            'electricity_kwh': 75
        },
        'costs': {
            'water': 75.0,
            'gas': 112.50,
            'electricity': 63.75,
            'total': 251.25
        },
        'equipment_utilization': {
            'Manhã': {
                'stove': {'used': 200, 'capacity': 240, 'utilization_pct': 83.3},
                'oven': {'used': 150, 'capacity': 180, 'utilization_pct': 83.3},
                'team': {'used': 600, 'capacity': 720, 'utilization_pct': 83.3}
            },
            'Tarde': {
                'stove': {'used': 250, 'capacity': 300, 'utilization_pct': 83.3},
                'oven': {'used': 200, 'capacity': 240, 'utilization_pct': 83.3},
                'team': {'used': 750, 'capacity': 900, 'utilization_pct': 83.3}
            },
            'Noite': {
                'stove': {'used': 120, 'capacity': 180, 'utilization_pct': 66.7},
                'oven': {'used': 80, 'capacity': 120, 'utilization_pct': 66.7},
                'team': {'used': 320, 'capacity': 480, 'utilization_pct': 66.7}
            }
        }
    }

    print("Testando visualizações...")
    print("\nGerando gráfico de custos...")
    fig1 = plot_resource_consumption(mock_solution)
    print("✓ Gráfico de custos criado")

    print("\nGerando cronograma de produção...")
    fig2 = plot_production_timeline(mock_solution)
    print("✓ Cronograma criado")

    print("\nGerando utilização de equipamentos...")
    fig3 = plot_equipment_utilization(mock_solution)
    print("✓ Gráfico de utilização criado")

    print("\nGerando tabela de produção...")
    df = plot_production_table(mock_solution)
    print("✓ Tabela criada:")
    print(df)

    print("\nTodas visualizações funcionando corretamente!")
