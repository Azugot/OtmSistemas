# 🍳 Sistema de Otimização de Cozinha Industrial

Sistema web para otimização de recursos em cozinhas industriais usando **Programação Linear**. Minimiza o consumo de água, energia elétrica e gás durante o preparo de refeições, respeitando restrições operacionais.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Características](#-características)
- [Instalação](#-instalação)
- [Como Usar](#-como-usar)
- [Modelo Matemático](#-modelo-matemático)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Tecnologias](#-tecnologias)
- [Exemplos](#-exemplos)
- [Contribuindo](#-contribuindo)
- [Autor](#-autor)

---

## 🎯 Visão Geral

Este projeto foi desenvolvido como trabalho da disciplina de **Sistemas Operacionais** na **PUC**. A aplicação utiliza o **Algoritmo Simplex implementado do zero** (sem bibliotecas de otimização externas) para resolver problemas de Programação Linear.

### Problema Resolvido

Dada uma cozinha industrial com:
- **N pratos** no cardápio (cada um com demanda mínima)
- **T períodos** de tempo (turnos de trabalho)
- **Recursos limitados**: fogões, fornos, água, gás, energia, equipe

**Objetivo**: Determinar quantas unidades de cada prato preparar em cada período para **minimizar o custo total** de recursos.

---

## ✨ Características

### 🧮 Algoritmo Simplex do Zero
- Implementação completa sem bibliotecas de PL externas
- Método das Duas Fases para problemas com restrições `>=` e `=`
- Detecção de casos: ótimo, ilimitado, inviável
- Regra de Bland para evitar ciclagem

### 🎨 Interface Moderna
- Design responsivo e intuitivo com **Streamlit**
- Formulários interativos para cadastro de pratos e períodos
- Visualizações dinâmicas com **Plotly**
- Suporte a exemplos pré-carregados

### 📊 Visualizações Interativas
- **Gráfico de Pizza**: Distribuição de custos (água, gás, energia)
- **Gráfico de Barras Empilhadas**: Cronograma de produção por período
- **Gráfico de Barras Agrupadas**: Utilização de equipamentos
- **Tabelas Detalhadas**: Cronograma completo de produção

### 💾 Exportação de Resultados
- Baixar cronograma em **CSV**
- Baixar relatório em **TXT**

---

## 🚀 Instalação

### Pré-requisitos

- **Python 3.8 ou superior**
- **pip** (gerenciador de pacotes Python)

### Passo a Passo

1. **Clone o repositório** (ou descompacte o arquivo ZIP):

```bash
cd "Trabalho-final"
```

2. **Crie um ambiente virtual** (recomendado):

```bash
python -m venv venv

# Ativação no macOS/Linux:
source venv/bin/activate

# Ativação no Windows:
venv\Scripts\activate
```

3. **Instale as dependências**:

```bash
pip install -r requirements.txt
```

4. **Execute a aplicação**:

```bash
streamlit run app.py
```

5. **Acesse no navegador**:

A aplicação abrirá automaticamente em `http://localhost:8501`

---

## 📖 Como Usar

### Método 1: Carregar Exemplo Pronto (Recomendado)

1. Na **barra lateral**, clique em **"📥 Carregar Exemplo Completo"**
2. Vá para a aba **"🚀 Otimizar"**
3. Clique em **"🚀 OTIMIZAR AGORA"**
4. Visualize os resultados na aba **"📊 Resultados"**

### Método 2: Cadastro Manual

#### Passo 1: Cadastrar Pratos

1. Vá para a aba **"🍽️ Cadastro de Pratos"**
2. Preencha o formulário:
   - Nome do prato
   - Demanda (quantidade mínima necessária)
   - Tempo de fogão e forno (minutos por unidade)
   - Consumo de água, gás e energia por unidade
   - Tempo de preparação da equipe
3. Clique em **"➕ Adicionar Prato"**

#### Passo 2: Definir Períodos

1. Vá para a aba **"⚙️ Restrições e Capacidades"**
2. Preencha o formulário:
   - Nome do período (ex: "Manhã 6h-12h")
   - Capacidade do fogão (minutos disponíveis)
   - Capacidade do forno (minutos disponíveis)
   - Capacidade da equipe (minutos-pessoa disponíveis)
3. Clique em **"➕ Adicionar Período"**

#### Passo 3: Configurar Custos

Na **barra lateral**, ajuste os custos unitários:
- Gás (R$/m³)
- Energia Elétrica (R$/kWh)
- Água (R$/litro)

#### Passo 4: Otimizar

1. Vá para a aba **"🚀 Otimizar"**
2. Clique em **"🚀 OTIMIZAR AGORA"**
3. Aguarde o processamento

#### Passo 5: Visualizar Resultados

1. Vá para a aba **"📊 Resultados"**
2. Analise:
   - Custos totais e por recurso
   - Cronograma de produção
   - Utilização de equipamentos
   - Consumo detalhado por prato
3. Exporte os resultados em CSV ou TXT

---

## 📐 Modelo Matemático

### Variáveis de Decisão

- **x_{i,t}**: Quantidade do prato `i` a ser preparado no período `t`

### Função Objetivo

**Minimizar:**

```
Z = Σ(i,t) [ (p_gas × c_gas_i + p_elet × c_elet_i + p_agua × c_agua_i) × x_{i,t} ]
```

Onde:
- `p_gas`, `p_elet`, `p_agua`: Preços unitários dos recursos
- `c_gas_i`, `c_elet_i`, `c_agua_i`: Consumo do prato `i` por unidade

### Restrições

#### 1. Atendimento da Demanda
```
Σ(t) x_{i,t} >= D_i     ∀ prato i
```

#### 2. Capacidade do Fogão
```
Σ(i) t_fogao_i × x_{i,t} <= CAP_fogao_t     ∀ período t
```

#### 3. Capacidade do Forno
```
Σ(i) t_forno_i × x_{i,t} <= CAP_forno_t     ∀ período t
```

#### 4. Capacidade da Equipe
```
Σ(i) t_prep_i × x_{i,t} <= CAP_equipe_t     ∀ período t
```

#### 5. Não-negatividade
```
x_{i,t} >= 0     ∀ i, t
```

---

## 📁 Estrutura do Projeto

```
Trabalho-final/
├── PRD.md                      # Product Requirements Document
├── README.md                   # Este arquivo
├── requirements.txt            # Dependências Python
├── app.py                      # Interface Streamlit (ponto de entrada)
└── src/
    ├── __init__.py
    ├── simplex.py              # Algoritmo Simplex implementado do zero
    ├── model.py                # Modelagem do problema (classes Dish, Period, KitchenOptimizer)
    ├── visualizations.py       # Funções de visualização com Plotly
    └── data_example.py         # Dados de exemplo pré-carregados
```

### Descrição dos Módulos

#### `src/simplex.py`
- Classe `SimplexSolver`: Implementação completa do algoritmo Simplex
- Método das Duas Fases para encontrar solução viável inicial
- Função `solve_linear_program()`: Interface simplificada

#### `src/model.py`
- Classe `Dish`: Representa um prato com todos os atributos
- Classe `Period`: Representa um período de tempo
- Classe `KitchenOptimizer`: Monta e resolve o problema de otimização

#### `src/visualizations.py`
- Funções para gerar gráficos interativos com Plotly
- Tabelas formatadas com Pandas

#### `src/data_example.py`
- Dados realistas de 15 pratos e 3 períodos
- Custos padrão para o Brasil

---

## 🛠️ Tecnologias

- **Python 3.8+**: Linguagem principal
- **NumPy**: Operações matriciais para o Simplex
- **Pandas**: Manipulação e exibição de dados
- **Streamlit**: Framework para interface web
- **Plotly**: Visualizações interativas

### Por que não usar bibliotecas de PL?

Este projeto foi desenvolvido com fins **educacionais**. A implementação manual do Simplex permite:
- Compreensão profunda do algoritmo
- Controle total sobre o processo de otimização
- Demonstração prática de conceitos teóricos

---

## 📊 Exemplos

### Exemplo Completo (15 pratos, 3 períodos)

**Pratos incluídos:**
- Arroz Branco, Feijão Preto, Frango Grelhado
- Lasanha, Salada Verde, Purê de Batata
- Bife à Parmegiana, Sopa de Legumes
- Macarrão, Torta de Frango, Carne Assada
- Batata Frita, Farofa, Pudim, Suco Natural

**Períodos:**
- Manhã (6h-12h): 240 min fogão, 180 min forno, 720 min-pessoa
- Tarde (12h-18h): 300 min fogão, 240 min forno, 900 min-pessoa
- Noite (18h-22h): 180 min fogão, 120 min forno, 480 min-pessoa

**Resultado Esperado:**
- Custo total otimizado
- Distribuição eficiente da produção entre períodos
- Utilização balanceada de equipamentos

---

## 🐛 Troubleshooting

### Problema: "ModuleNotFoundError"
**Solução**: Certifique-se de que todas as dependências estão instaladas:
```bash
pip install -r requirements.txt
```

### Problema: "Problema Inviável"
**Solução**:
- Aumente as capacidades dos períodos
- Reduza a demanda dos pratos
- Adicione mais períodos de produção

### Problema: Interface não abre
**Solução**:
- Verifique se a porta 8501 está disponível
- Tente especificar outra porta:
```bash
streamlit run app.py --server.port 8502
```

---

## 📚 Referências

- **Algoritmo Simplex**: Método Tableau com Regra de Bland
- **Programação Linear**: Teoria de Otimização Convexa
- **Streamlit Documentation**: https://docs.streamlit.io/
- **Plotly Documentation**: https://plotly.com/python/

---

## 👨‍💻 Autor

**Victor Colen**
- 🎓 PUC - Sistemas Operacionais
- 📧 Email: [seu-email@example.com]
- 💼 LinkedIn: [seu-linkedin]

---

## 📄 Licença

Este projeto foi desenvolvido para fins educacionais como parte do curso de Sistemas Operacionais.

---

## 🙏 Agradecimentos

- Professores da disciplina de Sistemas Operacionais
- Comunidade Python e Streamlit
- Colegas de turma pelas discussões e ideias

---

## 🚀 Próximos Passos (Melhorias Futuras)

- [ ] Restrições nutricionais (calorias, proteínas)
- [ ] Custos variáveis por período (tarifa de energia por horário)
- [ ] Planejamento semanal
- [ ] Exportação de relatório em PDF
- [ ] Otimização multi-objetivo (Pareto)
- [ ] API REST para integração com sistemas ERP

---

<div align="center">
  <p>Desenvolvido com ❤️ usando Programação Linear</p>
  <p>🍳 <strong>OptiChef</strong> - Otimização Inteligente de Cozinhas Industriais</p>
</div>
