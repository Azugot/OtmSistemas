"""
Dados de Exemplo para o Sistema de Otimização de Cozinha Industrial

Conjunto de pratos, períodos e custos realistas para demonstração.

Autor: Victor Colen
Data: 18/11/2025
"""

# Suporte para importação relativa e absoluta
try:
    from .model import Dish, Period, ResourceCosts
except ImportError:
    from model import Dish, Period, ResourceCosts


def get_example_dishes():
    """
    Retorna lista de pratos de exemplo com dados realistas.

    Returns:
        Lista de objetos Dish
    """
    dishes = [
        Dish(
            name="Arroz Branco",
            demand=100,
            stove_time=0.5,  # 30 seg por porção
            oven_time=0,
            water_consumption=0.1,  # 100ml
            gas_consumption=0.005,
            electricity_consumption=0,
            prep_time=0.15
        ),
        Dish(
            name="Feijão Preto",
            demand=80,
            stove_time=0.8,  # 48 seg por porção
            oven_time=0,
            water_consumption=0.12,
            gas_consumption=0.006,
            electricity_consumption=0,
            prep_time=0.2
        ),
        Dish(
            name="Frango Grelhado",
            demand=60,
            stove_time=0.3,
            oven_time=0.5,
            water_consumption=0.15,
            gas_consumption=0.003,
            electricity_consumption=0.025,
            prep_time=0.4
        ),
        Dish(
            name="Lasanha à Bolonhesa",
            demand=40,
            stove_time=0.2,
            oven_time=0.7,
            water_consumption=0.18,
            gas_consumption=0.002,
            electricity_consumption=0.035,
            prep_time=0.5
        ),
        Dish(
            name="Salada Verde",
            demand=90,
            stove_time=0,
            oven_time=0,
            water_consumption=0.2,
            gas_consumption=0,
            electricity_consumption=0.001,
            prep_time=0.12
        ),
        Dish(
            name="Purê de Batata",
            demand=50,
            stove_time=0.4,
            oven_time=0,
            water_consumption=0.12,
            gas_consumption=0.004,
            electricity_consumption=0,
            prep_time=0.18
        ),
        Dish(
            name="Bife à Parmegiana",
            demand=30,
            stove_time=0.25,
            oven_time=0.35,
            water_consumption=0.15,
            gas_consumption=0.005,
            electricity_consumption=0.02,
            prep_time=0.55
        ),
        Dish(
            name="Sopa de Legumes",
            demand=70,
            stove_time=0.6,
            oven_time=0,
            water_consumption=0.25,
            gas_consumption=0.005,
            electricity_consumption=0,
            prep_time=0.25
        ),
        Dish(
            name="Macarrão ao Molho",
            demand=85,
            stove_time=0.3,
            oven_time=0,
            water_consumption=0.08,
            gas_consumption=0.003,
            electricity_consumption=0,
            prep_time=0.15
        ),
        Dish(
            name="Torta de Frango",
            demand=35,
            stove_time=0.15,
            oven_time=0.65,
            water_consumption=0.12,
            gas_consumption=0.002,
            electricity_consumption=0.03,
            prep_time=0.45
        ),
        Dish(
            name="Carne Assada",
            demand=45,
            stove_time=0.15,
            oven_time=1.0,
            water_consumption=0.08,
            gas_consumption=0.003,
            electricity_consumption=0.042,
            prep_time=0.32
        ),
        Dish(
            name="Batata Frita",
            demand=55,
            stove_time=0,
            oven_time=0.4,
            water_consumption=0.15,
            gas_consumption=0,
            electricity_consumption=0.018,
            prep_time=0.22
        ),
        Dish(
            name="Farofa",
            demand=65,
            stove_time=0.22,
            oven_time=0,
            water_consumption=0.03,
            gas_consumption=0.002,
            electricity_consumption=0,
            prep_time=0.12
        ),
        Dish(
            name="Pudim de Leite",
            demand=40,
            stove_time=0.3,
            oven_time=0.8,
            water_consumption=0.08,
            gas_consumption=0.003,
            electricity_consumption=0.025,
            prep_time=0.4
        ),
        Dish(
            name="Suco Natural",
            demand=120,
            stove_time=0,
            oven_time=0,
            water_consumption=0.3,  # 300ml
            gas_consumption=0,
            electricity_consumption=0.003,
            prep_time=0.08
        )
    ]

    return dishes


def get_example_periods():
    """
    Retorna lista de períodos de exemplo (3 turnos).

    Returns:
        Lista de objetos Period
    """
    periods = [
        Period(
            name="Manhã (6h-12h)",
            stove_capacity=240,   # 4 horas * 60 min
            oven_capacity=180,    # 3 horas * 60 min
            team_capacity=720     # 2 pessoas * 6h * 60 min
        ),
        Period(
            name="Tarde (12h-18h)",
            stove_capacity=300,   # 5 horas * 60 min
            oven_capacity=240,    # 4 horas * 60 min
            team_capacity=900     # 2.5 pessoas * 6h * 60 min
        ),
        Period(
            name="Noite (18h-22h)",
            stove_capacity=180,   # 3 horas * 60 min (horário reduzido)
            oven_capacity=120,    # 2 horas * 60 min
            team_capacity=480     # 2 pessoas * 4h * 60 min
        )
    ]

    return periods


def get_example_costs():
    """
    Retorna custos unitários de exemplo (valores realistas para Brasil).

    Returns:
        Objeto ResourceCosts
    """
    return ResourceCosts(
        gas_price=4.50,         # R$ por m³
        electricity_price=0.85,  # R$ por kWh
        water_price=0.05        # R$ por litro
    )


def get_small_example():
    """
    Retorna exemplo pequeno para testes rápidos (3 pratos, 2 períodos).
    NOTA: Tempos são por unidade, ajustados para serem viáveis.

    Returns:
        (dishes, periods, costs)
    """
    dishes = [
        Dish(
            name="Arroz",
            demand=50,
            stove_time=0.5,  # 30 segundos por porção
            oven_time=0,
            water_consumption=0.1,  # 100ml por porção
            gas_consumption=0.005,  # 5 litros de gás por porção
            electricity_consumption=0,
            prep_time=0.2  # 12 segundos por porção
        ),
        Dish(
            name="Frango",
            demand=30,
            stove_time=0.3,  # 18 segundos por porção
            oven_time=0.5,  # 30 segundos por porção
            water_consumption=0.15,  # 150ml por porção
            gas_consumption=0.003,
            electricity_consumption=0.02,  # 20Wh por porção
            prep_time=0.4  # 24 segundos por porção
        ),
        Dish(
            name="Salada",
            demand=40,
            stove_time=0,
            oven_time=0,
            water_consumption=0.2,  # 200ml por porção (lavagem)
            gas_consumption=0,
            electricity_consumption=0.001,  # processador
            prep_time=0.15  # 9 segundos por porção
        )
    ]

    periods = [
        Period(
            name="Manhã",
            stove_capacity=300,  # 5 horas
            oven_capacity=200,
            team_capacity=1000  # ~16 horas-pessoa
        ),
        Period(
            name="Tarde",
            stove_capacity=300,
            oven_capacity=200,
            team_capacity=1000
        )
    ]

    costs = ResourceCosts(
        gas_price=4.50,
        electricity_price=0.85,
        water_price=0.05
    )

    return dishes, periods, costs


# Descrições dos pratos para interface
DISH_DESCRIPTIONS = {
    "Arroz Branco": "Arroz branco cozido tradicional",
    "Feijão Preto": "Feijão preto cozido com temperos",
    "Frango Grelhado": "Peito de frango grelhado temperado",
    "Lasanha à Bolonhesa": "Lasanha de carne com molho bolonhesa",
    "Salada Verde": "Mix de folhas verdes frescas",
    "Purê de Batata": "Purê de batata cremoso",
    "Bife à Parmegiana": "Bife empanado com molho e queijo",
    "Sopa de Legumes": "Sopa nutritiva de legumes variados",
    "Macarrão ao Molho": "Macarrão com molho de tomate",
    "Torta de Frango": "Torta assada com recheio de frango",
    "Carne Assada": "Carne bovina assada no forno",
    "Batata Frita": "Batatas fritas crocantes",
    "Farofa": "Farofa tradicional temperada",
    "Pudim de Leite": "Pudim de leite condensado",
    "Suco Natural": "Suco natural de frutas"
}


# Teste
if __name__ == "__main__":
    print("=== Dados de Exemplo ===\n")

    dishes = get_example_dishes()
    print(f"Total de pratos: {len(dishes)}")
    print("\nPratos:")
    for dish in dishes:
        print(f"  - {dish.name}: demanda {dish.demand}")

    periods = get_example_periods()
    print(f"\nTotal de períodos: {len(periods)}")
    print("\nPeríodos:")
    for period in periods:
        print(f"  - {period.name}")
        print(f"    Fogão: {period.stove_capacity} min")
        print(f"    Forno: {period.oven_capacity} min")
        print(f"    Equipe: {period.team_capacity} min-pessoa")

    costs = get_example_costs()
    print("\nCustos:")
    print(f"  Gás: R$ {costs.gas_price}/m³")
    print(f"  Energia: R$ {costs.electricity_price}/kWh")
    print(f"  Água: R$ {costs.water_price}/L")

    print("\n" + "="*50)
    print("\nTeste com exemplo pequeno:")
    small_dishes, small_periods, small_costs = get_small_example()
    print(f"Pratos: {len(small_dishes)}")
    print(f"Períodos: {len(small_periods)}")
