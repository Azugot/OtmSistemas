"""
Interface Streamlit - Sistema de Otimização de Cozinha Industrial

Aplicação web moderna para otimização de recursos em cozinhas industriais.

Autor: Victor Colen
Data: 18/11/2025
"""

import streamlit as st
import pandas as pd
import time
from src.model import Dish, Period, ResourceCosts, KitchenOptimizer
from src.data_example import (
    get_example_dishes, get_example_periods, get_example_costs,
    get_small_example, DISH_DESCRIPTIONS
)
from src.visualizations import (
    plot_resource_consumption, plot_production_timeline,
    plot_equipment_utilization, plot_production_table,
    plot_resource_consumption_detailed, generate_summary_metrics
)
from src.simplex import OptimizationStatus

# Configuração da página
st.set_page_config(
    page_title="Otimização de Cozinha Industrial",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado para design moderno
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1E3A8A;
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #1E3A8A 0%, #10B981 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sub-header {
        text-align: center;
        color: #6B7280;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #10B981;
    }
    .stButton>button {
        width: 100%;
        background-color: #10B981;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        border: none;
    }
    .stButton>button:hover {
        background-color: #059669;
    }
    </style>
""", unsafe_allow_html=True)

# Inicialização do estado da sessão
if 'optimizer' not in st.session_state:
    st.session_state.optimizer = KitchenOptimizer()
    st.session_state.dishes_df = pd.DataFrame()
    st.session_state.periods_df = pd.DataFrame()
    st.session_state.solution = None
    st.session_state.optimization_result = None

# Header
st.markdown('<h1 class="main-header">🍳 Sistema de Otimização de Cozinha Industrial</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Minimize recursos, maximize eficiência usando Programação Linear</p>', unsafe_allow_html=True)

# =====================
# SIDEBAR
# =====================
with st.sidebar:
    st.markdown("### 🍳 OptiChef")
    st.caption("Sistema de Otimização")
    st.markdown("---")

    st.header("💰 Custos Unitários")

    gas_price = st.number_input(
        "Gás (R$/m³)",
        min_value=0.0,
        value=4.50,
        step=0.10,
        format="%.2f",
        help="Preço do gás natural por metro cúbico"
    )

    electricity_price = st.number_input(
        "Energia Elétrica (R$/kWh)",
        min_value=0.0,
        value=0.85,
        step=0.05,
        format="%.2f",
        help="Tarifa de energia elétrica por kilowatt-hora"
    )

    water_price = st.number_input(
        "Água (R$/litro)",
        min_value=0.0,
        value=0.05,
        step=0.01,
        format="%.3f",
        help="Tarifa de água por litro"
    )

    st.session_state.optimizer.set_costs(ResourceCosts(
        gas_price=gas_price,
        electricity_price=electricity_price,
        water_price=water_price
    ))

    st.markdown("---")

    st.header("📋 Ações Rápidas")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📥 Carregar Exemplo Completo", use_container_width=True):
            # Carrega dados de exemplo
            st.session_state.optimizer = KitchenOptimizer()
            st.session_state.optimizer.add_dishes(get_example_dishes())
            st.session_state.optimizer.add_periods(get_example_periods())
            st.session_state.optimizer.set_costs(get_example_costs())

            # Cria DataFrames para exibição
            st.session_state.dishes_df = pd.DataFrame([
                {
                    'Prato': d.name,
                    'Demanda': d.demand,
                    'Fogão (min)': d.stove_time,
                    'Forno (min)': d.oven_time,
                    'Água (L)': d.water_consumption,
                    'Gás (m³)': d.gas_consumption,
                    'Energia (kWh)': d.electricity_consumption,
                    'Equipe (min)': d.prep_time
                }
                for d in get_example_dishes()
            ])

            st.session_state.periods_df = pd.DataFrame([
                {
                    'Período': p.name,
                    'Fogão (min)': p.stove_capacity,
                    'Forno (min)': p.oven_capacity,
                    'Equipe (min-pessoa)': p.team_capacity
                }
                for p in get_example_periods()
            ])

            st.success("✅ Exemplo completo carregado com 15 pratos e 3 períodos!")
            st.rerun()

    with col2:
        if st.button("🧪 Carregar Exemplo Simples", use_container_width=True):
            # Carrega exemplo pequeno
            dishes, periods, costs = get_small_example()

            st.session_state.optimizer = KitchenOptimizer()
            st.session_state.optimizer.add_dishes(dishes)
            st.session_state.optimizer.add_periods(periods)
            st.session_state.optimizer.set_costs(costs)

            st.session_state.dishes_df = pd.DataFrame([
                {
                    'Prato': d.name,
                    'Demanda': d.demand,
                    'Fogão (min)': d.stove_time,
                    'Forno (min)': d.oven_time,
                    'Água (L)': d.water_consumption,
                    'Gás (m³)': d.gas_consumption,
                    'Energia (kWh)': d.electricity_consumption,
                    'Equipe (min)': d.prep_time
                }
                for d in dishes
            ])

            st.session_state.periods_df = pd.DataFrame([
                {
                    'Período': p.name,
                    'Fogão (min)': p.stove_capacity,
                    'Forno (min)': p.oven_capacity,
                    'Equipe (min-pessoa)': p.team_capacity
                }
                for p in periods
            ])

            st.success("✅ Exemplo simples carregado com 3 pratos e 2 períodos!")
            st.rerun()

    if st.button("🗑️ Limpar Tudo", type="secondary", use_container_width=True):
        st.session_state.optimizer = KitchenOptimizer()
        st.session_state.optimizer.set_costs(ResourceCosts(
            gas_price=gas_price,
            electricity_price=electricity_price,
            water_price=water_price
        ))
        st.session_state.dishes_df = pd.DataFrame()
        st.session_state.periods_df = pd.DataFrame()
        st.session_state.solution = None
        st.session_state.optimization_result = None
        st.success("✅ Dados limpos!")
        st.rerun()

    st.markdown("---")

    st.caption("📘 Trabalho de Programação Linear")
    st.caption("🎓 Sistemas Operacionais - PUC")
    st.caption("👨‍💻 Victor Colen")

# =====================
# TABS PRINCIPAIS
# =====================
tab1, tab2, tab3, tab4 = st.tabs([
    "🍽️ Cadastro de Pratos",
    "⚙️ Restrições e Capacidades",
    "🚀 Otimizar",
    "📊 Resultados"
])

# =====================
# TAB 1: CADASTRO DE PRATOS
# =====================
with tab1:
    st.header("🍽️ Cadastro de Pratos do Cardápio")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Adicionar Novo Prato")

        with st.form("add_dish_form", clear_on_submit=True):
            col_a, col_b = st.columns(2)

            with col_a:
                dish_name = st.text_input("Nome do Prato", placeholder="Ex: Arroz Branco")
                demand = st.number_input("Demanda (unidades)", min_value=0, value=100, step=5)
                stove_time = st.number_input("Tempo de Fogão (min)", min_value=0.0, value=0.0, step=5.0)
                oven_time = st.number_input("Tempo de Forno (min)", min_value=0.0, value=0.0, step=5.0)

            with col_b:
                water = st.number_input("Água (litros)", min_value=0.0, value=0.0, step=1.0)
                gas = st.number_input("Gás (m³)", min_value=0.0, value=0.0, step=0.1, format="%.2f")
                electricity = st.number_input("Energia (kWh)", min_value=0.0, value=0.0, step=0.1, format="%.2f")
                prep_time = st.number_input("Tempo Equipe (min-pessoa)", min_value=0.0, value=0.0, step=5.0)

            submitted = st.form_submit_button("➕ Adicionar Prato", use_container_width=True)

            if submitted and dish_name:
                try:
                    new_dish = Dish(
                        name=dish_name,
                        demand=demand,
                        stove_time=stove_time,
                        oven_time=oven_time,
                        water_consumption=water,
                        gas_consumption=gas,
                        electricity_consumption=electricity,
                        prep_time=prep_time
                    )

                    st.session_state.optimizer.add_dish(new_dish)

                    # Atualiza DataFrame
                    new_row = pd.DataFrame([{
                        'Prato': dish_name,
                        'Demanda': demand,
                        'Fogão (min)': stove_time,
                        'Forno (min)': oven_time,
                        'Água (L)': water,
                        'Gás (m³)': gas,
                        'Energia (kWh)': electricity,
                        'Equipe (min)': prep_time
                    }])

                    if st.session_state.dishes_df.empty:
                        st.session_state.dishes_df = new_row
                    else:
                        st.session_state.dishes_df = pd.concat([st.session_state.dishes_df, new_row], ignore_index=True)

                    st.success(f"✅ Prato '{dish_name}' adicionado!")
                    st.rerun()

                except ValueError as e:
                    st.error(f"❌ Erro: {e}")

    with col2:
        st.subheader("📝 Dicas")
        st.info("""
        **Tempo de Fogão/Forno**: minutos necessários por unidade

        **Água**: litros consumidos (preparo + lavagem)

        **Gás**: metros cúbicos por unidade

        **Energia**: kWh por unidade

        **Tempo Equipe**: minutos-pessoa de trabalho
        """)

    st.markdown("---")

    st.subheader("📋 Pratos Cadastrados")

    if not st.session_state.dishes_df.empty:
        st.dataframe(st.session_state.dishes_df, use_container_width=True, hide_index=True)
        st.caption(f"Total de pratos: {len(st.session_state.dishes_df)}")
    else:
        st.warning("⚠️ Nenhum prato cadastrado. Use o formulário acima ou carregue um exemplo na barra lateral.")

# =====================
# TAB 2: RESTRIÇÕES
# =====================
with tab2:
    st.header("⚙️ Definição de Períodos e Capacidades")

    st.info("📌 Defina os turnos de trabalho e as capacidades de equipamentos para cada período.")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Adicionar Novo Período")

        with st.form("add_period_form", clear_on_submit=True):
            period_name = st.text_input("Nome do Período", placeholder="Ex: Manhã (6h-12h)")

            col_a, col_b, col_c = st.columns(3)

            with col_a:
                stove_cap = st.number_input("Capacidade Fogão (min)", min_value=0, value=240, step=30)

            with col_b:
                oven_cap = st.number_input("Capacidade Forno (min)", min_value=0, value=180, step=30)

            with col_c:
                team_cap = st.number_input("Capacidade Equipe (min-pessoa)", min_value=0, value=720, step=60)

            submitted_period = st.form_submit_button("➕ Adicionar Período", use_container_width=True)

            if submitted_period and period_name:
                try:
                    new_period = Period(
                        name=period_name,
                        stove_capacity=stove_cap,
                        oven_capacity=oven_cap,
                        team_capacity=team_cap
                    )

                    st.session_state.optimizer.add_period(new_period)

                    # Atualiza DataFrame
                    new_row = pd.DataFrame([{
                        'Período': period_name,
                        'Fogão (min)': stove_cap,
                        'Forno (min)': oven_cap,
                        'Equipe (min-pessoa)': team_cap
                    }])

                    if st.session_state.periods_df.empty:
                        st.session_state.periods_df = new_row
                    else:
                        st.session_state.periods_df = pd.concat([st.session_state.periods_df, new_row], ignore_index=True)

                    st.success(f"✅ Período '{period_name}' adicionado!")
                    st.rerun()

                except ValueError as e:
                    st.error(f"❌ Erro: {e}")

    with col2:
        st.subheader("💡 Exemplos")
        st.info("""
        **Manhã (6h-12h)**:
        - Fogão: 240 min
        - Forno: 180 min
        - Equipe: 720 min-pessoa

        **Tarde (12h-18h)**:
        - Fogão: 300 min
        - Forno: 240 min
        - Equipe: 900 min-pessoa
        """)

    st.markdown("---")

    st.subheader("📋 Períodos Cadastrados")

    if not st.session_state.periods_df.empty:
        st.dataframe(st.session_state.periods_df, use_container_width=True, hide_index=True)
        st.caption(f"Total de períodos: {len(st.session_state.periods_df)}")
    else:
        st.warning("⚠️ Nenhum período cadastrado. Use o formulário acima ou carregue um exemplo na barra lateral.")

# =====================
# TAB 3: OTIMIZAR
# =====================
with tab3:
    st.header("🚀 Executar Otimização")

    # Verifica se há dados suficientes
    has_dishes = len(st.session_state.optimizer.dishes) > 0
    has_periods = len(st.session_state.optimizer.periods) > 0

    if has_dishes and has_periods:
        st.success("✅ Sistema pronto para otimizar!")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("🍽️ Pratos", len(st.session_state.optimizer.dishes))

        with col2:
            st.metric("⏰ Períodos", len(st.session_state.optimizer.periods))

        with col3:
            total_vars = len(st.session_state.optimizer.dishes) * len(st.session_state.optimizer.periods)
            st.metric("📊 Variáveis", total_vars)

        st.markdown("---")

        st.subheader("🎯 Função Objetivo")
        st.latex(r"\min \sum_{i,t} (c_{gas} \cdot gas_i + c_{elet} \cdot elet_i + c_{agua} \cdot agua_i) \cdot x_{i,t}")

        st.markdown("**Onde:**")
        st.markdown(f"- **c_gas** = R$ {gas_price:.2f}/m³")
        st.markdown(f"- **c_elet** = R$ {electricity_price:.2f}/kWh")
        st.markdown(f"- **c_agua** = R$ {water_price:.3f}/L")

        st.markdown("---")

        if st.button("🚀 OTIMIZAR AGORA", type="primary", use_container_width=True):
            with st.spinner("⏳ Executando algoritmo Simplex..."):
                start_time = time.time()

                try:
                    result = st.session_state.optimizer.solve()
                    elapsed_time = time.time() - start_time

                    st.session_state.optimization_result = result
                    st.session_state.solution = st.session_state.optimizer.get_solution()

                    if result['success']:
                        st.success(f"✅ **Otimização concluída com sucesso!**")
                        st.info(f"⏱️ Tempo de execução: {elapsed_time:.3f} segundos | Iterações: {result['iterations']}")

                        # Preview dos resultados
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric("💰 Custo Total", f"R$ {st.session_state.solution['costs']['total']:.2f}")

                        with col2:
                            st.metric("💧 Água Total", f"{st.session_state.solution['resource_consumption']['water_liters']:.1f} L")

                        with col3:
                            st.metric("⚡ Energia Total", f"{st.session_state.solution['resource_consumption']['electricity_kwh']:.1f} kWh")

                        st.balloons()
                        st.info("📊 Vá para a aba **Resultados** para visualizar detalhes completos!")

                    else:
                        if result['status'] == OptimizationStatus.INFEASIBLE:
                            st.error("❌ **Problema Inviável**")
                            st.warning("""
                            O problema não possui solução viável. Possíveis causas:
                            - Demanda muito alta em relação às capacidades
                            - Capacidades de equipamentos insuficientes
                            - Conflito entre restrições

                            **Sugestões**:
                            - Aumente as capacidades dos períodos
                            - Reduza a demanda dos pratos
                            - Adicione mais períodos de produção
                            """)

                        elif result['status'] == OptimizationStatus.UNBOUNDED:
                            st.error("❌ **Problema Ilimitado**")
                            st.warning("A função objetivo pode diminuir infinitamente. Verifique a modelagem.")

                        else:
                            st.error(f"❌ Erro durante otimização: {result['message']}")

                except Exception as e:
                    st.error(f"❌ Erro inesperado: {str(e)}")
                    st.exception(e)

    else:
        st.warning("⚠️ **Sistema não está pronto para otimizar**")

        if not has_dishes:
            st.error("❌ Nenhum prato cadastrado. Vá para a aba **Cadastro de Pratos**.")

        if not has_periods:
            st.error("❌ Nenhum período cadastrado. Vá para a aba **Restrições e Capacidades**.")

        st.info("💡 **Dica**: Use os botões na barra lateral para carregar exemplos prontos!")

# =====================
# TAB 4: RESULTADOS
# =====================
with tab4:
    st.header("📊 Resultados da Otimização")

    if st.session_state.solution is not None:
        solution = st.session_state.solution
        result = st.session_state.optimization_result

        # Métricas principais
        st.subheader("💰 Resumo Financeiro")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "💰 Custo Total",
                f"R$ {solution['costs']['total']:.2f}",
                delta=None,
                delta_color="inverse"
            )

        with col2:
            st.metric(
                "💧 Custo Água",
                f"R$ {solution['costs']['water']:.2f}",
                delta=f"{solution['costs']['water']/solution['costs']['total']*100:.1f}%"
            )

        with col3:
            st.metric(
                "🔥 Custo Gás",
                f"R$ {solution['costs']['gas']:.2f}",
                delta=f"{solution['costs']['gas']/solution['costs']['total']*100:.1f}%"
            )

        with col4:
            st.metric(
                "⚡ Custo Energia",
                f"R$ {solution['costs']['electricity']:.2f}",
                delta=f"{solution['costs']['electricity']/solution['costs']['total']*100:.1f}%"
            )

        st.markdown("---")

        # Gráfico de distribuição de custos
        st.subheader("💰 Distribuição de Custos")
        fig_costs = plot_resource_consumption(solution)
        st.plotly_chart(fig_costs, use_container_width=True)

        st.markdown("---")

        # Cronograma de Produção
        st.subheader("📅 Cronograma de Produção")
        fig_timeline = plot_production_timeline(solution)
        st.plotly_chart(fig_timeline, use_container_width=True)

        st.markdown("---")

        # Tabela de produção
        st.subheader("📋 Tabela de Produção Detalhada")
        prod_table = plot_production_table(solution)
        st.dataframe(prod_table, use_container_width=True, hide_index=True)

        st.markdown("---")

        # Utilização de equipamentos
        st.subheader("⚙️  Utilização de Equipamentos")
        fig_equipment = plot_equipment_utilization(solution)
        st.plotly_chart(fig_equipment, use_container_width=True)

        # Alerta se houver superutilização
        for period, util in solution['equipment_utilization'].items():
            if util['stove']['utilization_pct'] > 100 or util['oven']['utilization_pct'] > 100 or util['team']['utilization_pct'] > 100:
                st.error(f"⚠️ Atenção: Capacidade excedida no período **{period}**!")

        st.markdown("---")

        # Consumo detalhado de recursos
        if len(st.session_state.optimizer.dishes) > 0:
            st.subheader("📊 Consumo Detalhado por Prato")
            fig_detailed = plot_resource_consumption_detailed(solution, st.session_state.optimizer.dishes)
            st.plotly_chart(fig_detailed, use_container_width=True)

        st.markdown("---")

        # Exportar resultados
        st.subheader("💾 Exportar Resultados")

        col1, col2 = st.columns(2)

        with col1:
            csv = prod_table.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Baixar Cronograma (CSV)",
                data=csv,
                file_name="cronograma_producao.csv",
                mime="text/csv",
                use_container_width=True
            )

        with col2:
            # Cria resumo em texto
            summary_text = f"""
            RELATÓRIO DE OTIMIZAÇÃO - COZINHA INDUSTRIAL
            ============================================

            CUSTOS:
            - Custo Total: R$ {solution['costs']['total']:.2f}
            - Água: R$ {solution['costs']['water']:.2f}
            - Gás: R$ {solution['costs']['gas']:.2f}
            - Energia: R$ {solution['costs']['electricity']:.2f}

            RECURSOS CONSUMIDOS:
            - Água: {solution['resource_consumption']['water_liters']:.2f} litros
            - Gás: {solution['resource_consumption']['gas_m3']:.2f} m³
            - Energia: {solution['resource_consumption']['electricity_kwh']:.2f} kWh

            OTIMIZAÇÃO:
            - Status: {result['status'].value}
            - Iterações: {result['iterations']}
            """

            st.download_button(
                label="📄 Baixar Relatório (TXT)",
                data=summary_text,
                file_name="relatorio_otimizacao.txt",
                mime="text/plain",
                use_container_width=True
            )

    else:
        st.info("ℹ️ Nenhum resultado disponível ainda.")
        st.markdown("""
        Para visualizar os resultados:
        1. Cadastre pratos na aba **Cadastro de Pratos**
        2. Defina períodos na aba **Restrições e Capacidades**
        3. Execute a otimização na aba **Otimizar**

        Ou use os botões na barra lateral para carregar exemplos prontos! 🚀
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6B7280; padding: 2rem 0;'>
    <p>🍳 <strong>Sistema de Otimização de Cozinha Industrial</strong></p>
    <p>Desenvolvido com ❤️ usando Programação Linear (Algoritmo Simplex implementado do zero)</p>
    <p>📚 Trabalho de Sistemas Operacionais | 🎓 PUC | 👨‍💻 Victor Colen</p>
</div>
""", unsafe_allow_html=True)
