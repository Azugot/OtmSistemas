"""
Modelagem do Problema de Otimização de Cozinha Industrial

Classes para representar pratos, períodos e construir o modelo de programação linear.

Autor: Victor Colen
Data: 18/11/2025
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# Suporte para importação relativa e absoluta
try:
    from .simplex import solve_linear_program, OptimizationStatus
except ImportError:
    from simplex import solve_linear_program, OptimizationStatus


@dataclass
class Dish:
    """
    Representa um prato do cardápio.

    Attributes:
        name: Nome do prato
        demand: Demanda total (quantidade mínima necessária)
        stove_time: Tempo de uso do fogão (minutos por unidade)
        oven_time: Tempo de uso do forno (minutos por unidade)
        water_consumption: Consumo de água (litros por unidade)
        gas_consumption: Consumo de gás (m³ por unidade)
        electricity_consumption: Consumo de energia elétrica (kWh por unidade)
        prep_time: Tempo de preparação da equipe (minutos-pessoa por unidade)
    """
    name: str
    demand: float
    stove_time: float = 0.0
    oven_time: float = 0.0
    water_consumption: float = 0.0
    gas_consumption: float = 0.0
    electricity_consumption: float = 0.0
    prep_time: float = 0.0

    def __post_init__(self):
        """Validação dos dados"""
        if self.demand < 0:
            raise ValueError(f"Demanda do prato '{self.name}' não pode ser negativa")
        if any(x < 0 for x in [self.stove_time, self.oven_time, self.water_consumption,
                                self.gas_consumption, self.electricity_consumption, self.prep_time]):
            raise ValueError(f"Atributos do prato '{self.name}' não podem ser negativos")


@dataclass
class Period:
    """
    Representa um período de tempo (turno).

    Attributes:
        name: Nome do período (ex: "Manhã", "Tarde")
        stove_capacity: Capacidade do fogão (minutos disponíveis)
        oven_capacity: Capacidade do forno (minutos disponíveis)
        team_capacity: Capacidade da equipe (minutos-pessoa disponíveis)
    """
    name: str
    stove_capacity: float
    oven_capacity: float
    team_capacity: float

    def __post_init__(self):
        """Validação dos dados"""
        if any(x < 0 for x in [self.stove_capacity, self.oven_capacity, self.team_capacity]):
            raise ValueError(f"Capacidades do período '{self.name}' não podem ser negativas")


@dataclass
class ResourceCosts:
    """
    Custos unitários dos recursos.

    Attributes:
        gas_price: Preço do gás (R$/m³)
        electricity_price: Preço da energia elétrica (R$/kWh)
        water_price: Preço da água (R$/litro)
    """
    gas_price: float = 4.50
    electricity_price: float = 0.85
    water_price: float = 0.05


class KitchenOptimizer:
    """
    Otimizador de cozinha industrial usando Programação Linear.

    Constrói e resolve o problema de otimização para minimizar custos
    de recursos enquanto atende a demanda e respeita restrições.
    """

    def __init__(self):
        """Inicializa o otimizador"""
        self.dishes: List[Dish] = []
        self.periods: List[Period] = []
        self.costs = ResourceCosts()
        self.solution = None
        self.optimization_result = None

    def add_dish(self, dish: Dish):
        """Adiciona um prato ao modelo"""
        self.dishes.append(dish)

    def add_dishes(self, dishes: List[Dish]):
        """Adiciona múltiplos pratos ao modelo"""
        self.dishes.extend(dishes)

    def add_period(self, period: Period):
        """Adiciona um período ao modelo"""
        self.periods.append(period)

    def add_periods(self, periods: List[Period]):
        """Adiciona múltiplos períodos ao modelo"""
        self.periods.extend(periods)

    def set_costs(self, costs: ResourceCosts):
        """Define os custos unitários dos recursos"""
        self.costs = costs

    def build_problem(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, List[str]]:
        """
        Constrói as matrizes do problema de programação linear.

        Variáveis de decisão:
            x_{i,t} = quantidade do prato i no período t
            Índice: i * num_periods + t

        Returns:
            (c, A, b, signs)
            c: Vetor de custos (função objetivo)
            A: Matriz de restrições
            b: Vetor de lados direitos
            signs: Lista de sinais das restrições
        """
        if not self.dishes:
            raise ValueError("Nenhum prato adicionado ao modelo")
        if not self.periods:
            raise ValueError("Nenhum período adicionado ao modelo")

        num_dishes = len(self.dishes)
        num_periods = len(self.periods)
        num_vars = num_dishes * num_periods

        # === Função Objetivo ===
        # Minimizar: Σ(i,t) custo_total_i * x_{i,t}
        c = np.zeros(num_vars)

        for i, dish in enumerate(self.dishes):
            # Custo total por unidade do prato
            total_cost_per_unit = (
                dish.gas_consumption * self.costs.gas_price +
                dish.electricity_consumption * self.costs.electricity_price +
                dish.water_consumption * self.costs.water_price
            )

            for t in range(num_periods):
                var_idx = i * num_periods + t
                c[var_idx] = total_cost_per_unit

        # === Restrições ===
        constraints = []
        signs = []

        # 1. Restrições de Demanda: Σ(t) x_{i,t} >= D_i
        for i, dish in enumerate(self.dishes):
            constraint = np.zeros(num_vars)
            for t in range(num_periods):
                var_idx = i * num_periods + t
                constraint[var_idx] = 1.0

            constraints.append(constraint)
            signs.append('>=')

        # 2. Restrições de Capacidade do Fogão: Σ(i) stove_time_i * x_{i,t} <= CAP_stove_t
        for t, period in enumerate(self.periods):
            constraint = np.zeros(num_vars)
            for i, dish in enumerate(self.dishes):
                var_idx = i * num_periods + t
                constraint[var_idx] = dish.stove_time

            constraints.append(constraint)
            signs.append('<=')

        # 3. Restrições de Capacidade do Forno: Σ(i) oven_time_i * x_{i,t} <= CAP_oven_t
        for t, period in enumerate(self.periods):
            constraint = np.zeros(num_vars)
            for i, dish in enumerate(self.dishes):
                var_idx = i * num_periods + t
                constraint[var_idx] = dish.oven_time

            constraints.append(constraint)
            signs.append('<=')

        # 4. Restrições de Capacidade da Equipe: Σ(i) prep_time_i * x_{i,t} <= CAP_team_t
        for t, period in enumerate(self.periods):
            constraint = np.zeros(num_vars)
            for i, dish in enumerate(self.dishes):
                var_idx = i * num_periods + t
                constraint[var_idx] = dish.prep_time

            constraints.append(constraint)
            signs.append('<=')

        # Monta matriz A e vetor b
        A = np.array(constraints)
        b = np.array(
            # Demandas
            [dish.demand for dish in self.dishes] +
            # Capacidades de fogão
            [period.stove_capacity for period in self.periods] +
            # Capacidades de forno
            [period.oven_capacity for period in self.periods] +
            # Capacidades de equipe
            [period.team_capacity for period in self.periods]
        )

        return c, A, b, signs

    def solve(self) -> Dict:
        """
        Resolve o problema de otimização.

        Returns:
            Dicionário com resultados da otimização
        """
        # Constrói o problema
        c, A, b, signs = self.build_problem()

        # Resolve usando Simplex
        result = solve_linear_program(c, A, b, signs, minimize=True)

        # Armazena resultado
        self.optimization_result = result

        if result['success']:
            # Interpreta solução
            self.solution = self._interpret_solution(result['x'])

        return result

    def _interpret_solution(self, x: np.ndarray) -> Dict:
        """
        Interpreta a solução do Simplex e organiza em formato legível.

        Args:
            x: Vetor de variáveis de decisão

        Returns:
            Dicionário com informações organizadas
        """
        num_periods = len(self.periods)
        num_dishes = len(self.dishes)

        # Organiza produção por prato e período
        production_schedule = {}

        for i, dish in enumerate(self.dishes):
            production_schedule[dish.name] = {
                'periods': {},
                'total': 0.0
            }

            for t, period in enumerate(self.periods):
                var_idx = i * num_periods + t
                quantity = x[var_idx]

                production_schedule[dish.name]['periods'][period.name] = quantity
                production_schedule[dish.name]['total'] += quantity

        # Calcula consumo total de recursos
        total_water = 0.0
        total_gas = 0.0
        total_electricity = 0.0

        for i, dish in enumerate(self.dishes):
            total_qty = production_schedule[dish.name]['total']
            total_water += total_qty * dish.water_consumption
            total_gas += total_qty * dish.gas_consumption
            total_electricity += total_qty * dish.electricity_consumption

        # Calcula utilização de equipamentos por período
        equipment_utilization = {}

        for t, period in enumerate(self.periods):
            stove_used = 0.0
            oven_used = 0.0
            team_used = 0.0

            for i, dish in enumerate(self.dishes):
                var_idx = i * num_periods + t
                quantity = x[var_idx]

                stove_used += quantity * dish.stove_time
                oven_used += quantity * dish.oven_time
                team_used += quantity * dish.prep_time

            equipment_utilization[period.name] = {
                'stove': {
                    'used': stove_used,
                    'capacity': period.stove_capacity,
                    'utilization_pct': (stove_used / period.stove_capacity * 100) if period.stove_capacity > 0 else 0
                },
                'oven': {
                    'used': oven_used,
                    'capacity': period.oven_capacity,
                    'utilization_pct': (oven_used / period.oven_capacity * 100) if period.oven_capacity > 0 else 0
                },
                'team': {
                    'used': team_used,
                    'capacity': period.team_capacity,
                    'utilization_pct': (team_used / period.team_capacity * 100) if period.team_capacity > 0 else 0
                }
            }

        # Calcula custos detalhados
        cost_breakdown = {
            'water': total_water * self.costs.water_price,
            'gas': total_gas * self.costs.gas_price,
            'electricity': total_electricity * self.costs.electricity_price,
            'total': (
                total_water * self.costs.water_price +
                total_gas * self.costs.gas_price +
                total_electricity * self.costs.electricity_price
            )
        }

        return {
            'production_schedule': production_schedule,
            'resource_consumption': {
                'water_liters': total_water,
                'gas_m3': total_gas,
                'electricity_kwh': total_electricity
            },
            'costs': cost_breakdown,
            'equipment_utilization': equipment_utilization
        }

    def get_solution(self) -> Optional[Dict]:
        """Retorna a solução interpretada"""
        return self.solution

    def get_optimization_result(self) -> Optional[Dict]:
        """Retorna o resultado bruto da otimização"""
        return self.optimization_result

    def print_solution(self):
        """Imprime a solução de forma legível"""
        if self.solution is None:
            print("Nenhuma solução disponível. Execute solve() primeiro.")
            return

        print("\n" + "="*60)
        print("SOLUÇÃO DE OTIMIZAÇÃO - COZINHA INDUSTRIAL")
        print("="*60)

        # Cronograma de Produção
        print("\n📋 CRONOGRAMA DE PRODUÇÃO")
        print("-" * 60)
        for dish_name, data in self.solution['production_schedule'].items():
            print(f"\n{dish_name}:")
            for period_name, qty in data['periods'].items():
                if qty > 0.01:  # Ignora quantidades muito pequenas
                    print(f"  {period_name}: {qty:.1f} unidades")
            print(f"  TOTAL: {data['total']:.1f} unidades")

        # Consumo de Recursos
        print("\n💧 CONSUMO DE RECURSOS")
        print("-" * 60)
        res = self.solution['resource_consumption']
        print(f"Água: {res['water_liters']:.2f} litros")
        print(f"Gás: {res['gas_m3']:.2f} m³")
        print(f"Energia Elétrica: {res['electricity_kwh']:.2f} kWh")

        # Custos
        print("\n💰 CUSTOS")
        print("-" * 60)
        costs = self.solution['costs']
        print(f"Água: R$ {costs['water']:.2f}")
        print(f"Gás: R$ {costs['gas']:.2f}")
        print(f"Energia: R$ {costs['electricity']:.2f}")
        print(f"{'─'*60}")
        print(f"TOTAL: R$ {costs['total']:.2f}")

        # Utilização de Equipamentos
        print("\n⚙️  UTILIZAÇÃO DE EQUIPAMENTOS")
        print("-" * 60)
        for period_name, util in self.solution['equipment_utilization'].items():
            print(f"\n{period_name}:")
            print(f"  Fogão: {util['stove']['used']:.1f}/{util['stove']['capacity']:.1f} min "
                  f"({util['stove']['utilization_pct']:.1f}%)")
            print(f"  Forno: {util['oven']['used']:.1f}/{util['oven']['capacity']:.1f} min "
                  f"({util['oven']['utilization_pct']:.1f}%)")
            print(f"  Equipe: {util['team']['used']:.1f}/{util['team']['capacity']:.1f} min "
                  f"({util['team']['utilization_pct']:.1f}%)")

        print("\n" + "="*60 + "\n")


# Teste do modelo
if __name__ == "__main__":
    print("=== Teste do Modelo de Otimização ===\n")

    # Cria otimizador
    optimizer = KitchenOptimizer()

    # Define custos
    optimizer.set_costs(ResourceCosts(
        gas_price=4.50,
        electricity_price=0.85,
        water_price=0.05
    ))

    # Adiciona pratos (exemplo simplificado)
    dishes = [
        Dish(
            name="Arroz Branco",
            demand=100,
            stove_time=30,
            oven_time=0,
            water_consumption=5,
            gas_consumption=0.3,
            electricity_consumption=0,
            prep_time=10
        ),
        Dish(
            name="Frango Grelhado",
            demand=60,
            stove_time=20,
            oven_time=30,
            water_consumption=10,
            gas_consumption=0.2,
            electricity_consumption=1.5,
            prep_time=25
        ),
        Dish(
            name="Salada Verde",
            demand=90,
            stove_time=0,
            oven_time=0,
            water_consumption=15,
            gas_consumption=0,
            electricity_consumption=0.1,
            prep_time=10
        )
    ]

    optimizer.add_dishes(dishes)

    # Adiciona períodos
    periods = [
        Period(name="Manhã", stove_capacity=240, oven_capacity=180, team_capacity=720),
        Period(name="Tarde", stove_capacity=300, oven_capacity=240, team_capacity=900),
        Period(name="Noite", stove_capacity=180, oven_capacity=120, team_capacity=480)
    ]

    optimizer.add_periods(periods)

    # Resolve
    print("Resolvendo problema de otimização...\n")
    result = optimizer.solve()

    print(f"Status: {result['status'].value}")
    print(f"Sucesso: {result['success']}")
    print(f"Mensagem: {result['message']}")
    print(f"Iterações: {result['iterations']}")

    if result['success']:
        optimizer.print_solution()
