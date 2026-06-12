# Relatório Comparativo: Experimento v1 vs v2

Este relatório apresenta um comparativo detalhado entre os resultados do **Experimento v1** (paráfrases geradas por prefixo mecânico) e o **Experimento v2** (paráfrases geradas de forma fluida e natural por IA, validadas humanamente). A estratégia de prompt livre (`free`) foi removida de ambas as análises para focar apenas nas saídas estruturadas em JSON (`strict` e `few_shot`).

## 1. Visão Geral Comparativa

| Métrica | Experimento v1 (Sem `free`) | Experimento v2 | Variação |
| :--- | :---: | :---: | :---: |
| **Taxa de Violação Metamórfica Geral** | 4.7143% (33/700) | 7.5714% (53/700) | +2.8571% |
| **Taxa de Flip de Predição Geral** | 1.2857% (9/700) | 3.0000% (21/700) | +1.7143% |
| **Saídas Inválidas (Formato JSON)** | 0 | 0 | 0 |
| **Tempo Médio de Resposta (s)** | 1.1922s | 1.3301s | +0.1379s |
| **Custo Total Estimado da API (USD)** | $0.208684 | $0.205886 | $-0.002798 |

## 2. Violações Metamórficas por Estratégia de Prompt

| Estratégia | Taxa v1 (Sem `free`) | Taxa v2 | Variação |
| :--- | :---: | :---: | :---: |
| `few_shot` | 2.0000% (7/350) | 5.7143% (20/350) | +3.7143% |
| `strict` | 7.4286% (26/350) | 9.4286% (33/350) | +2.0000% |

## 3. Violações Metamórficas por Tipo de Transformação

| Transformação | Taxa v1 (Sem `free`) | Taxa v2 | Variação |
| :--- | :---: | :---: | :---: |
| `capitalization` | 5.7143% (8/140) | 7.8571% (11/140) | +2.1429% |
| `paraphrase` | 4.2857% (18/420) | 7.8571% (33/420) | +3.5714% |
| `punctuation` | 5.0000% (7/140) | 6.4286% (9/140) | +1.4286% |

## 4. Flip de Predição por Estratégia de Prompt

| Estratégia | Taxa v1 (Sem `free`) | Taxa v2 | Variação |
| :--- | :---: | :---: | :---: |
| `few_shot` | 2.0000% (7/350) | 3.4286% (12/350) | +1.4286% |
| `strict` | 0.5714% (2/350) | 2.5714% (9/350) | +2.0000% |

## 5. Análise dos Resultados e Conclusão

### Por que a taxa de violações metamórficas aumentou na v2?
1. **Paráfrases Mais Naturais e Diversificadas:** No Experimento v1, o gerador de paráfrases utilizava um método automático de inserção de prefixos fixos (ex: todas as paráfrases de *refund_request* começavam com *'Preciso que a loja providencie a devolucao do valor, pois...'*). Isso tornava as sentenças muito semelhantes entre si e com forte viés de palavra-chave, facilitando a classificação correta pelo LLM. Na v2, a IA gerou sentenças com vocabulário rico, estruturas sintáticas diversas e sem prefixos repetitivos, criando um teste metamórfico significativamente mais realista e desafiador.
2. **Robustez dos Testes:** O aumento na taxa de violação geral (de **4.7143%** para **7.5714%**) indica que o novo dataset é melhor para encontrar inconsistências semânticas e instabilidades na classificação do modelo, expondo a verdadeira sensibilidade do LLM à variação linguística natural.
3. **Desempenho dos Prompts:** A estratégia `few_shot` continuou apresentando resultados superiores e mais estáveis do que a estratégia `strict` (taxa de erro de **5.7143%** contra **9.4286%**), embora ambas tenham sofrido um leve aumento devido à maior qualidade do dataset.
