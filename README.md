# Testes Metamorficos em LLMs para Classificacao de Intencoes

Projeto experimental sobre tecnicas de teste para sistemas baseados em IA. O estudo avalia uma pequena aplicacao de classificacao de intencoes baseada em LLM no dominio de atendimento ao cliente em e-commerce.

## Objetivo

Avaliar se um sistema baseado em LLM mantem consistencia semantica ao classificar mensagens de clientes que expressam a mesma intencao de formas diferentes.

O experimento usa relacoes metamorficas para verificar se transformacoes controladas na entrada preservam o rotulo esperado de classificacao.

## Escopo experimental

- Dominio: atendimento ao cliente em e-commerce.
- Idioma: portugues.
- Classificacao: single-label.
- Modelo: `claude-haiku-4-5`.
- Parametros: `temperature=0`, `max_tokens=64`.
- Estrategias de prompt: livre, estrito em JSON e few-shot.
- Rotulos: 7 classes.
- Dataset original: 70 mensagens, 10 por classe.
- Transformacoes: 350 casos.
- Execucoes principais: 1260 chamadas.
- Repeticao de nao determinismo: 10% da base, tres vezes.

## Principais resultados

| Metrica | Resultado |
| --- | ---: |
| Execucoes principais | 1260 |
| Custo total estimado | US$ 0.366396 |
| Invalid Output Rate | 0.3333 |
| Metamorphic Violation Rate | 0.3648 |
| Prediction Flip Rate | 0.0129 |

Taxa de violacao por estrategia:

| Estrategia | Taxa |
| --- | ---: |
| `few_shot` | 0.0200 |
| `strict` | 0.0743 |
| `free` | 1.0000 |

O melhor resultado foi obtido pelo prompt `few_shot`, que manteve saidas validas e apresentou a menor taxa de violacao. O prompt livre foi inadequado para integracao programatica porque retornou texto livre em vez de JSON parseavel.

## Estrutura

```text
data/
  original/              Dataset original
  transformed/           Dataset transformado
docs/
  relatorio.md           Relatorio tecnico
  reproducao.md          Guia de reproducao
  artefatos.md           Indice dos artefatos
results/
  raw/                   Logs JSONL brutos
  processed/             CSVs processados, metricas e tabelas
scripts/                 Scripts de geracao, execucao e analise
src/                     Codigo da aplicacao experimental
tests/                   Testes automatizados
```

## Reproducao

Crie um arquivo `.env` a partir de `.env.example`:

```bash
cp .env.example .env
```

Preencha `ANTHROPIC_API_KEY` no `.env`.

### Validação Local (Testes)
```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

### Reprodução dos Experimentos (v1 e v2)

1. **Gerar Datasets Transformados (v1 e v2):**
   ```bash
   python3 scripts/generate_transformed_dataset.py --version all
   ```

2. **Executar Coleta Completa (v2 - Padrão/Recomendado):**
   ```bash
   PYTHONPATH=src python3 scripts/run_experiment.py --version v2 --dataset all
   ```
   *(Para rodar o Experimento v1 original: `PYTHONPATH=src python3 scripts/run_experiment.py --version v1 --dataset all`)*

3. **Gerar Relatórios de Análise e Tabelas:**
   ```bash
   PYTHONPATH=src python3 scripts/analyze_experiments.py
   ```

Instrucoes completas estao em [reproducao.md](file:///c:/Users/walte/OneDrive/Desktop/faculdade/fundamentos_software/fundamentos-de-testes/docs/reproducao.md).

## Documentacao

- Relatorio tecnico: `docs/relatorio.md`.
- Guia de reproducao: `docs/reproducao.md`.
- Indice de artefatos: `docs/artefatos.md`.
- Backlog e rastreabilidade: `BACKLOG.md`.

## Limitacoes

As conclusoes se restringem ao dominio de atendimento ao cliente em e-commerce, ao conjunto de sete rotulos definido e ao modelo `claude-haiku-4-5` com os parametros usados neste experimento.

