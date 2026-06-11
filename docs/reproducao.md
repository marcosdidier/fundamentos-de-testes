# Guia de reproducao

## Ambiente

Use Python 3.11 ou superior. O projeto usa apenas biblioteca padrao para execucao principal e testes com `unittest`.

Crie um arquivo `.env` a partir de `.env.example`:

```bash
cp .env.example .env
```

Preencha:

```env
ANTHROPIC_API_KEY=sua_chave_aqui
ANTHROPIC_MODEL=claude-haiku-4-5
ANTHROPIC_MAX_TOKENS=64
```

## Validacao local

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

## Gerar datasets transformados (v1 e v2)

Para gerar os datasets transformados:
*   **v1 (prefixos mecânicos):** `python3 scripts/generate_transformed_dataset.py --version v1`
*   **v2 (paráfrases por IA):** `python3 scripts/generate_transformed_dataset.py --version v2`
*   **Ambos (Padrão):** `python3 scripts/generate_transformed_dataset.py --version all`

## Smoke test com API (v2)

Executa 1 caso original com as estratégias estruturadas (`strict` e `few_shot`):

```bash
PYTHONPATH=src python3 scripts/run_experiment.py \
  --version v2 \
  --dataset original \
  --limit 1 \
  --csv-output results/processed/smoke_original_1.csv \
  --jsonl-output results/raw/smoke_original_1.jsonl
```

## Coleta completa

Para executar a coleta completa de um experimento (original + transformados):

### Experimento v2 (Recomendado - Sem `free`)
Executa 420 casos de teste com as estratégias `strict` e `few_shot`, totalizando 840 execuções:
```bash
PYTHONPATH=src python3 scripts/run_experiment.py --version v2 --dataset all
```

### Experimento v1 (Original - Inclui `free`)
Executa 420 casos de teste com as estratégias `free`, `strict` e `few_shot`, totalizando 1260 execuções:
```bash
PYTHONPATH=src python3 scripts/run_experiment.py --version v1 --dataset all
```

## Repetição de 10% (v1)

```bash
PYTHONPATH=src python3 scripts/run_repetition_check.py \
  --csv-output results/processed/repetition_check_results.csv \
  --jsonl-output results/raw/repetition_check_logs.jsonl
```

## Gerar Métricas e Relatórios de Análise (v2)

Para calcular todas as métricas detalhadas, tabelas de visualização, relatórios de comparação de performance e análise qualitativa de falhas para a v2, execute:

```bash
PYTHONPATH=src python3 scripts/analyze_experiments.py
```

Saídas geradas:
*   `data/transformed/transformed_dataset_v2_visualizacao.md` (Tabela visual do dataset v2)
*   `results/processed/comparison_v1_v2.md` (Comparativo de métricas v1 vs v2)
*   `results/processed/failure_analysis_report.md` (Análise de causa raiz de erros)

---

## Métricas e Artefatos do Experimento v1 (Legado)

Para rodar o pipeline legado de análise de métricas da v1:

```bash
PYTHONPATH=src python3 scripts/calculate_metrics.py
PYTHONPATH=src python3 scripts/generate_analysis_artifacts.py
```

Saídas:
*   `results/processed/metrics.csv`
*   `results/processed/summary.csv`
*   `results/processed/analysis_tables.md`
*   `results/processed/representative_failures.csv`

## Pre-categorizar falhas

```bash
PYTHONPATH=src python3 scripts/precategorize_failures.py
```

Saida:

- `results/processed/representative_failures_precategorized.csv`

