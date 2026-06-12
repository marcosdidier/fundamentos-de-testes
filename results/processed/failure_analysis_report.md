# Análise Qualitativa de Falhas: Experimento v1 vs v2

Este relatório apresenta uma análise qualitativa das causas raiz de falhas de classificação e violações metamórficas nos dois experimentos (excluindo a estratégia `free` do v1).

## 1. Distribuição de Violações por Categoria Esperada

| Categoria Esperada | Violações v1 (Sem `free`) | Violações v2 | Variação |
| :--- | :---: | :---: | :---: |
| `account_support` | 0 | 10 | +10 |
| `cancel_order` | 0 | 3 | +3 |
| `other` | 33 | 40 | +7 |
| **TOTAL** | **33** | **53** | **+20** |

## 2. Padrões de Confusão do Modelo (Matriz de Erros)

Abaixo estão listadas as transições de classe mais frequentes onde o modelo desviou do rótulo esperado:

### Experimento v1 (Sem `free`)
| Rótulo Esperado -> Rótulo Classificado | Quantidade de Ocorrências |
| :--- | :---: |
| `other` ➔ `account_support` | 25 |
| `other` ➔ `product_information` | 8 |

### Experimento v2
| Rótulo Esperado -> Rótulo Classificado | Quantidade de Ocorrências |
| :--- | :---: |
| `other` ➔ `account_support` | 30 |
| `other` ➔ `product_information` | 10 |
| `account_support` ➔ `other` | 10 |
| `cancel_order` ➔ `payment_issue` | 3 |

## 3. Diagnóstico e Causa Raiz das Falhas

### Causa 1: Incoerência na Categoria Generalista (`other`)
- **O que aconteceu:** A maior parte de todas as falhas nos dois experimentos vem da categoria `other`. 
- **Diagnóstico:** As mensagens classificadas em `other` na verdade possuem semânticas muito fortes de outras categorias na visão de mundo do LLM:
  - Perguntas sobre horário de atendimento da empresa (`orig_other_009`) e disponibilidade de atendente (`orig_other_010`) são logicamente classificadas como `account_support` pelo modelo.
  - Perguntas sobre parcerias comerciais (`orig_other_006`) são entendidas como `product_information` pelo modelo.
  - Links de política de privacidade (`orig_other_004`) são categorizados como `account_support` ou `product_information`.
  - **Conclusão:** O rótulo `other` é inerentemente problemático para LLMs se não for muito bem definido no prompt (ou se a mensagem for muito específica de atendimento técnico/comercial).

### Causa 2: Desalinhamento de Anotação Humana vs Entendimento da IA (`orig_other_005`)
- **O que aconteceu:** No v2, alteramos o rótulo de `orig_other_005` (*Gostaria de deixar uma sugestão para melhorar o aplicativo*) de `other` para `account_support` com base em discussões internas do grupo. No entanto, isso gerou **10 violações de teste**.
- **Diagnóstico:** O modelo `claude-haiku-4-5` insistiu em classificar esta frase e todas as suas paráfrases (ex: *'Como posso enviar um feedback com ideias para aperfeiçoar o app?'*) como `other` (ou seja, ele manteve a classificação original humana). Isso demonstra que o LLM não vê feedbacks ou sugestões gerais como suporte de conta técnico, gerando um desalinhamento sistemático com a nova anotação humana.

### Causa 3: Confusão Linguística de Vocabulário Financeiro (`cancel_order` ➔ `payment_issue`)
- **O que aconteceu:** No v2, tivemos **3 violações** na categoria `cancel_order` que foram rotuladas como `payment_issue`.
- **Diagnóstico:** Duas paráfrases de cancelamento introduziram a palavra **'transação'**:
  - *'Por favor, suspendam a transação que acabei de concluir.'*
  - *'Preciso anular a transação que fiz no dia de hoje.'*
  - A palavra 'transação' aciona um forte gatilho semântico ligado a questões financeiras e cobranças, fazendo com que o modelo associe a mensagem a `payment_issue` em vez de `cancel_order`. Isso mostra a sensibilidade do LLM ao vocabulário específico das paráfrases.
