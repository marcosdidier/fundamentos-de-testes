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

## Gerar datasets transformados

```bash
python3 scripts/generate_transformed_dataset.py
```

## Smoke test com API

Executa 1 caso original com as 3 estrategias:

```bash
PYTHONPATH=src python3 scripts/run_experiment.py \
  --dataset original \
  --limit 1 \
  --csv-output results/processed/smoke_original_1.csv \
  --jsonl-output results/raw/smoke_original_1.jsonl
```

## Coleta completa

Executa 420 casos com 3 estrategias, totalizando 1260 chamadas:

```bash
PYTHONPATH=src python3 scripts/run_experiment.py \
  --dataset all \
  --csv-output results/processed/full_execution_results.csv \
  --jsonl-output results/raw/full_execution_logs.jsonl
```

## Repeticao de 10%

```bash
PYTHONPATH=src python3 scripts/run_repetition_check.py \
  --csv-output results/processed/repetition_check_results.csv \
  --jsonl-output results/raw/repetition_check_logs.jsonl
```

## Calcular metricas

```bash
PYTHONPATH=src python3 scripts/calculate_metrics.py
```

Saidas:

- `results/processed/summary.csv`
- `results/processed/metrics.csv`

## Gerar artefatos de analise

```bash
PYTHONPATH=src python3 scripts/generate_analysis_artifacts.py
```

Saidas:

- `results/processed/analysis_tables.md`
- `results/processed/analysis_tables.csv`
- `results/processed/representative_failures.csv`

## Pre-categorizar falhas

```bash
PYTHONPATH=src python3 scripts/precategorize_failures.py
```

Saida:

- `results/processed/representative_failures_precategorized.csv`

