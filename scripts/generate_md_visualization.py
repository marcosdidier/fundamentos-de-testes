import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_FILE = ROOT / "data" / "transformed" / "transformed_dataset_v2.csv"
MD_FILE = ROOT / "data" / "transformed" / "transformed_dataset_v2_visualizacao.md"

def main():
    if not CSV_FILE.exists():
        print(f"Error: {CSV_FILE} does not exist.")
        return

    with CSV_FILE.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Let's write a clean markdown table
    with MD_FILE.open("w", encoding="utf-8") as f:
        f.write("# Visualização do Dataset Transformado v2\n\n")
        f.write("Esta tabela contém os 350 casos de teste gerados para a v2.\n\n")
        f.write("| ID do Caso | Tipo de Transformação | Texto Original | Texto Transformado | Rótulo Esperado |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- |\n")
        
        for r in rows:
            # Escape pipe symbols in markdown
            case_id = r["case_id"]
            trans_type = r["transformation_type"]
            orig_text = r["original_text"].replace("|", "\\|")
            trans_text = r["transformed_text"].replace("|", "\\|")
            label = r["expected_label"]
            f.write(f"| `{case_id}` | `{trans_type}` | {orig_text} | **{trans_text}** | `{label}` |\n")

    print(f"wrote={MD_FILE}")

if __name__ == "__main__":
    main()
