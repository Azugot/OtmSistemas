# PRD - Sistema de Otimização de Cozinha Industrial

## 📖 Visão Geral

Sistema de otimização para cozinhas industriais que utiliza **Programação Linear** para minimizar o consumo de recursos (energia elétrica, gás e água) durante o preparo de refeições, respeitando as restrições operacionais de equipamentos, turnos de funcionários e demanda do cardápio.

### Objetivo Principal
Minimizar os custos operacionais através da otimização do uso de recursos naturais e energéticos, mantendo a qualidade e quantidade necessária de refeições.

---

## 🎯 Objetivos Específicos

1. **Redução de Custos**: Minimizar consumo de água, energia elétrica e gás natural
2. **Eficiência Operacional**: Otimizar o uso de equipamentos (fogões e fornos)
3. **Gestão de Pessoal**: Respeitar turnos e capacidade da equipe
4. **Planejamento**: Fornecer cronograma de produção otimizado
5. **Transparência**: Visualizar impacto de decisões em tempo real

---

## 📐 Modelo Matemático

### Variáveis de Decisão

- **x_{i,t}**: Quantidade do prato `i` a ser preparado no período `t`
  - `i ∈ {1, 2, ..., n}` (pratos do cardápio)
  - `t ∈ {1, 2, ..., T}` (períodos de tempo, ex: manhã, tarde, noite)

### Parâmetros do Modelo

Para cada prato `i`:
- **c_gas_i**: Consumo de gás (m³) por unidade
- **c_elet_i**: Consumo de energia elétrica (kWh) por unidade
- **c_agua_i**: Consumo de água (litros) por unidade
- **t_fogao_i**: Tempo de uso do fogão (minutos) por unidade
- **t_forno_i**: Tempo de uso do forno (minutos) por unidade
- **t_prep_i**: Tempo de preparação pela equipe (minutos-pessoa) por unidade
- **D_i**: Demanda mínima do prato `i` (quantidade total necessária)

Para cada período `t`:
- **CAP_fogao_t**: Capacidade do fogão no período `t` (minutos disponíveis)
- **CAP_forno_t**: Capacidade do forno no período `t` (minutos disponíveis)
- **CAP_equipe_t**: Capacidade da equipe no período `t` (minutos-pessoa disponíveis)

Custos unitários:
- **p_gas**: Preço do gás (R$/m³)
- **p_elet**: Preço da energia (R$/kWh)
- **p_agua**: Preço da água (R$/litro)

### Função Objetivo

**Minimizar:**
```
Z = Σ(i,t) [ p_gas × c_gas_i × x_{i,t}
           + p_elet × c_elet_i × x_{i,t}
           + p_agua × c_agua_i × x_{i,t} ]
```

Ou de forma equivalente:
```
MIN: Σ(i,t) [ (p_gas × c_gas_i + p_elet × c_elet_i + p_agua × c_agua_i) × x_{i,t} ]
```

### Restrições

#### 1. Atendimento da Demanda
```
Σ(t=1 até T) x_{i,t} >= D_i     ∀ i
```
A soma das quantidades do prato `i` em todos os períodos deve atender a demanda.

#### 2. Capacidade do Fogão
```
Σ(i) t_fogao_i × x_{i,t} <= CAP_fogao_t     ∀ t
```
O tempo total de uso do fogão não pode exceder a capacidade disponível em cada período.

#### 3. Capacidade do Forno
```
Σ(i) t_forno_i × x_{i,t} <= CAP_forno_t     ∀ t
```
O tempo total de uso do forno não pode exceder a capacidade disponível em cada período.

#### 4. Capacidade da Equipe
```
Σ(i) t_prep_i × x_{i,t} <= CAP_equipe_t     ∀ t
```
O tempo total de trabalho não pode exceder a capacidade da equipe disponível em cada período.

#### 5. Limite de Água Diário (Opcional)
```
Σ(i,t) c_agua_i × x_{i,t} <= AGUA_max
```
Se houver limitação de abastecimento de água.

#### 6. Não-negatividade
```
x_{i,t} >= 0     ∀ i, t
```

### Forma Padrão para o Simplex

Para resolver pelo método Simplex, o problema deve ser convertido para a forma padrão:

**Minimizar:** c^T × x

**Sujeito a:**
- A × x = b
- x >= 0

Onde:
- Desigualdades (<=) são convertidas adicionando variáveis de folga
- Desigualdades (>=) são convertidas subtraindo variáveis de excesso e adicionando artificiais
- A função objetivo de minimização pode ser convertida em maximização multiplicando por -1

---

## 🏗️ Arquitetura da Solução

### Estrutura de Diretórios
```
/Trabalho-final
├── PRD.md                      # Este documento
├── README.md                   # Instruções de uso
├── requirements.txt            # Dependências Python
├── app.py                      # Interface Streamlit
└── src/
    ├── __init__.py
    ├── simplex.py              # Implementação do algoritmo Simplex
    ├── model.py                # Modelagem do problema de otimização
    ├── visualizations.py       # Funções de visualização (Plotly)
    └── data_example.py         # Dados de exemplo pré-carregados
```

### Componentes Principais

#### 1. **Simplex Solver** (`src/simplex.py`)
- Classe `SimplexSolver`
- Método `solve(c, A, b, signs)`: Resolve problema de PL
- Método `_to_standard_form()`: Converte para forma padrão
- Método `_phase_one()`: Encontra solução básica viável inicial
- Método `_phase_two()`: Otimiza a função objetivo
- Tratamento de casos especiais: ótimo, ilimitado, inviável

#### 2. **Model Builder** (`src/model.py`)
- Classe `Dish`: Representa um prato com seus atributos
- Classe `Period`: Representa um período de tempo
- Classe `KitchenOptimizer`: Monta e resolve o problema
  - Método `add_dish()`: Adiciona prato ao modelo
  - Método `add_period()`: Adiciona período
  - Método `set_costs()`: Define custos unitários
  - Método `build_problem()`: Constrói matrizes A, b, c
  - Método `solve()`: Chama o Simplex e interpreta resultados

#### 3. **Visualizations** (`src/visualizations.py`)
- `plot_resource_consumption()`: Gráficos de consumo por prato/período
- `plot_production_timeline()`: Cronograma de produção (Gantt)
- `plot_equipment_utilization()`: Taxa de ocupação de equipamentos
- `generate_summary_metrics()`: Métricas totais e economia

#### 4. **Interface Streamlit** (`app.py`)
- **Header**: Título e descrição
- **Sidebar**: Configuração de custos e períodos
- **Tab 1 - Cadastro de Pratos**: Formulários dinâmicos
- **Tab 2 - Restrições**: Capacidades de equipamentos e equipe
- **Tab 3 - Otimização**: Botão resolver + resultados
- **Tab 4 - Visualizações**: Gráficos interativos

---

## ✨ Requisitos Funcionais

### RF01 - Cadastro de Pratos
- ✅ Usuário pode adicionar pratos com nome, demanda e atributos
- ✅ Atributos: tempo de fogão, forno, água, gás, energia, tempo de equipe
- ✅ Validação de dados (valores positivos, campos obrigatórios)
- ✅ Edição e remoção de pratos cadastrados

### RF02 - Definição de Períodos
- ✅ Usuário define períodos de planejamento (ex: 3 períodos/dia)
- ✅ Para cada período: capacidade de fogão, forno e equipe
- ✅ Opção de copiar capacidades entre períodos

### RF03 - Configuração de Custos
- ✅ Definir preços unitários: gás (R$/m³), energia (R$/kWh), água (R$/L)
- ✅ Valores padrão sugeridos

### RF04 - Otimização
- ✅ Botão "Otimizar" executa o algoritmo Simplex
- ✅ Exibe status: processando, sucesso, inviável, ilimitado
- ✅ Tempo de execução exibido

### RF05 - Resultados Detalhados
- ✅ Tabela com quantidade de cada prato por período
- ✅ Custo total minimizado (breakdown: gás, energia, água)
- ✅ Taxa de utilização de equipamentos

### RF06 - Visualizações
- ✅ Gráfico de barras: consumo de recursos por prato
- ✅ Gráfico de barras empilhadas: distribuição por período
- ✅ Timeline de produção (tipo Gantt)
- ✅ Indicadores visuais de economia

### RF07 - Dados de Exemplo
- ✅ Botão "Carregar Exemplo" preenche com dados fictícios realistas
- ✅ 10-15 pratos variados (arroz, feijão, carne, saladas, etc.)

### RF08 - Exportação
- ✅ Baixar resultados em formato CSV
- ✅ Exportar gráficos como PNG

---

## 🔧 Requisitos Não-Funcionais

### RNF01 - Performance
- Algoritmo Simplex deve resolver problemas com até 50 variáveis em < 5 segundos
- Interface deve ser responsiva (atualização < 1 segundo)

### RNF02 - Usabilidade
- Interface intuitiva, sem necessidade de treinamento técnico
- Feedback visual claro em todas as operações
- Mensagens de erro amigáveis

### RNF03 - Robustez
- Tratamento de casos especiais (problema inviável, ilimitado)
- Validação de entrada para evitar erros numéricos
- Mensagens explicativas quando não há solução

### RNF04 - Manutenibilidade
- Código documentado (docstrings)
- Separação clara entre lógica e interface
- Testes unitários para o Simplex

### RNF05 - Estética
- Design moderno com paleta de cores harmônica
- Uso de ícones e emojis para facilitar navegação
- Layout responsivo (funciona em diferentes resoluções)

---

## 📊 Dados de Exemplo

### Pratos (10 exemplos)

| # | Prato | Demanda | Fogão (min) | Forno (min) | Água (L) | Gás (m³) | Energia (kWh) | Equipe (min) |
|---|-------|---------|-------------|-------------|----------|----------|---------------|--------------|
| 1 | Arroz Branco | 100 | 30 | 0 | 5 | 0.3 | 0 | 10 |
| 2 | Feijão Preto | 80 | 50 | 0 | 8 | 0.4 | 0 | 15 |
| 3 | Frango Grelhado | 60 | 20 | 30 | 10 | 0.2 | 1.5 | 25 |
| 4 | Lasanha | 40 | 15 | 45 | 12 | 0.1 | 2.0 | 30 |
| 5 | Salada Verde | 90 | 0 | 0 | 15 | 0 | 0.1 | 10 |
| 6 | Purê de Batata | 50 | 25 | 0 | 8 | 0.25 | 0 | 12 |
| 7 | Bife à Parmegiana | 30 | 15 | 20 | 10 | 0.3 | 1.2 | 35 |
| 8 | Sopa de Legumes | 70 | 40 | 0 | 20 | 0.35 | 0 | 18 |
| 9 | Macarrão ao Molho | 85 | 20 | 0 | 6 | 0.2 | 0 | 12 |
| 10 | Torta de Frango | 35 | 10 | 40 | 8 | 0.15 | 1.8 | 28 |

### Períodos (3 turnos)

| Período | Fogão (min) | Forno (min) | Equipe (min-pessoa) |
|---------|-------------|-------------|---------------------|
| Manhã (6h-12h) | 240 | 180 | 720 (2 pessoas × 6h) |
| Tarde (12h-18h) | 300 | 240 | 900 (2.5 pessoas × 6h) |
| Noite (18h-22h) | 180 | 120 | 480 (2 pessoas × 4h) |

### Custos Unitários

- Gás: R$ 4,50/m³
- Energia: R$ 0,85/kWh
- Água: R$ 0,05/L

---

## 🎨 Especificação da Interface

### Paleta de Cores
- **Primária**: #1E3A8A (azul escuro)
- **Secundária**: #10B981 (verde esmeralda)
- **Acento**: #F59E0B (laranja)
- **Fundo**: #F3F4F6 (cinza claro)
- **Erro**: #EF4444 (vermelho)

### Layout

```
┌─────────────────────────────────────────────────────────┐
│  🍳 Sistema de Otimização de Cozinha Industrial         │
│  Minimize recursos, maximize eficiência                 │
├─────────────────┬───────────────────────────────────────┤
│   SIDEBAR       │   CONTEÚDO PRINCIPAL                  │
│                 │                                       │
│ 💰 Custos       │  [Tab: Pratos] [Tab: Restrições]     │
│  Gas: R$/m³     │  [Tab: Otimizar] [Tab: Resultados]   │
│  Energia: R$/kWh│                                       │
│  Água: R$/L     │  ┌─────────────────────────────────┐ │
│                 │  │  Formulário de Cadastro         │ │
│ ⏰ Períodos     │  │  Nome: [___________]            │ │
│  [3] turnos     │  │  Demanda: [____]                │ │
│                 │  │  Tempo fogão: [____] min        │ │
│ 📋 Ações        │  │  ...                            │ │
│  [Carregar      │  │  [+ Adicionar Prato]            │ │
│   Exemplo]      │  └─────────────────────────────────┘ │
│  [Limpar Dados] │                                       │
│                 │  📊 Gráficos e Visualizações          │
│                 │                                       │
└─────────────────┴───────────────────────────────────────┘
```

### Componentes Visuais

1. **Cards**: Métricas principais com ícones
2. **Dataframes Interativos**: Tabelas editáveis do Streamlit
3. **Gráficos Plotly**: Interativos, com zoom e hover
4. **Expanders**: Para seções colapsáveis
5. **Progress Bar**: Durante otimização
6. **Alerts**: Mensagens de sucesso/erro com cores

---

## 🧪 Casos de Uso

### Caso de Uso 1: Otimização Básica
1. Usuário clica em "Carregar Exemplo"
2. Sistema preenche 10 pratos e 3 períodos
3. Usuário clica em "Otimizar"
4. Sistema exibe: custo total R$ 1.234,56, cronograma, gráficos

### Caso de Uso 2: Problema Inviável
1. Usuário define demanda muito alta (500 unidades)
2. Capacidades insuficientes (1 hora de fogão total)
3. Sistema detecta inviabilidade
4. Exibe: "Problema inviável - aumente capacidades ou reduza demanda"

### Caso de Uso 3: Análise de Sensibilidade
1. Usuário resolve com custo de energia R$ 0,85/kWh
2. Altera para R$ 1,50/kWh
3. Resolve novamente
4. Compara resultados: pratos com forno reduzidos

---

## 📚 Referências Técnicas

### Algoritmo Simplex
- Método Tableau
- Regra de Bland para evitar ciclagem
- Método das Duas Fases para problemas com restrições >=

### Bibliotecas Utilizadas
- **Streamlit**: Interface web
- **NumPy**: Operações matriciais
- **Plotly**: Visualizações interativas
- **Pandas**: Manipulação de dados

### Complexidade
- Worst case: O(2^n) (exponencial)
- Average case: Polynomial na prática
- Espaço: O(m × n) para tableau

---

## 📝 Critérios de Aceitação

- ✅ Algoritmo Simplex implementado sem bibliotecas externas de PL
- ✅ Resolve problema de 10+ pratos e 3 períodos corretamente
- ✅ Interface moderna e intuitiva
- ✅ Visualizações claras e informativas
- ✅ Código documentado e organizado
- ✅ Tratamento de erros adequado
- ✅ Tempo de resposta < 5 segundos

---

## 🚀 Próximos Passos (Futuro)

1. **Restrições Nutricionais**: Mínimo de calorias, proteínas
2. **Custos Variáveis**: Preço de ingredientes por período (demanda)
3. **Otimização Multi-objetivo**: Pareto entre custo e tempo
4. **Planejamento Semanal**: Estender para 7 dias
5. **Machine Learning**: Prever demanda futura
6. **Integração**: API para sistemas ERP

---

**Versão:** 1.0
**Data:** 18/11/2025
**Autor:** Victor Colen
