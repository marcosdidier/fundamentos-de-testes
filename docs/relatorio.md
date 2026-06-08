# Avaliacao de Testes Metamorficos em LLMs para Classificacao de Intencoes

## Resumo

Este projeto avaliou testes metamorficos em uma aplicacao baseada em LLM para classificacao single-label de intencoes em mensagens de atendimento ao cliente de e-commerce. O sistema sob teste recebeu mensagens em portugues e retornou um unico rotulo entre sete classes predefinidas.

O experimento comparou tres estrategias de prompt: livre, estrito em JSON e few-shot. O modelo usado foi `claude-haiku-4-5`, via API Claude, com `temperature=0` e `max_tokens=64`.

O melhor desempenho foi obtido pelo prompt few-shot, com taxa de violacao por estrategia de 0.0200 e nenhuma saida invalida. O prompt estrito tambem manteve o formato valido, mas apresentou mais violacoes. O prompt livre retornou texto livre em todas as execucoes e, por isso, falhou no contrato de saida esperado.

## Metodologia

### Dominio e tarefa

- Dominio: atendimento ao cliente em e-commerce.
- Idioma: portugues.
- Tarefa: classificacao de intencoes.
- Tipo de classificacao: single-label.
- Modelo: `claude-haiku-4-5`.
- Parametros: `temperature=0`, `max_tokens=64`.

### Rotulos

Foram usados sete rotulos:

- `refund_request`
- `cancel_order`
- `delivery_problem`
- `payment_issue`
- `product_information`
- `account_support`
- `other`

### Dataset

O dataset original possui 70 mensagens em portugues, com distribuicao balanceada de 10 exemplos por rotulo. A partir dele, foram geradas 350 transformacoes metamorficas:

- 210 parafrases semanticas.
- 70 transformacoes de pontuacao.
- 70 transformacoes de capitalizacao.

### Relacoes metamorficas

Foram avaliadas tres relacoes:

- MR1: consistencia semantica para parafrases.
- MR2: invariancia a alteracoes de pontuacao.
- MR3: invariancia a alteracoes de capitalizacao.

### Oraculos

O oraculo principal comparou o rotulo parseado do LLM com o rotulo esperado definido no dataset. Uma violacao ocorreu quando o rotulo parseado diferiu do esperado ou quando a saida nao foi valida.

O oraculo secundario comparou a predicao da entrada transformada com a predicao da entrada original para identificar `prediction flip`. Esse calculo depende de uma predicao original parseavel; por isso, o prompt livre ficou fora do denominador desse oraculo.

## Execucao

Foram executados 420 casos, cada um com tres estrategias de prompt, totalizando 1260 execucoes:

- 70 mensagens originais x 3 prompts = 210 execucoes.
- 350 mensagens transformadas x 3 prompts = 1050 execucoes.

Tambem foi executada uma repeticao de 10% da base tres vezes para verificar possiveis efeitos de nao determinismo. A amostra teve 42 casos, com 6 casos por rotulo e cobertura de originais, parafrases, pontuacao e capitalizacao.

## Resultados

### Resumo global

| Campo | Valor |
| --- | ---: |
| Execucoes | 1260 |
| Casos unicos | 420 |
| Custo total estimado | US$ 0.366396 |
| Violacoes contra rotulo esperado | 460 |
| Saidas invalidas | 420 |
| Tempo medio de resposta | 1.3648s |

### Taxa de violacao por estrategia de prompt

| Estrategia | Violacoes | Denominador | Taxa |
| --- | ---: | ---: | ---: |
| `few_shot` | 7 | 350 | 0.0200 |
| `free` | 350 | 350 | 1.0000 |
| `strict` | 26 | 350 | 0.0743 |

### Taxa de violacao por tipo de transformacao

| Transformacao | Violacoes | Denominador | Taxa |
| --- | ---: | ---: | ---: |
| `capitalization` | 78 | 210 | 0.3714 |
| `paraphrase` | 228 | 630 | 0.3619 |
| `punctuation` | 77 | 210 | 0.3667 |

### Taxa de saida invalida por estrategia

| Estrategia | Saidas invalidas | Denominador | Taxa |
| --- | ---: | ---: | ---: |
| `few_shot` | 0 | 420 | 0.0000 |
| `free` | 420 | 420 | 1.0000 |
| `strict` | 0 | 420 | 0.0000 |

### Custo por violacao detectada

| Estrategia | Custo relativo usado no calculo | Violacoes | Custo por violacao |
| --- | ---: | ---: | ---: |
| `few_shot` | 129011 | 9 | US$ 0.0143 |
| `free` | 157711 | 420 | US$ 0.0004 |
| `strict` | 79671 | 31 | US$ 0.0026 |

O custo por violacao do prompt livre deve ser interpretado com cuidado, pois as violacoes foram causadas por falha sistematica de formato, nao por deteccao util de inconsistencias semanticas.

### Prediction flip

Foram observados 9 `prediction flips` em 700 execucoes transformadas com predicao original parseavel, resultando em taxa de 0.0129. Por estrategia:

- `strict`: 2 em 350.
- `few_shot`: 7 em 350.

O prompt livre nao entrou nesse denominador porque suas predicoes originais nao foram parseaveis.

### Repeticao de 10%

Na repeticao de 10% da base:

- Execucoes: 378.
- Erros de API: 0.
- Saidas invalidas: 126, todas no prompt livre.
- Grupos com variacao entre repeticoes: 0.

Com `temperature=0`, nao foi observada variacao entre repeticoes para o mesmo par caso/estrategia.

## Analise qualitativa

Foram selecionadas 20 falhas representativas para inspecao qualitativa. A categorizacao final validada foi:

| Categoria | Quantidade |
| --- | ---: |
| `ambiguous input` | 10 |
| `label confusion` | 2 |
| `formatting failure` | 8 |

As falhas de formato correspondem ao prompt livre, que retornou respostas explicativas em vez de JSON parseavel. As falhas categorizadas como `ambiguous input` ocorreram principalmente em mensagens rotuladas como `other`, mas que podem ser interpretadas como pedidos de suporte ou informacao. As falhas de `label confusion` indicam casos em que a saida foi valida, mas o modelo escolheu uma categoria especifica diferente do rotulo esperado.

## Discussao

O prompt few-shot apresentou o melhor resultado geral, combinando saidas validas com menor taxa de violacao metamorfica. O prompt estrito tambem foi adequado para controlar formato, mas teve mais erros de classificacao do que o few-shot.

O prompt livre mostrou baixa adequacao para este sistema, pois nao impôs o contrato de saida em JSON. Como o parser esperava um objeto JSON curto com `label`, todas as respostas do prompt livre foram invalidas. Esse resultado sugere que, para sistemas que dependem de integracao programatica com LLMs, o controle do formato de saida e parte essencial do desenho do prompt.

As taxas por tipo de transformacao ficaram proximas entre si quando consideradas todas as estrategias, mas esse resultado e fortemente influenciado pelo prompt livre. A analise por estrategia mostra que few-shot e strict reduzem substancialmente as violacoes.

## Ameacas a validade

| Ameaca | Mitigacao aplicada ou planejada |
| --- | --- |
| Tamanho limitado do dataset | Foi usada distribuicao balanceada com 70 mensagens originais e 350 transformacoes. A limitacao deve ser declarada nas conclusoes. |
| Parafrases podem alterar o sentido original | As parafrases foram marcadas para revisao e falhas representativas foram analisadas qualitativamente. |
| Subjetividade na validacao manual | Foram usadas categorias predefinidas e o arquivo de falhas representativas preserva textos, rotulos e predicoes para auditoria. |
| Mudancas na API ou versao do modelo | O modelo, parametros, timestamps, outputs brutos, token usage e custos foram registrados. |
| Custo de API pode limitar repeticoes | A repeticao foi restrita a 10% da base, conforme desenho experimental. |
| Nao determinismo mesmo com temperature 0 | Uma amostra de 10% foi repetida tres vezes; nao houve variacao observada. |
| Baixa generalizacao para outros dominios | As conclusoes devem ser restritas ao dominio de atendimento de e-commerce em portugues. |

## Conclusao

Dentro do escopo avaliado, a estrategia few-shot foi a mais eficaz para classificacao de intencoes com LLM, pois produziu saidas validas e a menor taxa de violacao metamorfica. O prompt estrito foi uma alternativa robusta em formato, mas menos preciso. O prompt livre foi inadequado para a aplicacao por nao respeitar o contrato de saida esperado.

As conclusoes se aplicam ao dominio de atendimento ao cliente em e-commerce, ao conjunto de sete rotulos definido e ao modelo `claude-haiku-4-5` com os parametros usados neste experimento.

## Trabalhos futuros

- Avaliar outros modelos da familia Claude ou de outras familias.
- Aumentar o dataset e incluir mensagens reais anonimizadas.
- Refinar a classe `other` para reduzir ambiguidades.
- Testar prompts com mecanismos adicionais de restricao de formato.
- Repetir o experimento em outros dominios alem de e-commerce.

