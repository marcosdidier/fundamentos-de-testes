# Pendencias metodologicas

Itens marcados como pendentes no `BACKLOG.md` e que nao devem ser inventados durante a implementacao:

- Formato exato dos arquivos CSV e JSONL alem dos campos listados.

Itens resolvidos durante a implementacao:

- Nome exato do modelo Claude: `claude-haiku-4-5`.
- Valor numerico de `max_tokens`: 64.
- `estimated_cost`: calculado com `usage.input_tokens` e `usage.output_tokens`.
- `Token Usage`: registrado em `metadata.usage` nos logs JSONL.
