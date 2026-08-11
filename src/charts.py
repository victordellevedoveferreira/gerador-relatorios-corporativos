from __future__ import annotations

from pathlib import Path

import pandas as pd


PRIMARY = "#0B3B60"
ACCENT = "#00A6A6"
MUTED = "#DCE7F0"


def _matplotlib():
    try:
        import matplotlib.pyplot as plt
    except ImportError as error:
        raise RuntimeError("Instale matplotlib com 'pip install -r requirements.txt' para gerar os graficos.") from error
    return plt


def create_charts(monthly: pd.DataFrame, areas: pd.DataFrame, output_dir: Path) -> dict[str, Path]:
    plt = _matplotlib()
    output_dir.mkdir(parents=True, exist_ok=True)

    plt.style.use("default")
    revenue_path = output_dir / "receita_mensal.png"
    figure, axis = plt.subplots(figsize=(10, 4.7), facecolor="white")
    axis.plot(monthly["mes"], monthly["receita_liquida"], color=PRIMARY, linewidth=3, marker="o")
    axis.fill_between(monthly["mes"], monthly["receita_liquida"], color=ACCENT, alpha=0.16)
    axis.set_title("Receita liquida por mes", loc="left", fontsize=16, fontweight="bold", color=PRIMARY)
    axis.set_ylabel("Receita (R$)")
    axis.grid(axis="y", color=MUTED)
    axis.spines[["top", "right", "left"]].set_visible(False)
    axis.tick_params(axis="x", rotation=35)
    figure.tight_layout()
    figure.savefig(revenue_path, dpi=180, bbox_inches="tight")
    plt.close(figure)

    area_path = output_dir / "receita_por_area.png"
    sorted_areas = areas.sort_values("receita_liquida")
    figure, axis = plt.subplots(figsize=(9.5, 4.7), facecolor="white")
    bars = axis.barh(sorted_areas["area"], sorted_areas["receita_liquida"], color=[ACCENT if index == len(sorted_areas) - 1 else PRIMARY for index in range(len(sorted_areas))])
    axis.set_title("Receita acumulada por area", loc="left", fontsize=16, fontweight="bold", color=PRIMARY)
    axis.set_xlabel("Receita liquida (R$)")
    axis.grid(axis="x", color=MUTED)
    axis.spines[["top", "right", "bottom"]].set_visible(False)
    for bar, value in zip(bars, sorted_areas["receita_liquida"]):
        axis.text(value, bar.get_y() + bar.get_height() / 2, f" R$ {value:,.0f}", va="center", color=PRIMARY, fontsize=9)
    figure.tight_layout()
    figure.savefig(area_path, dpi=180, bbox_inches="tight")
    plt.close(figure)

    return {"receita_mensal": revenue_path, "receita_por_area": area_path}
