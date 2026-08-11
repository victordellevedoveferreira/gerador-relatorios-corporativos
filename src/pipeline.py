from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from src.analysis import build_insights, calculate_metrics, prepare_transactions, summarize_areas, summarize_clients, summarize_monthly
from src.charts import create_charts
from src.generate_data import generate_transactions, save_transactions
from src.report import build_pdf


ROOT = Path(__file__).resolve().parents[1]


def run(regenerate: bool, generate_artifacts: bool) -> None:
    raw_path = ROOT / "data/raw/transacoes.csv"
    if regenerate or not raw_path.exists():
        save_transactions(generate_transactions(), raw_path)

    raw = pd.read_csv(raw_path)
    prepared = prepare_transactions(raw)
    monthly = summarize_monthly(prepared)
    areas = summarize_areas(prepared)
    clients = summarize_clients(prepared)
    metrics = calculate_metrics(prepared, monthly)
    insights = build_insights(metrics, monthly, areas, clients)

    processed_dir = ROOT / "data/processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    prepared.to_csv(processed_dir / "transacoes_tratadas.csv", index=False, encoding="utf-8-sig")
    monthly.to_csv(processed_dir / "desempenho_mensal.csv", index=False, encoding="utf-8-sig")
    areas.to_csv(processed_dir / "desempenho_por_area.csv", index=False, encoding="utf-8-sig")
    clients.to_csv(processed_dir / "principais_clientes.csv", index=False, encoding="utf-8-sig")
    (processed_dir / "metricas.json").write_text(
        json.dumps({"metricas": metrics.to_dict(), "insights": insights}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    if generate_artifacts:
        charts = create_charts(monthly, areas, ROOT / "outputs/charts")
        build_pdf(metrics, monthly, insights, charts, ROOT / "outputs/pdf/relatorio_mensal.pdf")

    print("Pipeline concluido.")
    for insight in insights:
        print(f"- {insight}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gera relatorios corporativos a partir de dados mensais.")
    parser.add_argument("--regenerate", action="store_true", help="Regenera a base sintetica antes de processar.")
    parser.add_argument("--no-artifacts", action="store_true", help="Processa os dados sem gerar graficos e PDF.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run(regenerate=args.regenerate, generate_artifacts=not args.no_artifacts)
