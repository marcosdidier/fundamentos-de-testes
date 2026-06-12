# Testes Metamórficos em LLMs para Classificação de Intenções

Projeto experimental sobre técnicas de teste de consistência semântica para classificadores de intenções baseados em Modelos de Linguagem de Grande Porte (LLMs). O estudo avalia o comportamento de um classificador de atendimento ao cliente de e-commerce sob perturbações de entrada.

---

## 🎯 Objetivo do Projeto

Avaliar a robustez e a consistência semântica de um classificador de intenções baseado em LLM (`claude-haiku-4-5`) em português. O projeto utiliza **Testes Metamórficos** para validar se alterações sintáticas e estruturais na mensagem do cliente mantêm a mesma intenção original de classificação (invariância semântica).

---

## 🔬 O que são Testes Metamórficos em LLMs?

Sistemas baseados em LLMs sofrem do **problema do oráculo**: não há um comportamento determinístico e absoluto que possa ser validado de forma convencional para entradas em linguagem natural. 

Os testes metamórficos mitigam essa limitação ao definir **Relações Metamórficas (MR)** entre inputs e outputs relacionados:

*   **MR1 (Paráfrase):** Se a mensagem for reescrita mantendo o mesmo significado, o rótulo da intenção deve ser idêntico.
*   **MR2 (Pontuação):** Alterações de pontuação final (ponto final, exclamação, interrogação) não devem alterar o rótulo.
*   **MR3 (Capitalização):** Alterar entre caixa alta, caixa baixa ou maiúscula inicial não deve afetar a intenção.

Uma **Violação Metamórfica** ocorre quando uma mensagem transformada (paráfrase, pontuação ou capitalização) recebe um rótulo diferente da mensagem original.

---

## 📊 Estrutura e Escopo do Experimento

O experimento foi desenvolvido e executado em duas fases evolutivas para aumentar o realismo e rigor metodológico:

### Comparativo de Escopo: v1 vs v2

| Configuração | Experimento v1 (Original) | Experimento v2 (Refinado) |
| :--- | :--- | :--- |
| **Origem do Dataset** | Gerado sinteticamente (Claude Opus 4.7) | Gerado por Gemini 3.5 Flash + Validação Humana |
| **Geração de Paráfrases** | Mecânica (uso de prefixos textuais fixos) | Naturalista (geração dinâmica por IA) |
| **Estratégias de Prompt** | `free` (Livre), `strict` (JSON), `few_shot` | `strict` (JSON) e `few_shot` (Foco estruturado) |
| **Fronteira Semântica** | Linha de base original de 7 classes | Classe `orig_other_005` refinada consensualmente |
| **Chamadas de API** | 1.260 | 840 |
| **Amostra de Repetição** | 10% da base executada 3× para não-determinismo | — (Consolidação de determinismo da v1 com `temp=0`) |

---

## 📈 Resultados Consolidados (Sem a estratégia `free`)

A tabela abaixo compara o desempenho das respostas estruturadas entre a versão mecânica (v1) e a versão naturalista de IA (v2):

| Métrica | Experimento v1 (Sem `free`) | Experimento v2 (Refinado) | Variação |
| :--- | :---: | :---: | :---: |
| **Execuções Principais** | 700 | 700 | — |
| **Taxa de Violação Geral** | 4,71% (33/700) | **7,57% (53/700)** | **+2,86%** |
| **Saídas Inválidas (JSON)** | 0% (0/700) | **0% (0/700)** | — |
| **Custo Estimado da API** | US$ 0.2087 | **US$ 0.2059** | -US$ 0.0028 |

### Violações por Estratégia de Prompt

| Estratégia | Taxa v1 (Mecânico) | Taxa v2 (Realista) | Variação |
| :--- | :---: | :---: | :---: |
| `few_shot` | 2,00% (7/350) | **5,71% (20/350)** | **+3,71%** |
| `strict` | 7,43% (26/350) | **9,43% (33/350)** | **+2,00%** |

### Violações por Tipo de Transformação

| Transformação | Taxa v1 (Mecânico) | Taxa v2 (Realista) | Variação |
| :--- | :---: | :---: | :---: |
| `capitalization` | 5,71% (8/140) | **7,86% (11/140)** | **+2,14%** |
| `paraphrase` | 4,29% (18/420) | **7,86% (33/420)** | **+3,57%** |
| `punctuation` | 5,00% (7/140) | **6,43% (9/140)** | **+1,43%** |

> **Nota Metodológica:** O aumento geral na taxa de violações metamórficas de **4,71% para 7,57%** na v2 é um **indicador positivo da qualidade do teste**. Paráfrases mais naturais e sintaticamente ricas são melhores em revelar inconsistências ocultas no comportamento do LLM do que prefixos mecânicos repetitivos.

---

## 🔍 Principais Lições e Causas de Falha

1.  **Vazamento Semântico da Classe `other`:** Cerca de 75% de todas as falhas ocorrem em mensagens rotuladas como "Outros". O modelo tende a associar dúvidas sobre horários ou políticas do site a classes como `account_support` ou `product_information` devido a sua semântica geral.
2.  **Gatilhos de Vocabulário:** A introdução de palavras como "transação" em pedidos de cancelamento (`cancel_order`) induz o LLM a classificá-los erroneamente como problemas de cobrança (`payment_issue`).
3.  **Supremacia do Few-Shot:** A estratégia `few_shot` foi consistentemente mais estável que a `strict` em ambas as versões do dataset.

---

## 📂 Estrutura do Repositório

```text
apresentacao/
  estudo_apresentacao.md   Guia completo de estudo para banca e apresentação de aula
data/
  original/                Dataset original (70 mensagens v1/v2)
  transformed/             Mensagens transformadas (v1/v2 e visualização tabular)
docs/
  relatorio.md             Relatório científico final do experimento
  reproducao.md            Guia detalhado para reprodução técnica do experimento
  artefatos.md             Índice completo de todos os arquivos gerados
notebooks/                 Diretório reservado para análises interativas
results/
  raw/                     Logs JSONL brutos das interações de API com Claude
  processed/               CSV compilados de execuções, falhas qualitativas e métricas
scripts/                   Scripts Python unificados e versionados
src/                       Código-fonte do classificador e infraestrutura de teste
tests/                     Testes de regressão automatizados (unittest)
```

---

## 🚀 Como Reproduzir o Experimento

### 1. Configuração do Ambiente

Crie o seu arquivo `.env` a partir do modelo disponibilizado:
```bash
cp .env.example .env
```
Preencha a sua chave da API da Anthropic no campo `ANTHROPIC_API_KEY`.

### 2. Executar os Testes Automatizados (Validação Local)
```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

### 3. Execução dos Fluxos do Experimento

Todos os scripts são parametrizados por flag para permitir a replicação total de ambas as versões (`v1` e `v2`):

*   **Gerar Datasets Transformados (v1 e v2):**
    ```bash
    python3 scripts/generate_transformed_dataset.py --version all
    ```
*   **Executar Coleta Completa (v2 - Recomendado):**
    ```bash
    PYTHONPATH=src python3 scripts/run_experiment.py --version v2 --dataset all
    ```
    *(Para rodar o Experimento v1 original: `PYTHONPATH=src python3 scripts/run_experiment.py --version v1 --dataset all`)*
*   **Processar e Gerar Tabelas Comparativas:**
    ```bash
    PYTHONPATH=src python3 scripts/analyze_experiments.py
    ```

Instruções e documentações de parâmetros completas estão em [reproducao.md](file:///c:/Users/walte/OneDrive/Desktop/faculdade/fundamentos_software/fundamentos-de-testes/docs/reproducao.md).

---

## 📚 Materiais de Apresentação e Estudo

Na pasta [apresentacao/](file:///c:/Users/walte/OneDrive/Desktop/faculdade/fundamentos_software/fundamentos-de-testes/apresentacao/) você encontrará:
*   [estudo_apresentacao.md](file:///c:/Users/walte/OneDrive/Desktop/faculdade/fundamentos_software/fundamentos-de-testes/apresentacao/estudo_apresentacao.md): Um guia narrativo detalhado focado em possíveis perguntas da banca de professores e as respostas sugeridas baseadas nos dados do projeto.
