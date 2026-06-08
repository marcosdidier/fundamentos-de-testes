# Backlog do Projeto: Testes Metamorficos em LLMs

Este backlog foi gerado a partir do documento `Desenho_Experimental_Plano_Coleta_LLMs_1 (1).pdf`.

Regra para a proxima sessao Codex: nao inventar requisitos, dados, metricas, modelos especificos, formatos ou decisoes metodologicas alem do que esta neste backlog e no PDF fonte. Quando algo nao estiver definido no documento, registrar como pendencia ou pedir decisao ao grupo.

## Contexto do projeto

Tema escolhido:

- Tecnicas de testes para sistemas baseados em IA.

Titulo do projeto:

- Avaliacao de Testes Metamorficos em Sistemas Baseados em LLMs para Classificacao de Intencoes.

Enfoque:

- Estudo empirico exploratorio e comparativo de estrategias de prompt em uma aplicacao baseada em LLM.

Objetivo:

- Avaliar se um sistema baseado em LLM consegue manter consistencia semantica ao classificar mensagens de clientes que expressam a mesma intencao de formas diferentes.
- Usar relacoes metamorficas para verificar se transformacoes controladas na entrada preservam o rotulo esperado de classificacao.

Sistema sob teste:

- Pequena aplicacao de classificacao de intencoes baseada em LLM.
- A aplicacao recebe uma mensagem textual de cliente de e-commerce.
- A aplicacao retorna exatamente um rotulo correspondente a intencao principal expressa.
- A aplicacao deve ser estruturada como sistema com template de prompt, cliente de API, parser de saida e executor de testes.

Decisoes fixas do experimento:

- Dominio: atendimento ao cliente em e-commerce.
- Tarefa: classificacao de intencoes.
- Idioma: portugues.
- Tipo de classificacao: single-label.
- Modelo: LLM via API, utilizando um modelo da familia Claude.
- Quantidade de modelos: um modelo.
- Modelo escolhido para implementacao: `claude-haiku-4-5`.
- Temperature: 0.
- Max tokens: 64, pois a saida esperada e apenas um JSON curto.
- Politica de erro: em caso de falha, repetir uma vez; se falhar novamente, marcar como erro.

Pendencias que o PDF nao especifica:

- Formato exato dos arquivos CSV e JSONL alem dos campos listados.

Decisoes complementares tomadas durante a implementacao:

- Nome exato do modelo Claude: `claude-haiku-4-5`.
- Valor numerico de `max_tokens`: 64.
- `estimated_cost`: calculado a partir de `usage.input_tokens` e `usage.output_tokens` retornados pela API, usando os precos configurados para o modelo em `src/llm_metamorphic_testing/costs.py`.
- `Token Usage`: registrado em `metadata.usage` nos logs JSONL com `input_tokens`, `output_tokens` e `total_tokens` quando disponiveis.
- Variaveis de ambiente suportadas: `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL`, `ANTHROPIC_MAX_TOKENS`.
- Arquivo de exemplo para configuracao local: `.env.example`.

## Rotulos de classificacao

Cada mensagem deve ser classificada em exatamente um dos sete rotulos abaixo. O conjunto de rotulos deve permanecer igual em todas as estrategias de prompt.

| Rotulo | Descricao |
| --- | --- |
| `refund_request` | Solicitacao de reembolso ou devolucao de dinheiro. |
| `cancel_order` | Solicitacao de cancelamento de pedido ou compra. |
| `delivery_problem` | Problemas relacionados a entrega, atraso, rastreio ou recebimento. |
| `payment_issue` | Problemas relacionados a pagamento, cobranca, cartao, boleto ou PIX. |
| `product_information` | Duvidas sobre caracteristicas, disponibilidade, garantia ou detalhes de produto. |
| `account_support` | Problemas relacionados a conta, login, senha ou cadastro. |
| `other` | Mensagens que nao se encaixam claramente nas categorias anteriores. |

## Dataset e transformacoes

Dataset original:

- 70 mensagens em portugues.
- Distribuicao balanceada entre os sete rotulos.
- 10 exemplos originais por classe.
- Mensagens geradas com apoio de um LLM.
- Revisao manual pelo grupo antes do experimento.
- Casos ambiguos devem ser evitados.
- Mensagens devem variar em tamanho e estilo, incluindo frases curtas, medias e longas.

Transformacoes metamorficas:

| Tipo | Quantidade | Descricao |
| --- | ---: | --- |
| Parafrase semantica | 3 por mensagem, 210 casos | Reescrita com outras palavras preservando a mesma intencao. |
| Pontuacao | 1 por mensagem, 70 casos | Alteracao controlada da pontuacao sem mudar o conteudo semantico. |
| Capitalizacao | 1 por mensagem, 70 casos | Alteracao de caixa alta, caixa baixa ou combinacoes controladas. |

Quantidade de casos:

- 70 mensagens originais.
- 350 mensagens transformadas.
- 3 estrategias de prompt.
- 210 execucoes originais: 70 mensagens originais x 3 prompts.
- 1050 execucoes transformadas: 350 mensagens transformadas x 3 prompts.
- Total estimado: 1260 execucoes.
- Repetir 10% da base tres vezes para verificar possiveis efeitos de nao determinismo, mesmo com temperature 0.

Criterios de validacao das parafrases:

1. Preservar a intencao original da mensagem.
2. Manter o mesmo rotulo esperado.
3. Nao introduzir ambiguidade.
4. Nao adicionar informacoes que mudem o sentido da mensagem.
5. Nao remover informacoes essenciais da solicitacao original.

Exemplo de parafrase valida:

- Original: "Quero cancelar meu pedido."
- Parafrase: "Gostaria de desistir da compra que fiz."
- Rotulo esperado: `cancel_order`

Exemplo de parafrase potencialmente invalida:

- Original: "Quero cancelar meu pedido."
- Parafrase: "Quero cancelar meu pedido e pedir reembolso."
- Motivo: a nova frase introduz uma segunda intencao.

## Relacoes metamorficas e oraculos

Relacoes metamorficas:

| Relacao | Definicao | Comportamento esperado |
| --- | --- | --- |
| MR1 - Consistencia semantica | Se duas entradas expressam a mesma intencao, o sistema deve retornar o mesmo rotulo. | A parafrase deve receber o mesmo rotulo da mensagem original. |
| MR2 - Invariancia a pontuacao | Alteracoes de pontuacao nao devem mudar a intencao principal. | A mensagem com pontuacao alterada deve manter o mesmo rotulo. |
| MR3 - Invariancia a capitalizacao | Alteracoes de caixa alta ou caixa baixa nao devem mudar a intencao principal. | A mensagem com capitalizacao alterada deve manter o mesmo rotulo. |

Oraculo principal:

- Comparar a saida parseada do LLM com o rotulo esperado humano definido e validado pelo grupo.
- Violacao ocorre quando a resposta parseada do modelo e diferente do rotulo esperado para aquele caso.

Oraculo secundario:

- Comparar a saida obtida para a entrada transformada com a saida obtida pelo LLM para a entrada original.
- Essa comparacao mede mudancas de predicao causadas pela transformacao, mesmo quando a saida original do modelo ja estava incorreta.
- Quando a predicao transformada difere da predicao original, registrar `prediction flip`.

## Estrategias de prompt

Todas as estrategias devem usar o mesmo conjunto de rotulos.

### Prompt livre

```text
Leia a mensagem do cliente e identifique qual e a intencao principal.
Mensagem:
"{mensagem}"
```

### Prompt estrito

```text
Classifique a intencao da mensagem abaixo.
Retorne apenas um JSON no seguinte formato:
{"label": "um_dos_rotulos"}
Rotulos possiveis:
refund_request, cancel_order, delivery_problem, payment_issue,
product_information, account_support, other
Mensagem:
"{mensagem}"
```

### Prompt few-shot

```text
Classifique a intencao da mensagem abaixo.
Rotulos possiveis:
refund_request, cancel_order, delivery_problem, payment_issue,
product_information, account_support, other
Exemplos:
"Quero meu dinheiro de volta." -> refund_request
"Gostaria de cancelar meu pedido." -> cancel_order
"Minha entrega ainda nao chegou." -> delivery_problem
"Meu pagamento foi recusado." -> payment_issue
"Esse produto tem garantia?" -> product_information
"Nao consigo acessar minha conta." -> account_support
"Obrigado pelo atendimento." -> other
Retorne apenas um JSON no seguinte formato:
{"label": "um_dos_rotulos"}
Mensagem:
"{mensagem}"
```

## Plano de coleta e armazenamento

Armazenar dados em dois formatos:

- CSV para analise tabular.
- JSONL para preservacao dos logs brutos.

Campos coletados por execucao:

- `case_id`
- `original_input_id`
- `transformation_type`
- `original_text`
- `transformed_text`
- `expected_label`
- `prompt_strategy`
- `prompt_text`
- `model_name`
- `parameters`
- `raw_output`
- `parsed_label`
- `is_valid_output`
- `is_violation_expected_label`
- `is_prediction_flip`
- `execution_time`
- `estimated_cost`
- `timestamp`
- `manual_review_notes`

Estrutura sugerida do repositorio:

```text
llm-metamorphic-testing/
|-- data/
|   |-- original/
|   `-- transformed/
|-- results/
|   |-- raw/
|   `-- processed/
|-- notebooks/
|-- src/
`-- docs/
```

## Metricas e analise

Metricas de avaliacao:

| Metrica | Descricao |
| --- | --- |
| Metamorphic Violation Rate | Proporcao de casos transformados que violam a relacao metamorfica esperada. |
| Prediction Flip Rate | Proporcao de casos em que a predicao da entrada transformada difere da predicao da entrada original. |
| Invalid Output Rate | Proporcao de respostas que nao seguem o formato esperado ou nao contem um rotulo valido. |
| Violation Rate by Transformation Type | Taxa de violacao separada por parafrase, pontuacao e capitalizacao. |
| Violation Rate by Prompt Strategy | Taxa de violacao separada por prompt livre, estrito e few-shot. |
| Cost per Detected Violation | Custo de API necessario para detectar uma violacao. |
| Average Response Time | Tempo medio de resposta por execucao. |
| Token Usage | Quantidade de tokens utilizada por estrategia e no total. |
| Total API Cost | Custo total estimado da execucao do experimento. |

Calculos de custo por violacao:

- Custo por violacao global = custo total da API / numero total de violacoes detectadas.
- Custo por violacao por estrategia = custo da estrategia / numero de violacoes detectadas pela estrategia.

Variaveis do experimento:

| Tipo de variavel | Variaveis |
| --- | --- |
| Independentes | Estrategia de prompt; tipo de transformacao. |
| Dependentes | Taxa de violacao metamorfica; taxa de mudanca de predicao; taxa de saida invalida; custo; tempo de resposta. |
| Controladas | Mesmo modelo; mesma temperature; mesmo dataset; mesmos rotulos; mesmas transformacoes; mesmos parametros de API. |

Cenarios experimentais:

- Cenario 1: execucao com prompt livre.
- Cenario 2: execucao com prompt estrito em JSON.
- Cenario 3: execucao com prompt few-shot com sete exemplos fixos.

Plano de analise:

- Comparar a taxa de violacao por estrategia de prompt.
- Comparar a taxa de violacao por tipo de transformacao.
- Comparar a taxa de saida invalida por estrategia de prompt.
- Comparar o custo por violacao detectada.
- Analisar exemplos representativos de falhas.
- Produzir tabelas e graficos com:
  - Violation rate by prompt strategy.
  - Violation rate by transformation type.
  - Invalid output rate by prompt strategy.
  - Cost per detected violation by prompt strategy.
  - Representative failure examples.
- Inspecionar manualmente entre 10 e 20 violacoes representativas.
- Categorizar falhas representativas segundo:
  - `label confusion`
  - `formatting failure`
  - `semantic misunderstanding`
  - `over-sensitivity to wording`
  - `ambiguous input`
  - `paraphrase quality issue`

## Ameacas a validade

Registrar e discutir as ameacas abaixo no relatorio:

| Ameaca | Mitigacao planejada |
| --- | --- |
| Tamanho limitado do dataset | Utilizar distribuicao balanceada e documentar a limitacao no relatorio. |
| Parafrases podem alterar o sentido original | Realizar revisao manual por dois avaliadores e discutir discordancias. |
| Subjetividade na validacao manual | Definir criterios objetivos de aceitacao e registrar observacoes dos revisores. |
| Mudancas na API ou versao do modelo | Registrar modelo, data, parametros e outputs brutos. |
| Custo de API pode limitar repeticoes | Manter desenho experimental de tamanho medio e repetir apenas 10% da base. |
| Nao determinismo mesmo com temperature 0 | Executar repeticoes em uma amostra da base e registrar variacoes. |
| Baixa generalizacao para outros dominios | Restringir conclusoes ao dominio de e-commerce e indicar trabalhos futuros. |

## Backlog por fase

### Fase 1 - Estrutura do projeto

- [x] Criar estrutura sugerida do repositorio:
  - `data/original/`
  - `data/transformed/`
  - `results/raw/`
  - `results/processed/`
  - `notebooks/`
  - `src/`
  - `docs/`
- [x] Documentar no repositorio que o experimento usa apenas um modelo Claude via API.
- [x] Registrar como pendencia a escolha do nome exato do modelo Claude.
- [x] Definir local dos arquivos CSV e JSONL sem alterar os campos coletados definidos no PDF.

Status:

- Implementado pacote base em `src/llm_metamorphic_testing/`.
- Criados modulos de rotulos, prompts, parser, schemas e runner abstrato sem API real.
- Pendencias metodologicas registradas em `docs/pendencias.md`.
- Testes unitarios locais executados com `unittest`.

### Fase 2 - Dataset original

- [x] Criar 70 mensagens originais em portugues com apoio de um LLM.
- [x] Distribuir exatamente 10 mensagens para cada rotulo:
  - `refund_request`
  - `cancel_order`
  - `delivery_problem`
  - `payment_issue`
  - `product_information`
  - `account_support`
  - `other`
- [x] Garantir variacao de tamanho e estilo: frases curtas, medias e longas.
- [x] Evitar casos ambiguos nesta etapa.
- [ ] Revisar manualmente cada mensagem original.
- [ ] Confirmar que cada exemplo possui uma intencao principal clara.
- [ ] Confirmar que o rotulo esperado de cada exemplo esta adequado.

Status:

- Dataset criado em `data/original/original_dataset.csv`.
- Validacao mecanica: 70 linhas, 70 IDs unicos, 10 exemplos por rotulo, nenhum texto vazio e nenhum rotulo fora do conjunto definido.
- Revisao manual do grupo ainda pendente.

### Fase 3 - Transformacoes metamorficas

- [x] Gerar 3 parafrases semanticas para cada mensagem original.
- [x] Gerar 1 transformacao de pontuacao para cada mensagem original.
- [x] Gerar 1 transformacao de capitalizacao para cada mensagem original.
- [ ] Validar cada parafrase por dois avaliadores.
- [ ] Discutir discordancias entre avaliadores.
- [ ] Aceitar parafrases somente quando cumprirem todos os cinco criterios da secao "Dataset e transformacoes".
- [ ] Registrar observacoes de revisao em `manual_review_notes` quando aplicavel.
- [x] Garantir total de 350 casos transformados.

Status:

- Dataset transformado criado em `data/transformed/transformed_dataset.csv`.
- Gerador versionado em `scripts/generate_transformed_dataset.py`.
- Validacao mecanica: 350 casos transformados, 210 parafrases, 70 pontuacao, 70 capitalizacao, 5 transformacoes por original e nenhum rotulo fora do conjunto definido.
- Todos os casos permanecem com `manual_review_status=pending`.
- Revisao manual das parafrases por dois avaliadores ainda pendente.

### Fase 4 - Aplicacao sob teste

- [x] Implementar template de prompt para prompt livre.
- [x] Implementar template de prompt para prompt estrito.
- [x] Implementar template de prompt para prompt few-shot.
- [x] Implementar cliente de API para um modelo da familia Claude.
- [x] Configurar temperature igual a 0.
- [x] Configurar limite baixo de tokens de saida.
- [x] Implementar politica de erro:
  - repetir uma vez em caso de falha;
  - se falhar novamente, marcar como erro.
- [x] Implementar parser de saida.
- [x] Validar que a saida parseada contem exatamente um dos sete rotulos permitidos.
- [x] Registrar `is_valid_output`.

Status:

- Templates de prompt e parser implementados localmente.
- Runner abstrato implementado para receber um cliente LLM via interface.
- Cliente Claude real implementado em `src/llm_metamorphic_testing/claude_client.py` usando a Messages API por HTTP.
- Configuracao padrao: `claude-haiku-4-5`, `temperature=0`, `max_tokens=64`.
- `.env.example` criado para orientar configuracao local da chave e dos parametros.
- Politica de erro implementada: o cliente tenta a chamada original e uma repeticao; se falhar novamente, o runner registra a execucao como saida invalida com `api_error` em `metadata`.
- Uso de tokens retornado pela API e salvo em `metadata.usage`; custo estimado salvo em `estimated_cost` quando houver precificacao configurada.

### Fase 5 - Executor de testes

- [x] Executar as 70 mensagens originais com cada uma das 3 estrategias de prompt.
- [x] Executar os 350 casos transformados com cada uma das 3 estrategias de prompt.
- [x] Registrar total estimado de 1260 execucoes.
- [x] Repetir 10% da base tres vezes para verificar possiveis efeitos de nao determinismo.
- [x] Registrar para cada execucao todos os campos listados em "Plano de coleta e armazenamento".
- [x] Salvar resultados em CSV.
- [x] Salvar logs brutos em JSONL.

Status:

- Implementado carregamento de `.env` sem dependencia externa em `src/llm_metamorphic_testing/config.py`.
- Implementados loaders de dataset em `src/llm_metamorphic_testing/datasets.py`.
- Implementado executor de casos em `src/llm_metamorphic_testing/executor.py`, aplicando as tres estrategias de prompt.
- Criada CLI `scripts/run_experiment.py`.
- Smoke test sugerido antes da execucao completa:
  - `PYTHONPATH=src python3 scripts/run_experiment.py --dataset original --limit 1`
- Smoke test real executado com 1 caso original e 3 chamadas de API:
  - Saidas em `results/processed/smoke_original_1.csv` e `results/raw/smoke_original_1.jsonl`.
  - Prompt livre: resposta textual/truncada, `is_valid_output=False`.
  - Prompt estrito: `parsed_label=refund_request`, `is_valid_output=True`.
  - Prompt few-shot: `parsed_label=refund_request`, `is_valid_output=True`.
  - `usage` e `estimated_cost` foram registrados.
- Execucao completa sugerida, quando aprovada pelo grupo:
  - `PYTHONPATH=src python3 scripts/run_experiment.py --dataset all`
- Execucao completa realizada:
  - CSV: `results/processed/full_execution_results.csv`.
  - JSONL: `results/raw/full_execution_logs.jsonl`.
  - Casos executados: 420.
  - Execucoes registradas: 1260.
  - Erros de API: 0.
  - Total de tokens registrado: 205332 (`input_tokens=165066`, `output_tokens=40266`).
  - Custo estimado registrado: US$ 0.366396.
  - Saidas invalidas: 420, todas no prompt livre.
  - Violacoes contra rotulo esperado: prompt livre 420, prompt estrito 31, prompt few-shot 9.
  - `prediction_flip`: 9 casos entre 700 execucoes transformadas com predicao original parseavel; prompt livre ficou sem base parseavel para esse oraculo secundario.
- Repeticao de 10% da base realizada:
  - Amostra estratificada de 42 casos: 6 por rotulo.
  - Distribuicao por transformacao na amostra: 7 originais, 21 parafrases, 7 pontuacao, 7 capitalizacao.
  - Repeticoes: 3.
  - Casos repetidos: 126.
  - Execucoes registradas: 378.
  - CSV: `results/processed/repetition_check_results.csv`.
  - JSONL: `results/raw/repetition_check_logs.jsonl`.
  - Erros de API: 0.
  - Total de tokens registrado: 60002 (`input_tokens=47943`, `output_tokens=12059`).
  - Custo estimado registrado: US$ 0.108238.
  - Saidas invalidas: 126, todas no prompt livre.
  - Grupos com variacao entre repeticoes: 0.
- Implementada infraestrutura de persistencia em `src/llm_metamorphic_testing/storage.py`.
- CSV usa exatamente os campos listados em "Plano de coleta e armazenamento".
- JSONL preserva o registro completo de execucao, incluindo metadados auxiliares como erro de parser quando houver.
- Execucao real dos casos ainda pendente porque requer `ANTHROPIC_API_KEY` valida e decisao operacional do grupo para consumir API.

### Fase 6 - Oraculos e metricas

- [x] Calcular violacao em relacao ao rotulo esperado humano.
- [x] Calcular `prediction flip` comparando saida transformada com saida original do LLM.
- [x] Calcular Metamorphic Violation Rate.
- [x] Calcular Prediction Flip Rate.
- [x] Calcular Invalid Output Rate.
- [x] Calcular Violation Rate by Transformation Type.
- [x] Calcular Violation Rate by Prompt Strategy.
- [x] Calcular Cost per Detected Violation.
- [x] Calcular Average Response Time.
- [x] Registrar Token Usage.
- [x] Calcular Total API Cost.
- [x] Calcular custo por violacao global.
- [x] Calcular custo por violacao por estrategia.

Status:

- Script de metricas criado em `scripts/calculate_metrics.py`.
- Modulo de metricas criado em `src/llm_metamorphic_testing/metrics.py`.
- Arquivos gerados:
  - `results/processed/summary.csv`.
  - `results/processed/metrics.csv`.
- Resumo global:
  - Execucoes: 1260.
  - Casos unicos: 420.
  - Custo total estimado: US$ 0.366396.
  - Total de violacoes contra rotulo esperado: 460.
  - Total de saidas invalidas: 420.
  - Tempo medio de resposta: 1.3648s.
- Metricas principais:
  - Invalid Output Rate: 0.3333.
  - Metamorphic Violation Rate: 0.3648 sobre 1050 execucoes transformadas.
  - Prediction Flip Rate: 0.0129 sobre 700 execucoes transformadas com predicao original parseavel.
  - Violation Rate by Transformation Type:
    - `capitalization`: 0.3714.
    - `paraphrase`: 0.3619.
    - `punctuation`: 0.3667.
  - Violation Rate by Prompt Strategy:
    - `free`: 1.0000.
    - `strict`: 0.0743.
    - `few_shot`: 0.0200.
  - Cost per Detected Violation:
    - global: US$ 0.000797.
    - `free`: US$ 0.000376.
    - `strict`: US$ 0.002570.
    - `few_shot`: US$ 0.014335.
- Observacao: o custo por violacao inclui violacoes causadas por saidas invalidas; por isso o prompt livre aparece com baixo custo por violacao, apesar de falhar no formato em todas as execucoes.

### Fase 7 - Analise quantitativa e qualitativa

- [x] Gerar tabela ou grafico de violation rate by prompt strategy.
- [x] Gerar tabela ou grafico de violation rate by transformation type.
- [x] Gerar tabela ou grafico de invalid output rate by prompt strategy.
- [x] Gerar tabela ou grafico de cost per detected violation by prompt strategy.
- [x] Selecionar entre 10 e 20 violacoes representativas.
- [x] Inspecionar manualmente as violacoes selecionadas.
- [x] Categorizar as falhas representativas usando as categorias definidas no PDF.

Status:

- Script de artefatos de analise criado em `scripts/generate_analysis_artifacts.py`.
- Modulo de analise criado em `src/llm_metamorphic_testing/analysis.py`.
- Tabelas geradas em:
  - `results/processed/analysis_tables.md`.
  - `results/processed/analysis_tables.csv`.
- Falhas representativas selecionadas em `results/processed/representative_failures.csv`.
- Total de falhas selecionadas: 20.
- Distribuicao das falhas selecionadas por estrategia:
  - `strict`: 6.
  - `few_shot`: 6.
  - `free`: 8.
- Categorias iniciais:
  - `formatting failure`: 8 casos, atribuida automaticamente para saidas invalidas.
  - `pending_manual_review`: 12 casos, aguardando inspecao e classificacao qualitativa final.
- Pre-categorizacao gerada em `results/processed/representative_failures_precategorized.csv`.
- Distribuicao da pre-categorizacao:
  - `ambiguous input`: 10.
  - `label confusion`: 2.
  - `formatting failure`: 8.
- Pre-categorizacao validada pelo grupo e aceita como categorizacao qualitativa final para os 20 casos selecionados.

### Fase 8 - Documentacao e entrega

- [x] Documentar metodologia.
- [x] Documentar resultados.
- [x] Documentar discussao.
- [x] Documentar ameacas a validade e mitigacoes.
- [x] Restringir conclusoes ao dominio de e-commerce.
- [x] Indicar trabalhos futuros quando discutir baixa generalizacao para outros dominios.
- [x] Preparar material de entrega para a disciplina de Testes de Software.

Status:

- Relatorio tecnico criado em `docs/relatorio.md`.
- Guia de reproducao criado em `docs/reproducao.md`.
- README criado em `README.md`.
- Indice de artefatos criado em `docs/artefatos.md`.
- O relatorio inclui metodologia, resultados quantitativos, analise qualitativa, discussao, ameacas a validade, conclusao e trabalhos futuros.
- O guia de reproducao inclui os comandos para validacao local, geracao de transformacoes, smoke test, coleta completa, repeticao de 10%, calculo de metricas e geracao de artefatos de analise.
- Checagem final de consistencia executada:
  - Testes automatizados: 41 testes OK.
  - Dataset original: 70 linhas.
  - Dataset transformado: 350 linhas.
  - Coleta completa: 1260 registros em CSV e 1260 logs JSONL.
  - Repeticao de 10%: 378 registros em CSV e 378 logs JSONL.
  - Falhas representativas categorizadas: 20 linhas.
  - Documentos principais presentes: `README.md`, `docs/artefatos.md`, `docs/relatorio.md`, `docs/reproducao.md`, `BACKLOG.md`.

## Divisao de trabalho sugerida

| Fase | Responsabilidade |
| --- | --- |
| Dataset | Criar e revisar as 70 mensagens originais. |
| Transformacoes | Gerar e validar parafrases, pontuacao e capitalizacao. |
| Implementacao | Criar cliente da API, templates de prompt, parser e executor de testes. |
| Analise | Calcular metricas, gerar tabelas e graficos. |
| Escrita | Documentar metodologia, resultados, discussao e ameacas a validade. |

## Checklist de consistencia antes de executar

- [x] O projeto ainda usa apenas um modelo Claude via API.
- [x] O conjunto de rotulos continua com exatamente 7 classes.
- [x] Cada classe tem 10 mensagens originais.
- [x] O dataset original tem 70 mensagens.
- [x] Existem 210 parafrases semanticas.
- [x] Existem 70 transformacoes de pontuacao.
- [x] Existem 70 transformacoes de capitalizacao.
- [x] O total de casos transformados e 350.
- [x] As tres estrategias de prompt usam os mesmos rotulos.
- [x] O total estimado de execucoes e 1260.
- [x] A repeticao de nao determinismo usa 10% da base, tres vezes.
- [x] Todos os campos de coleta do PDF sao preservados.
- [x] As metricas do PDF sao calculadas ou marcadas como pendencia justificada.
