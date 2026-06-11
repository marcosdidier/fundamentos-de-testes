---
marp: true
theme: default
paginate: true
backgroundColor: #0f172a
color: #e2e8f0
style: |
  section {
    font-family: 'Segoe UI', system-ui, sans-serif;
    padding: 48px 64px;
  }
  h1 { color: #38bdf8; font-size: 2em; margin-bottom: 0.2em; }
  h2 { color: #7dd3fc; border-bottom: 2px solid #334155; padding-bottom: 0.3em; }
  h3 { color: #93c5fd; }
  table { width: 100%; border-collapse: collapse; font-size: 0.85em; }
  th { background: #1e3a5f; color: #7dd3fc; padding: 8px 12px; text-align: left; }
  td { padding: 7px 12px; border-bottom: 1px solid #1e293b; }
  tr:nth-child(even) td { background: #111827; }
  code { background: #1e293b; color: #f472b6; padding: 2px 6px; border-radius: 4px; }
  blockquote { border-left: 4px solid #38bdf8; padding-left: 16px; color: #94a3b8; font-style: italic; }
  strong { color: #fbbf24; }
  .small { font-size: 0.8em; color: #64748b; }
---

<!-- slide 1: capa -->
# Testes Metamórficos em LLMs
## Classificação de Intenções em Atendimento ao Cliente

**Fundamentos de Teste de Software**

---

<!-- slide 2: agenda -->
## Agenda

1. 🎯 Problema e Motivação
2. 🔬 Testes Metamórficos — Conceito
3. 🛠️ Sistema Sob Teste (SUT)
4. 📊 Dataset e Transformações
5. 🧪 Experimento v1 — Resultados
6. ⚡ Experimento v2 — Refinamento
7. 🔍 Análise de Causa Raiz
8. ✅ Conclusões

---

<!-- slide 3: problema -->
## 1. O Problema

### Testar LLMs é diferente de testar software convencional

Em software tradicional:
> Input fixo → Output determinístico → Verificação direta

Em sistemas LLM:
> Input em linguagem natural → Resposta probabilística → **Oráculo é difícil de definir**

**Como saber se o sistema é consistente?**

---

<!-- slide 4: relacoes metamorficas -->
## 2. Testes Metamórficos

> _"Se a intenção é a mesma, o rótulo deve ser o mesmo."_

Em vez de verificar correção absoluta, verificamos **consistência** entre inputs relacionados.

| Relação | Transformação | Exemplo |
| :--- | :--- | :--- |
| **MR1** | Paráfrase semântica | "Quero cancelar" ≈ "Preciso anular meu pedido" |
| **MR2** | Alteração de pontuação | "Quero cancelar." ≈ "Quero cancelar!" |
| **MR3** | Alteração de capitalização | "quero cancelar" ≈ "QUERO CANCELAR" |

Uma **violação metamórfica** = rótulo da transformação ≠ rótulo da original.

---

<!-- slide 5: SUT -->
## 3. Sistema Sob Teste

| Configuração | Valor |
| :--- | :--- |
| Tarefa | Classificação single-label de intenções |
| Modelo | `claude-haiku-4-5` |
| Temperatura | `0` (determinístico) |
| Idioma | Português |
| Saída esperada | `{"label": "<classe>"}` |

### 7 Classes de Classificação

`refund_request` · `cancel_order` · `delivery_problem` · `payment_issue`
`product_information` · `account_support` · **`other`**

---

<!-- slide 6: estrategias de prompt -->
## 3. Estratégias de Prompt

| Estratégia | Descrição |
| :--- | :--- |
| `free` (Livre) | Instrução em linguagem natural, sem restrição de formato |
| `strict` (Estrito) | Exige retorno em JSON exato |
| `few_shot` | Instrução + exemplos de entrada/saída |

**Hipótese:** `few_shot` produzirá saídas mais estáveis e consistentes.

---

<!-- slide 7: dataset -->
## 4. Dataset e Transformações

### Dataset Original
- **70 mensagens** em português
- **10 por classe** (distribuição balanceada)
- Validadas consensualmente por 2 integrantes do grupo

### 350 Transformações Geradas

| Tipo | Quantidade |
| :--- | :---: |
| Paráfrases semânticas | **210** (3 por mensagem) |
| Alteração de pontuação | **70** (1 por mensagem) |
| Alteração de capitalização | **70** (1 por mensagem) |

---

<!-- slide 8: v1 vs v2 dataset -->
## 4. v1 vs v2 — Qualidade das Paráfrases

### v1 — Prefixo Mecânico (simplista)
> _"Preciso que a loja providencie o cancelamento, pois quero cancelar meu pedido."_

- Prefixo fixo + frase original
- Palavras-chave fortes e repetitivas
- **Teste fácil demais para o modelo**

### v2 — Geradas por IA (naturalísticas)
> _"Por favor, suspendam a transação que acabei de concluir."_

- Vocabulário diverso, estrutura sintática variada
- Sem viés de palavras-chave repetitivas
- **Teste mais rigoroso e realista**

---

<!-- slide 9: escala execucao -->
## 5. Escala de Execução

| Experimento | Chamadas de API | Estratégias |
| :--- | :---: | :--- |
| v1 (3 prompts) | **1.260** | free + strict + few_shot |
| v2 (2 prompts) | **840** | strict + few_shot |
| Verificação de Non-Det. | **378** | Amostra de 10%, repetida 3× |
| **TOTAL** | **2.478** | — |

**Verificação de não-determinismo:**
Com `temperature=0` → **0 variações** observadas em 378 execuções. O modelo é completamente determinístico.

---

<!-- slide 10: resultados v1 -->
## 5. Resultados v1 — Taxa de Violação

| Estratégia | Violações | Total | Taxa |
| :--- | :---: | :---: | :---: |
| `few_shot` | 7 | 350 | **2,0%** ✅ |
| `strict` | 26 | 350 | **7,4%** ⚠️ |
| `free` | 350 | 350 | **100%** ❌ |

### Por que `free` falhou 100%?
O prompt livre retornou **texto explicativo**, nunca JSON.
O parser esperava `{"label": "..."}` → **todas as respostas foram inválidas**.

> Lição: controle de formato de saída é parte essencial do design de sistemas LLM.

---

<!-- slide 11: comparacao v1 v2 -->
## 6. Comparação v1 vs v2 (sem `free`)

| Métrica | v1 | v2 | Δ |
| :--- | :---: | :---: | :---: |
| Taxa de Violação Geral | 4,71% | **7,57%** | +2,86% |
| Taxa de Flip de Predição | 1,29% | **3,00%** | +1,71% |
| Saídas Inválidas (JSON) | 0 | **0** | — |
| Custo Total API | $0.2087 | $0.2059 | −$0.003 |

**O aumento de violações na v2 é um indicador positivo:**
significa que o dataset v2 é mais rigoroso e eficiente em expor fragilidades reais.

---

<!-- slide 12: violacoes por estrategia v2 -->
## 6. Violações por Estratégia e Transformação (v2)

### Por Estratégia

| Estratégia | v1 | v2 | Δ |
| :--- | :---: | :---: | :---: |
| `few_shot` | 2,0% | **5,71%** | +3,71% |
| `strict` | 7,43% | **9,43%** | +2,0% |

### Por Tipo de Transformação

| Transformação | v1 | v2 |
| :--- | :---: | :---: |
| Paráfrases | 4,29% | **7,86%** |
| Pontuação | 5,00% | **6,43%** |
| Capitalização | 5,71% | **7,86%** |

---

<!-- slide 13: causa raiz 1 -->
## 7. Causa Raiz 1 — Vulnerabilidade da Classe `other`

**40 de 53 violações (75%)** originam da categoria `other`.

| Mensagem (rótulo: `other`) | Classificado como |
| :--- | :--- |
| "Qual o horário de atendimento?" | `account_support` |
| "Vocês têm parceria com outras empresas?" | `product_information` |
| "Gostaria de ver a política de privacidade." | `account_support` |

**Diagnóstico:** A categoria `other` não tem fronteira semântica clara.
O LLM usa seu conhecimento geral para reclassificar em categorias mais específicas.

> **Recomendação:** Subdividir `other` em subcategorias ou definir exemplos negativos no prompt.

---

<!-- slide 14: causa raiz 2 -->
## 7. Causa Raiz 2 — Desalinhamento Humano vs IA

**10 violações** (exclusivas da v2).

**Ação do grupo:** Reclassificamos `orig_other_005` de `other` → `account_support`:
> _"Gostaria de deixar uma sugestão para melhorar o aplicativo."_

**Raciocínio humano:** Sugestão sobre o app → interação com a conta → `account_support`.

**Raciocínio do modelo:** Feedback/sugestão genérica → `other`.

O modelo discordou sistematicamente da reclassificação.

> **Lição:** Rótulos limítrofes têm subjetividade real. O LLM não é neutro — ele tem sua própria semântica implícita.

---

<!-- slide 15: causa raiz 3 -->
## 7. Causa Raiz 3 — Gatilho de Vocabulário Financeiro

**3 violações** (`cancel_order` → `payment_issue`).

Paráfrases naturalísticas do v2 introduziram a palavra **"transação"**:

> _"Por favor, suspendam a **transação** que acabei de concluir."_
> _"Preciso anular a **transação** que fiz no dia de hoje."_

O modelo associou "transação" → `payment_issue` em vez de `cancel_order`.

**Diagnóstico:** Palavras com forte apelo financeiro ativam associações semânticas dominantes no modelo, sobrepondo o contexto da frase.

> **Lição:** A escolha lexical nas paráfrases influencia diretamente o resultado do teste.

---

<!-- slide 16: distribuicao falhas -->
## 7. Distribuição Consolidada das Falhas (v2)

| Categoria da Violação | Causa Raiz | Ocorrências |
| :--- | :--- | :---: |
| `other` → `account_support` | Fronteira semântica fraca da classe `other` | **30** |
| `other` → `product_information` | Fronteira semântica fraca da classe `other` | **10** |
| `account_support` → `other` | Desalinhamento anotação humana vs IA | **10** |
| `cancel_order` → `payment_issue` | Gatilho de vocabulário financeiro | **3** |
| **TOTAL** | | **53** |

---

<!-- slide 17: conclusoes -->
## 8. Conclusões

| # | Conclusão |
| :--- | :--- |
| 1 | Testes metamórficos são eficazes para mapear fragilidades de LLMs |
| 2 | O design do prompt (`few_shot`) é crítico para saídas programáticas |
| 3 | Paráfrases realistas (v2) revelam ~61% mais violações que mecânicas (v1) |
| 4 | A classe `other` concentra 75% de todas as falhas em ambos os experimentos |
| 5 | Com `temperature=0`, o modelo é 100% determinístico |

---

<!-- slide 18: recomendacoes -->
## 8. Recomendações para Produção

| Recomendação | Impacto Esperado |
| :--- | :--- |
| Usar sempre `few_shot` | Menor taxa de violação, saídas sempre válidas |
| Subdividir a classe `other` | Eliminar até 75% das violações observadas |
| Incluir exemplos negativos no prompt | Melhor definição de fronteiras entre classes |
| Auditar vocabulário das paráfrases | Evitar gatilhos lexicais indesejados |

---

<!-- slide 19: limitacoes -->
## 8. Limitações do Estudo

- 📌 Dataset pequeno (70 mensagens originais)
- 📌 Domínio restrito: e-commerce em português
- 📌 Apenas `claude-haiku-4-5` avaliado
- 📌 Rótulo `other` tem subjetividade inerente na anotação

### Trabalhos Futuros
- Avaliar outros modelos (GPT-4, Gemini, Llama)
- Expandir dataset com mensagens reais anonimizadas
- Aplicar em outros domínios (saúde, finanças, jurídico)
- Refinar a classe `other` em subcategorias

---

<!-- slide 20: encerramento -->
# Obrigado!

## Repositório do Projeto

```
https://github.com/[seu-usuario]/fundamentos-de-testes
```

**Para replicar o experimento:**
```bash
cp .env.example .env  # configure ANTHROPIC_API_KEY
python scripts/generate_transformed_dataset.py --version all
PYTHONPATH=src python scripts/run_experiment.py --version v2 --dataset all
PYTHONPATH=src python scripts/analyze_experiments.py
```

> Instruções completas em `docs/reproducao.md`

---

*Fundamentos de Teste de Software — 2026*
