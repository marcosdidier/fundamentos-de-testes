import csv
from pathlib import Path
from collections import defaultdict, Counter

ROOT = Path(__file__).resolve().parents[1]
V1_RESULTS_PATH = ROOT / "results" / "processed" / "full_execution_results.csv"
V2_RESULTS_PATH = ROOT / "results" / "processed" / "v2_execution_results.csv"
REPORT_PATH = ROOT / "results" / "processed" / "failure_analysis_report.md"

def load_rows(path: Path):
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def get_violations(rows, exclude_free=True):
    violations = []
    for r in rows:
        if r["transformation_type"] == "original":
            continue
        if exclude_free and r["prompt_strategy"] == "free":
            continue
        if r["is_violation_expected_label"] == "True":
            violations.append(r)
    return violations

def analyze_v1_failures(viols):
    # Analyze where they went
    confusions = defaultdict(int)
    for v in viols:
        confusions[(v["expected_label"], v["parsed_label"])] += 1
    return confusions

def analyze_v2_failures(viols):
    confusions = defaultdict(int)
    for v in viols:
        confusions[(v["expected_label"], v["parsed_label"])] += 1
    return confusions

def main():
    v1_rows = load_rows(V1_RESULTS_PATH)
    v2_rows = load_rows(V2_RESULTS_PATH)

    v1_viols = get_violations(v1_rows, exclude_free=True)
    v2_viols = get_violations(v2_rows, exclude_free=False)

    v1_conf = analyze_v1_failures(v1_viols)
    v2_conf = analyze_v2_failures(v2_viols)

    with REPORT_PATH.open("w", encoding="utf-8") as f:
        f.write("# Análise Qualitativa de Falhas: Experimento v1 vs v2\n\n")
        f.write("Este relatório apresenta uma análise qualitativa das causas raiz de falhas de classificação e violações metamórficas nos dois experimentos (excluindo a estratégia `free` do v1).\n\n")

        f.write("## 1. Distribuição de Violações por Categoria Esperada\n\n")
        f.write("| Categoria Esperada | Violações v1 (Sem `free`) | Violações v2 | Variação |\n")
        f.write("| :--- | :---: | :---: | :---: |\n")
        
        all_categories = sorted(list({v["expected_label"] for v in v1_viols} | {v["expected_label"] for v in v2_viols}))
        for cat in all_categories:
            c1 = sum(1 for v in v1_viols if v["expected_label"] == cat)
            c2 = sum(1 for v in v2_viols if v["expected_label"] == cat)
            diff = c2 - c1
            f.write(f"| `{cat}` | {c1} | {c2} | {diff:+} |\n")
        f.write(f"| **TOTAL** | **{len(v1_viols)}** | **{len(v2_viols)}** | **+{len(v2_viols) - len(v1_viols)}** |\n\n")

        f.write("## 2. Padrões de Confusão do Modelo (Matriz de Erros)\n\n")
        f.write("Abaixo estão listadas as transições de classe mais frequentes onde o modelo desviou do rótulo esperado:\n\n")

        f.write("### Experimento v1 (Sem `free`)\n")
        f.write("| Rótulo Esperado -> Rótulo Classificado | Quantidade de Ocorrências |\n")
        f.write("| :--- | :---: |\n")
        for (expected, classified), count in sorted(v1_conf.items(), key=lambda x: x[1], reverse=True):
            f.write(f"| `{expected}` ➔ `{classified}` | {count} |\n")
        f.write("\n")

        f.write("### Experimento v2\n")
        f.write("| Rótulo Esperado -> Rótulo Classificado | Quantidade de Ocorrências |\n")
        f.write("| :--- | :---: |\n")
        for (expected, classified), count in sorted(v2_conf.items(), key=lambda x: x[1], reverse=True):
            f.write(f"| `{expected}` ➔ `{classified}` | {count} |\n")
        f.write("\n")

        f.write("## 3. Diagnóstico e Causa Raiz das Falhas\n\n")
        
        f.write("### Causa 1: Incoerência na Categoria Generalista (`other`)\n")
        f.write("- **O que aconteceu:** A maior parte de todas as falhas nos dois experimentos vem da categoria `other`. \n")
        f.write("- **Diagnóstico:** As mensagens classificadas em `other` na verdade possuem semânticas muito fortes de outras categorias na visão de mundo do LLM:\n")
        f.write("  - Perguntas sobre horário de atendimento da empresa (`orig_other_009`) e disponibilidade de atendente (`orig_other_010`) são logicamente classificadas como `account_support` pelo modelo.\n")
        f.write("  - Perguntas sobre parcerias comerciais (`orig_other_006`) são entendidas como `product_information` pelo modelo.\n")
        f.write("  - Links de política de privacidade (`orig_other_004`) são categorizados como `account_support` ou `product_information`.\n")
        f.write("  - **Conclusão:** O rótulo `other` é inerentemente problemático para LLMs se não for muito bem definido no prompt (ou se a mensagem for muito específica de atendimento técnico/comercial).\n\n")

        f.write("### Causa 2: Desalinhamento de Anotação Humana vs Entendimento da IA (`orig_other_005`)\n")
        f.write("- **O que aconteceu:** No v2, alteramos o rótulo de `orig_other_005` (*Gostaria de deixar uma sugestão para melhorar o aplicativo*) de `other` para `account_support` com base em discussões internas do grupo. No entanto, isso gerou **10 violações de teste**.\n")
        f.write("- **Diagnóstico:** O modelo `claude-haiku-4-5` insistiu em classificar esta frase e todas as suas paráfrases (ex: *'Como posso enviar um feedback com ideias para aperfeiçoar o app?'*) como `other` (ou seja, ele manteve a classificação original humana). Isso demonstra que o LLM não vê feedbacks ou sugestões gerais como suporte de conta técnico, gerando um desalinhamento sistemático com a nova anotação humana.\n\n")

        f.write("### Causa 3: Confusão Linguística de Vocabulário Financeiro (`cancel_order` ➔ `payment_issue`)\n")
        f.write("- **O que aconteceu:** No v2, tivemos **3 violações** na categoria `cancel_order` que foram rotuladas como `payment_issue`.\n")
        f.write("- **Diagnóstico:** Duas paráfrases de cancelamento introduziram a palavra **'transação'**:\n")
        f.write("  - *'Por favor, suspendam a transação que acabei de concluir.'*\n")
        f.write("  - *'Preciso anular a transação que fiz no dia de hoje.'*\n")
        f.write("  - A palavra 'transação' aciona um forte gatilho semântico ligado a questões financeiras e cobranças, fazendo com que o modelo associe a mensagem a `payment_issue` em vez de `cancel_order`. Isso mostra a sensibilidade do LLM ao vocabulário específico das paráfrases.\n")

    print(f"wrote={REPORT_PATH}")

if __name__ == "__main__":
    main()
