# Guia de Estudo para Apresentação
## Testes Metamórficos em LLMs para Classificação de Intenções

> **Como usar este documento:** Leia na ordem das seções. Cada seção corresponde a uma parte da apresentação. Os destaques em negrito são os pontos que o professor provavelmente vai perguntar.

---

## 1. O Problema: Por que testar LLMs é difícil?

Sistemas baseados em LLMs não têm um **oráculo determinístico claro**. Em software tradicional, você sabe o output correto para um input. Com um LLM, o output é probabilístico e em linguagem natural — como saber se está certo?

### A abordagem escolhida: Testes Metamórficos

**Testes metamórficos** são uma técnica para sistemas onde o oráculo é difícil de definir. Em vez de verificar se o output é "correto" em termos absolutos, verificamos se ele é **consistente** com relações conhecidas entre inputs.

**Intuição:** Se eu perguntar _"Como rastrear meu pedido?"_ e depois perguntar _"Onde está a minha encomenda?"_, um classificador de intenções confiável deve retornar o mesmo rótulo para ambas as frases.

### Relações Metamórficas Avaliadas (MR)

| Relação | Nome | Exemplo |
| :--- | :--- | :--- |
| **MR1** | Invariância a Paráfrases | "Quero cancelar" ≈ "Preciso anular meu pedido" |
| **MR2** | Invariância a Pontuação | "quero cancelar." ≈ "quero cancelar!" |
| **MR3** | Invariância a Capitalização | "quero cancelar" ≈ "QUERO CANCELAR" |

> **Ponto-chave para a apresentação:** A propriedade metamórfica é: _"se a intenção semântica é a mesma, o rótulo deve ser o mesmo"_. Uma **violação metamórfica** ocorre quando a frase transformada recebe um rótulo diferente da original.

---

## 2. O Sistema Sob Teste (SUT)

### Arquitetura
- **Tarefa:** Classificação single-label de intenções em mensagens de atendimento ao cliente de e-commerce.
- **Idioma:** Português.
- **Modelo:** `claude-haiku-4-5` (Anthropic).
- **Parâmetros:** `temperature=0`, `max_tokens=64`.
- **Saída esperada:** Objeto JSON `{"label": "<classe>"}`.

### Os 7 Rótulos de Classificação

| Rótulo | Descrição |
| :--- | :--- |
| `refund_request` | Pedido de reembolso |
| `cancel_order` | Cancelamento de pedido |
| `delivery_problem` | Problema com entrega |
| `payment_issue` | Problema com pagamento |
| `product_information` | Informação sobre produto |
| `account_support` | Suporte de conta |
| `other` | Outros (categoria generalista) |

### Estratégias de Prompt Testadas

1. **`free` (Livre):** Apenas instrução em linguagem natural, sem restrição de formato.
2. **`strict` (Estrito JSON):** Instrução explícita para retornar JSON exato.
3. **`few_shot`:** Instrução + exemplos de entrada/saída antes da pergunta.

---

## 3. O Dataset

### Dataset Original
- **70 mensagens** em português, **10 por classe** (distribuição balanceada).
- Criadas e validadas pelo grupo. 2 integrantes realizaram revisão consensual para resolver discrepâncias de anotação.

### Transformações Geradas (350 casos)

| Tipo | Quantidade | Técnica |
| :--- | :---: | :--- |
| Paráfrases Semânticas | 210 (3 por mensagem) | Geração por IA (v2) ou prefixo mecânico (v1) |
| Alteração de Pontuação | 70 (1 por mensagem) | Troca de pontuação final |
| Alteração de Capitalização | 70 (1 por mensagem) | Caixa alta/baixa |

### Evolução: v1 → v2

Este é um ponto central da apresentação. O experimento foi realizado em **duas versões**:

**v1 — Paráfrases Mecânicas (prefixo fixo):**
- Cada paráfrase era criada adicionando um prefixo padrão à frase original.
- Exemplo de paráfrase de `cancel_order`: _"Preciso que a loja providencie o cancelamento, pois quero cancelar meu pedido."_
- **Problema:** As frases tinham viés de palavras-chave forte, tornando o teste fácil demais para o modelo.

**v2 — Paráfrases por IA (naturalísticas):**
- Paráfrases geradas pelo próprio LLM com variação sintática e lexical real.
- Exemplo de paráfrase de `cancel_order`: _"Por favor, suspendam a transação que acabei de concluir."_
- **Resultado:** Dataset mais realista, que expõe melhor as fragilidades do modelo.

> **Ponto-chave:** A v2 não é "pior" porque tem mais violações — ela é **melhor como ferramenta de teste** porque é mais rigorosa.

---

## 4. Execução dos Experimentos

### Escala Total

| Experimento | Chamadas de API | Estratégias |
| :--- | :---: | :--- |
| v1 (original, 3 prompts) | 1.260 | free + strict + few_shot |
| v2 (refinado, 2 prompts) | 840 | strict + few_shot |
| Verificação de Não-Determinismo (v1) | 378 | free + strict + few_shot |
| **TOTAL** | **2.478** | — |

### Verificação de Não-Determinismo
- 10% da base foi repetida **3 vezes** com `temperature=0`.
- **Resultado:** 0 variações observadas. O modelo é completamente determinístico com essa configuração.

---

## 5. Resultados do Experimento v1 (3 estratégias)

### Taxa de Violação Metamórfica

| Estratégia | Violações | Total | Taxa |
| :--- | :---: | :---: | :---: |
| `few_shot` | 7 | 350 | **2,0%** |
| `strict` | 26 | 350 | **7,4%** |
| `free` | 350 | 350 | **100%** |

> **Por que `free` foi 100%?** O prompt livre retornou texto explicativo, nunca JSON. Como o parser esperava `{"label": "..."}`, **todas as respostas foram inválidas** — ou seja, violação garantida por falha de formato, não por erro semântico.

### Taxa de Invalidade por Estratégia

| Estratégia | Saídas Inválidas | Taxa |
| :--- | :---: | :---: |
| `few_shot` | 0 / 420 | **0%** |
| `strict` | 0 / 420 | **0%** |
| `free` | 420 / 420 | **100%** |

### Lição Aprendida (v1)
**O design do prompt é parte essencial da engenharia de sistemas LLM.** Sem instrução de formato, o modelo não pode ser integrado programaticamente.

---

## 6. Resultados do Experimento v2 (2 estratégias)

### Comparação Direta v1 vs v2 (excluindo `free`)

| Métrica | v1 (sem `free`) | v2 | Variação |
| :--- | :---: | :---: | :---: |
| Taxa de Violação Geral | 4,71% (33/700) | **7,57% (53/700)** | +2,86% |
| Taxa de Flip de Predição | 1,29% (9/700) | **3,00% (21/700)** | +1,71% |
| Saídas Inválidas (JSON) | 0 | 0 | — |
| Custo Total API | $0.2087 | $0.2059 | -$0.003 |

### Violações por Estratégia (v2)

| Estratégia | Violações | Total | Taxa |
| :--- | :---: | :---: | :---: |
| `few_shot` | 20 | 350 | **5,71%** |
| `strict` | 33 | 350 | **9,43%** |

### Violações por Tipo de Transformação (v2 vs v1)

| Transformação | Taxa v1 | Taxa v2 |
| :--- | :---: | :---: |
| Paráfrases | 4,29% | **7,86%** |
| Pontuação | 5,00% | **6,43%** |
| Capitalização | 5,71% | **7,86%** |

> **Interpretação:** O aumento é esperado e desejável — significa que o dataset v2 é mais eficiente em revelar fragilidades reais do modelo.

---

## 7. Análise de Causa Raiz das Falhas

Esta é a parte mais rica analiticamente. As 53 violações da v2 foram investigadas e classificadas em 3 causas raiz.

### Causa 1: A Fragilidade da Categoria `other` (Generalista)

**Magnitude:** 40 das 53 violações (75%).

**O que aconteceu:** O LLM insistiu em categorizar mensagens do dataset como `other` em classes mais específicas.

| Mensagem `other` | Classificado como |
| :--- | :--- |
| "Qual o horário de atendimento?" | `account_support` |
| "Vocês têm parceria com outras empresas?" | `product_information` |
| "Política de privacidade do site" | `account_support` |

**Por quê:** A categoria `other` não tem fronteira semântica clara para um LLM treinado em dados gerais do mundo. O modelo usa seu conhecimento para reclassificar em categorias mais específicas.

**Lição:** Classes generalistas como `other` devem ser muito bem definidas no prompt ou subdivididas em subcategorias.

---

### Causa 2: Desalinhamento Humano vs IA (`account_support` ← `other`)

**Magnitude:** 10 das 53 violações (exclusivas da v2).

**O que aconteceu:** O grupo reclassificou manualmente a mensagem `orig_other_005` de `other` para `account_support`:
> _"Gostaria de deixar uma sugestão para melhorar o aplicativo."_

**Raciocínio do grupo:** Sugestão sobre o app = interação com a conta = `account_support`.

**Raciocínio do modelo:** Sugestão/feedback genérico sobre o produto = `other`.

**Resultado:** O modelo discordou sistematicamente da reclassificação humana, gerando 10 violações (1 original + 3 paráfrases × 2 estratégias + erros adicionais).

**Lição:** O desalinhamento entre anotadores humanos e LLMs é uma fonte real de erros. A subjetividade na anotação de rótulos limítrofes é um desafio real em NLP.

---

### Causa 3: Gatilho de Vocabulário Financeiro (`cancel_order` → `payment_issue`)

**Magnitude:** 3 das 53 violações (exclusivas da v2).

**O que aconteceu:** Paráfrases naturalísticas de `cancel_order` incluíram a palavra **"transação"**:
- _"Por favor, suspendam a **transação** que acabei de concluir."_
- _"Preciso anular a **transação** que fiz no dia de hoje."_

**Resultado:** O modelo classificou como `payment_issue` — confundindo cancelamento com problema de pagamento.

**Lição:** A escolha lexical em paráfrases pode ativar associações semânticas fortes no modelo. Palavras financeiras como "transação" têm viés forte para categorias de pagamento.

---

## 8. Conclusões Finais

### O que o experimento provou

1. **Testes metamórficos são eficazes para LLMs.** Eles revelam inconsistências semânticas que testes unitários tradicionais não detectariam.

2. **O design do prompt é crítico.** A estratégia `free` falhou totalmente; `few_shot` foi a mais robusta.

3. **Paráfrases realistas são melhores para testes.** O dataset v2 (paráfrases por IA) expôs ~61% mais violações que o v1 (paráfrases mecânicas), confirmando que a qualidade das transformações importa.

4. **A classe `other` é estruturalmente problemática.** Ela concentra 75% de todas as falhas em ambos os experimentos.

5. **Com `temperature=0`, o modelo é determinístico.** Não há nondeterminismo a mitigar neste contexto.

### Recomendações Práticas

| Recomendação | Justificativa |
| :--- | :--- |
| Sempre usar `few_shot` em produção | Menor taxa de violação e saídas sempre válidas |
| Subdividir a categoria `other` | Evita 75% das falhas observadas |
| Revisar vocabulário das paráfrases | Palavras financeiras induzem classificação errada |
| Incluir exemplos negativos no prompt | Define melhor as fronteiras entre `other` e `account_support` |

### Limitações do Estudo
- Dataset pequeno (70 mensagens originais).
- Restrito ao domínio de e-commerce em português.
- Avaliado apenas com `claude-haiku-4-5`.
- Rótulos `other` têm subjetividade inerente.

---

## 9. Perguntas Frequentes de Banca

**Q: Por que usar testes metamórficos em vez de acurácia simples?**
> A: Porque não há um conjunto de respostas corretas absolutas — o oráculo é difícil de definir para LLMs. Testes metamórficos verificam *consistência* em vez de *correção absoluta*.

**Q: A taxa de violação mais alta no v2 significa que o modelo piorou?**
> A: Não. Significa que o *conjunto de testes* ficou mais difícil e mais realista. O v2 é melhor como instrumento de teste, não pior como resultado.

**Q: Por que excluíram o prompt `free` do v2?**
> A: Porque o v1 já provou que `free` é inviável programaticamente (100% de saídas inválidas). Incluí-lo no v2 adicionaria custo sem nenhum valor analítico.

**Q: O que é um "prediction flip"?**
> A: É quando a predição da frase transformada é diferente da predição da frase original (não do rótulo esperado). Mede instabilidade interna do modelo, independente de qual rótulo é o "certo".

**Q: Como a verificação de não-determinismo foi feita?**
> A: 10% da base foi executada 3 vezes. Com `temperature=0`, nenhuma variação foi observada — o modelo é completamente determinístico nessa configuração.

---

*Documento gerado como material de suporte para a apresentação do projeto de Fundamentos de Teste de Software.*
