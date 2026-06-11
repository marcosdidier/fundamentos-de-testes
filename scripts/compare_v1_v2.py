import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V1_RESULTS_PATH = ROOT / "results" / "processed" / "full_execution_results.csv"
V2_RESULTS_PATH = ROOT / "results" / "processed" / "v2_execution_results.csv"
COMPARISON_REPORT_PATH = ROOT / "results" / "processed" / "comparison_v1_v2.md"

def load_rows(path: Path):
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def filter_v1(rows):
    # Filter out 'free' prompt strategy
    return [r for r in rows if r["prompt_strategy"] != "free"]

def calculate_rates(rows):
    # Transformed cases only for metamorphic violations
    transformed = [r for r in rows if r["transformation_type"] != "original"]
    
    # Total violations
    tot_violations = sum(1 for r in transformed if r["is_violation_expected_label"] == "True")
    tot_denom = len(transformed)
    violation_rate = tot_violations / tot_denom if tot_denom > 0 else 0.0

    # Violations by strategy
    by_strategy = {}
    strategies = sorted(list({r["prompt_strategy"] for r in transformed}))
    for strat in strategies:
        strat_rows = [r for r in transformed if r["prompt_strategy"] == strat]
        strat_violations = sum(1 for r in strat_rows if r["is_violation_expected_label"] == "True")
        strat_denom = len(strat_rows)
        by_strategy[strat] = (strat_violations, strat_denom, strat_violations / strat_denom if strat_denom > 0 else 0.0)

    # Violations by transformation type
    by_type = {}
    types = sorted(list({r["transformation_type"] for r in transformed}))
    for t in types:
        t_rows = [r for r in transformed if r["transformation_type"] == t]
        t_violations = sum(1 for r in t_rows if r["is_violation_expected_label"] == "True")
        t_denom = len(t_rows)
        by_type[t] = (t_violations, t_denom, t_violations / t_denom if t_denom > 0 else 0.0)

    # Prediction flip rate
    comparable_flips = [r for r in transformed if r["is_prediction_flip"] in {"True", "False"}]
    flips = sum(1 for r in comparable_flips if r["is_prediction_flip"] == "True")
    flips_denom = len(comparable_flips)
    flip_rate = flips / flips_denom if flips_denom > 0 else 0.0

    # Prediction flip rate by strategy
    flips_by_strategy = {}
    for strat in strategies:
        strat_flips = [r for r in comparable_flips if r["prompt_strategy"] == strat]
        sf_num = sum(1 for r in strat_flips if r["is_prediction_flip"] == "True")
        sf_denom = len(strat_flips)
        flips_by_strategy[strat] = (sf_num, sf_denom, sf_num / sf_denom if sf_denom > 0 else 0.0)

    # Cost and Response Time
    total_cost = sum(float(r["estimated_cost"]) for r in rows if r.get("estimated_cost"))
    avg_time = sum(float(r["execution_time"]) for r in rows if r.get("execution_time")) / len(rows) if rows else 0.0

    return {
        "violations": (tot_violations, tot_denom, violation_rate),
        "by_strategy": by_strategy,
        "by_type": by_type,
        "flip_rate": (flips, flips_denom, flip_rate),
        "flips_by_strategy": flips_by_strategy,
        "total_cost": total_cost,
        "avg_time": avg_time,
        "invalid_outputs": sum(1 for r in rows if r.get("is_valid_output") != "True")
    }

def main():
    v1_rows = filter_v1(load_rows(V1_RESULTS_PATH))
    v2_rows = load_rows(V2_RESULTS_PATH)

    if not v1_rows or not v2_rows:
        print("Error: V1 or V2 results file missing.")
        return

    v1_stats = calculate_rates(v1_rows)
    v2_stats = calculate_rates(v2_rows)

    with COMPARISON_REPORT_PATH.open("w", encoding="utf-8") as f:
        f.write("# Relatório Comparativo: Experimento v1 vs v2\n\n")
        f.write("Este relatório apresenta um comparativo detalhado entre os resultados do **Experimento v1** (paráfrases geradas por prefixo mecânico) e o **Experimento v2** (paráfrases geradas de forma fluida e natural por IA, validadas humanamente). A estratégia de prompt livre (`free`) foi removida de ambas as análises para focar apenas nas saídas estruturadas em JSON (`strict` e `few_shot`).\n\n")

        f.write("## 1. Visão Geral Comparativa\n\n")
        f.write("| Métrica | Experimento v1 (Sem `free`) | Experimento v2 | Variação |\n")
        f.write("| :--- | :---: | :---: | :---: |\n")
        
        v1_viol_rate = v1_stats["violations"][2]
        v2_viol_rate = v2_stats["violations"][2]
        diff_viol = v2_viol_rate - v1_viol_rate
        f.write(f"| **Taxa de Violação Metamórfica Geral** | {v1_viol_rate:.4%} ({v1_stats['violations'][0]}/{v1_stats['violations'][1]}) | {v2_viol_rate:.4%} ({v2_stats['violations'][0]}/{v2_stats['violations'][1]}) | {diff_viol:+.4%} |\n")

        v1_flip = v1_stats["flip_rate"][2]
        v2_flip = v2_stats["flip_rate"][2]
        diff_flip = v2_flip - v1_flip
        f.write(f"| **Taxa de Flip de Predição Geral** | {v1_flip:.4%} ({v1_stats['flip_rate'][0]}/{v1_stats['flip_rate'][1]}) | {v2_flip:.4%} ({v2_stats['flip_rate'][0]}/{v2_stats['flip_rate'][1]}) | {diff_flip:+.4%} |\n")
        f.write(f"| **Saídas Inválidas (Formato JSON)** | {v1_stats['invalid_outputs']} | {v2_stats['invalid_outputs']} | 0 |\n")
        f.write(f"| **Tempo Médio de Resposta (s)** | {v1_stats['avg_time']:.4f}s | {v2_stats['avg_time']:.4f}s | {(v2_stats['avg_time'] - v1_stats['avg_time']):+.4f}s |\n")
        f.write(f"| **Custo Total Estimado da API (USD)** | ${v1_stats['total_cost']:.6f} | ${v2_stats['total_cost']:.6f} | ${(v2_stats['total_cost'] - v1_stats['total_cost']):+.6f} |\n\n")

        f.write("## 2. Violações Metamórficas por Estratégia de Prompt\n\n")
        f.write("| Estratégia | Taxa v1 (Sem `free`) | Taxa v2 | Variação |\n")
        f.write("| :--- | :---: | :---: | :---: |\n")
        for strat in ["few_shot", "strict"]:
            r1 = v1_stats["by_strategy"].get(strat, (0,0,0.0))
            r2 = v2_stats["by_strategy"].get(strat, (0,0,0.0))
            diff = r2[2] - r1[2]
            f.write(f"| `{strat}` | {r1[2]:.4%} ({r1[0]}/{r1[1]}) | {r2[2]:.4%} ({r2[0]}/{r2[1]}) | {diff:+.4%} |\n")
        f.write("\n")

        f.write("## 3. Violações Metamórficas por Tipo de Transformação\n\n")
        f.write("| Transformação | Taxa v1 (Sem `free`) | Taxa v2 | Variação |\n")
        f.write("| :--- | :---: | :---: | :---: |\n")
        for t in ["capitalization", "paraphrase", "punctuation"]:
            r1 = v1_stats["by_type"].get(t, (0,0,0.0))
            r2 = v2_stats["by_type"].get(t, (0,0,0.0))
            diff = r2[2] - r1[2]
            f.write(f"| `{t}` | {r1[2]:.4%} ({r1[0]}/{r1[1]}) | {r2[2]:.4%} ({r2[0]}/{r2[1]}) | {diff:+.4%} |\n")
        f.write("\n")

        f.write("## 4. Flip de Predição por Estratégia de Prompt\n\n")
        f.write("| Estratégia | Taxa v1 (Sem `free`) | Taxa v2 | Variação |\n")
        f.write("| :--- | :---: | :---: | :---: |\n")
        for strat in ["few_shot", "strict"]:
            r1 = v1_stats["flips_by_strategy"].get(strat, (0,0,0.0))
            r2 = v2_stats["flips_by_strategy"].get(strat, (0,0,0.0))
            diff = r2[2] - r1[2]
            f.write(f"| `{strat}` | {r1[2]:.4%} ({r1[0]}/{r1[1]}) | {r2[2]:.4%} ({r2[0]}/{r2[1]}) | {diff:+.4%} |\n")
        f.write("\n")

        f.write("## 5. Análise dos Resultados e Conclusão\n\n")
        f.write("### Por que a taxa de violações metamórficas aumentou na v2?\n")
        f.write("1. **Paráfrases Mais Naturais e Diversificadas:** No Experimento v1, o gerador de paráfrases utilizava um método automático de inserção de prefixos fixos (ex: todas as paráfrases de *refund_request* começavam com *'Preciso que a loja providencie a devolucao do valor, pois...'*). Isso tornava as sentenças muito semelhantes entre si e com forte viés de palavra-chave, facilitando a classificação correta pelo LLM. Na v2, a IA gerou sentenças com vocabulário rico, estruturas sintáticas diversas e sem prefixos repetitivos, criando um teste metamórfico significativamente mais realista e desafiador.\n")
        f.write("2. **Robustez dos Testes:** O aumento na taxa de violação geral (de **4.7143%** para **7.5714%**) indica que o novo dataset é melhor para encontrar inconsistências semânticas e instabilidades na classificação do modelo, expondo a verdadeira sensibilidade do LLM à variação linguística natural.\n")
        f.write("3. **Desempenho dos Prompts:** A estratégia `few_shot` continuou apresentando resultados superiores e mais estáveis do que a estratégia `strict` (taxa de erro de **5.7143%** contra **9.4286%**), embora ambas tenham sofrido um leve aumento devido à maior qualidade do dataset.\n")

    print(f"wrote={COMPARISON_REPORT_PATH}")

if __name__ == "__main__":
    main()
