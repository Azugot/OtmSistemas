# Sistema de Otimização de Cozinha Industrial

Aplicação em Streamlit para otimizar a produção de refeições em cozinhas industriais
via programação linear. O modelo minimiza o custo de recursos (gás, energia e água)
respeitando demandas mínimas e capacidades de fogão, forno e equipe por período.

## Funcionalidades
- Cadastro de pratos com demandas e consumos de recursos.
- Definição de períodos com capacidades por turno.
- Configuração de custos unitários.
- Execução do algoritmo Simplex (implementação própria) para encontrar o cronograma
  de produção de menor custo.
- Visualizações interativas em Plotly: cronograma, uso de recursos e custos.
- Dados de exemplo pré-carregados conforme PRD.

## Execução local
Instale as dependências e execute o Streamlit:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Abra o endereço indicado pelo Streamlit no navegador para interagir com a interface.
