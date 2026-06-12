# Resumo Conclusivo: Experimento de Testes Metamórficos (v1 vs v2)

Este documento apresenta o resumo conclusivo consolidado das descobertas, métricas e lições aprendidas a partir do Experimento v2 de Testes Metamórficos de Classificação de Intenções.

---

## 1. O Contexto do Experimento v2
O Experimento v2 foi desenvolvido com o objetivo de aumentar o realismo e a robustez dos testes de metamorfismo aplicados ao classificador de intenções baseado no modelo `claude-haiku-4-5`.
*   **Paráfrases por IA:** Substituímos as paráfrases da v1 (que eram baseadas em prefixos mecânicos repetitivos e simplistas) por paráfrases fluidas, diversas e semanticamente ricas, geradas por inteligência artificial.
*   **Validação Humana:** O dataset original foi validado por **2 integrantes do grupo (de um total de 4)**, resolvendo de forma consensual discrepâncias semânticas e estabelecendo um padrão-ouro de rótulos esperados.
*   **Foco Estruturado:** Excluímos a estratégia de prompt livre (`free`) — que já havia se provado inviável para integração programática devido à formatação de texto livre — focando apenas em saídas estruturadas em JSON (`strict` e `few_shot`).

---

## 2. Principais Indicadores e Resultados
A execução das **840 novas chamadas de API** demonstrou que o dataset v2 é substancialmente mais desafiador:
1.  **Aumento nas Violações Metamórficas:** A taxa de violação geral subiu de **4.71%** para **7.57%**. Isso é um **indicador positivo de qualidade do teste**: o dataset v2 é mais rigoroso e eficiente em expor a sensibilidade do LLM a variações naturais da língua.
2.  **Aumento nos Flips de Predição:** A taxa de inversão de classe (quando uma mesma frase com mudança sutil de pontuação/paráfrase muda de classificação) subiu de **1.29%** para **3.00%**.
3.  **Supremacia do Few-Shot:** A estratégia `few_shot` continuou muito superior à `strict`, com uma taxa de violação de apenas **5.71%** (contra **9.43%** da strict), reforçando que o aprendizado em contexto é essencial para estabilizar o comportamento do modelo.

---

## 3. Diagnóstico de Falhas (Causas Raiz)
A análise detalhada identificou três categorias principais de falha semântica:

*   **A Vulnerabilidade da Classe `other` (Outros):**
    O LLM tende a classificar dúvidas sobre políticas do site, horário de atendimento ou saudações como `account_support` ou `product_information`. A classe `other`, por ser generalista, não possui uma fronteira semântica forte para o modelo.
*   **Desalinhamento de Intuição Humana vs Computacional:**
    O grupo reclassificou sugestões/feedbacks do app como `account_support`. No entanto, a IA continuou classificando-as estritamente como `other`. Isso mostra que o modelo separa rigidamente a intenção de "enviar ideias" da intenção de "solicitar suporte".
*   **Gatilhos de Vocabulário Específico:**
    A inclusão da palavra *"transação"* nas paráfrases de cancelamento de pedido (`cancel_order`) fez com que a IA classificasse as frases como problema de pagamento (`payment_issue`), demonstrando como palavras individuais com forte apelo financeiro podem induzir o modelo ao erro.

---

## 4. Conclusão Geral e Próximos Passos
O estudo valida que **testes metamórficos com paráfrases realistas são indispensáveis** para mapear as fragilidades de LLMs em produção. 

Como próximos passos para aumentar a consistência do sistema de atendimento:
1.  **Refinamento de Prompts:** Incorporar exemplos negativos ou limites claros para as classes `other` e `account_support` na instrução do prompt `few_shot`.
2.  **Subdivisão de Categorias:** Quebrar a categoria `other` em subcategorias mais específicas (ex: "comercial", "institucional") para evitar o transbordo semântico para suporte de conta.
