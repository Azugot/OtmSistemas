# Planejamento de Dieta com Restrições Nutricionais

Mockup funcional em Python + Qt (PySide6) para otimização de dieta usando programação linear.

## Requisitos funcionais
- Cadastro interno de alimentos em tabela editável.
- Definição de metas nutricionais mínimas (calorias, proteína, carboidrato, vitaminas).
- Botão para calcular dieta otimizada, exibindo porções ideais e custo mínimo.
- Validação de campos vazios e alerta para instâncias inviáveis.

## Execução local
Instale apenas as dependências necessárias:

```bash
pip install PySide6
pip install pulp
```

Depois, execute a aplicação:

```bash
python main.py
```

A interface apresenta painel superior para cadastro e metas, e painel inferior com botão de cálculo e área de resultados (tabela de porções, custo total e resumo de nutrientes alcançados).
