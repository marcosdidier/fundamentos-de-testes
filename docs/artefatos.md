# Indice de artefatos

Este documento lista os principais artefatos produzidos no projeto.

## Planejamento

| Artefato | Caminho | Descricao |
| --- | --- | --- |
| Backlog | `BACKLOG.md` | Planejamento por fase, decisoes, pendencias e status de execucao. |
| PDF fonte | `Desenho_Experimental_Plano_Coleta_LLMs_1 (1).pdf` | Documento original usado como base do backlog. |
| Pendencias | `docs/pendencias.md` | Pendencias metodologicas registradas durante o desenvolvimento. |

## Codigo

| Artefato | Caminho | Descricao |
| --- | --- | --- |
| Pacote principal | `src/llm_metamorphic_testing/` | Codigo da aplicacao experimental. |
| Scripts | `scripts/` | Geracao de dataset, execucao da API, repeticao, metricas e analise. |
| Testes | `tests/` | Testes automatizados com `unittest`. |

## Datasets

| Artefato | Caminho | Descricao |
| --- | --- | --- |
| Dataset original | `data/original/original_dataset.csv` | 70 mensagens originais em portugues, 10 por rotulo. |
| Dataset transformado | `data/transformed/transformed_dataset.csv` | 350 casos transformados. |

## Resultados brutos

| Artefato | Caminho | Descricao |
| --- | --- | --- |
| Smoke test JSONL | `results/raw/smoke_original_1.jsonl` | Logs brutos do smoke test de 1 caso. |
| Coleta completa JSONL | `results/raw/full_execution_logs.jsonl` | Logs brutos das 1260 execucoes principais. |
| Repeticao JSONL | `results/raw/repetition_check_logs.jsonl` | Logs brutos da repeticao de 10% da base. |

## Resultados processados

| Artefato | Caminho | Descricao |
| --- | --- | --- |
| Smoke test CSV | `results/processed/smoke_original_1.csv` | Resultado tabular do smoke test. |
| Coleta completa CSV | `results/processed/full_execution_results.csv` | Resultado tabular das 1260 execucoes principais. |
| Repeticao CSV | `results/processed/repetition_check_results.csv` | Resultado tabular da repeticao de 10%. |
| Resumo | `results/processed/summary.csv` | Resumo global das execucoes. |
| Metricas | `results/processed/metrics.csv` | Metricas calculadas. |
| Tabelas de analise | `results/processed/analysis_tables.md` | Tabelas em Markdown para relatorio. |
| Tabelas de analise CSV | `results/processed/analysis_tables.csv` | Tabelas quantitativas em CSV. |
| Falhas representativas | `results/processed/representative_failures.csv` | 20 falhas selecionadas para analise qualitativa. |
| Falhas categorizadas | `results/processed/representative_failures_precategorized.csv` | Falhas representativas categorizadas e validadas. |

## Documentacao de entrega

| Artefato | Caminho | Descricao |
| --- | --- | --- |
| Relatorio tecnico | `docs/relatorio.md` | Relatorio com metodologia, resultados, discussao e ameacas a validade. |
| Guia de reproducao | `docs/reproducao.md` | Comandos para reproduzir o experimento. |
| README | `README.md` | Visao geral do projeto e instrucoes basicas. |

## Apresentação

| Artefato | Caminho | Descricao |
| --- | --- | --- |
| Guia de Estudo | `apresentacao/estudo_apresentacao.md` | Guia completo estruturado em perguntas e respostas para estudo da apresentação de aula. |
| Slides (Markdown) | `apresentacao/slides_apresentacao.md` | Slides em Markdown compatíveis com Marp. |
| Slides (HTML) | `apresentacao/slides_apresentacao.html` | Slides interativos em formato web/HTML com animações. |
| Slides (PDF) | `apresentacao/slides_apresentacao.pdf` | Slides compilados em formato PDF prontos para apresentação. |


