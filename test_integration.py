"""
Teste de Integração Completa
Testa o fluxo completo: dados -> modelo -> simplex -> solução
"""

from src.model import KitchenOptimizer
from src.data_example import get_small_example

print("="*60)
print("TESTE DE INTEGRAÇÃO COMPLETA")
print("="*60)

# Carrega exemplo pequeno
dishes, periods, costs = get_small_example()

print(f"\n📊 Dados do Problema:")
print(f"  - Pratos: {len(dishes)}")
print(f"  - Períodos: {len(periods)}")
print(f"  - Variáveis de decisão: {len(dishes) * len(periods)}")

# Cria otimizador
optimizer = KitchenOptimizer()
optimizer.add_dishes(dishes)
optimizer.add_periods(periods)
optimizer.set_costs(costs)

print(f"\n✅ Otimizador configurado:")
print(f"  - Pratos no modelo: {len(optimizer.dishes)}")
print(f"  - Períodos no modelo: {len(optimizer.periods)}")

# Lista pratos e demandas
print(f"\n🍽️  Pratos e Demandas:")
for dish in optimizer.dishes:
    print(f"  - {dish.name}: {dish.demand} unidades")

# Lista períodos e capacidades
print(f"\n⏰ Períodos e Capacidades:")
for period in optimizer.periods:
    print(f"  - {period.name}:")
    print(f"      Fogão: {period.stove_capacity} min")
    print(f"      Forno: {period.oven_capacity} min")
    print(f"      Equipe: {period.team_capacity} min-pessoa")

# Tenta resolver
print(f"\n🚀 Executando otimização...")
try:
    result = optimizer.solve()

    print(f"\n📋 Resultado:")
    print(f"  - Status: {result['status'].value}")
    print(f"  - Sucesso: {result['success']}")
    print(f"  - Mensagem: {result['message']}")
    print(f"  - Iterações: {result['iterations']}")

    if result['success']:
        print(f"\n✅ OTIMIZAÇÃO BEM-SUCEDIDA!")
        optimizer.print_solution()
    else:
        print(f"\n❌ OTIMIZAÇÃO FALHOU")
        print(f"Motivo: {result['message']}")

        if result['status'].value == 'infeasible':
            print("\n🔍 Diagnóstico:")
            print("O problema está inviável. Possíveis causas:")
            print("  1. Demanda muito alta para as capacidades")
            print("  2. Restrições conflitantes")
            print("  3. Capacidades muito baixas")

except Exception as e:
    print(f"\n❌ ERRO INESPERADO:")
    print(f"  {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("TESTE CONCLUÍDO")
print("="*60)
