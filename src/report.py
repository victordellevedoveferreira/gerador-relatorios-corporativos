from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.analysis import ExecutiveMetrics


def _fpdf():
    try:
        from fpdf import FPDF
    except ImportError as error:
        raise RuntimeError("Instale fpdf2 com 'pip install -r requirements.txt' para exportar o PDF.") from error
    return FPDF


def _currency(value: float) -> str:
    return f"R$ {value:,.0f}".replace(",", ".")


def build_pdf(
    metrics: ExecutiveMetrics,
    monthly: pd.DataFrame,
    insights: list[str],
    charts: dict[str, Path],
    output: Path,
) -> None:
    FPDF = _fpdf()
    output.parent.mkdir(parents=True, exist_ok=True)
    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.add_page()

    pdf.set_fill_color(11, 59, 96)
    pdf.rect(0, 0, 210, 38, style="F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_xy(15, 12)
    pdf.cell(0, 8, "Relatorio Executivo Mensal")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_xy(15, 23)
    pdf.cell(0, 6, "Dados sinteticos | Gerado automaticamente")

    pdf.set_text_color(11, 59, 96)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_xy(15, 49)
    pdf.cell(0, 8, "Resumo do periodo")

    cards = [
        ("Receita liquida", _currency(metrics.receita_liquida)),
        ("Margem bruta", _currency(metrics.margem_bruta)),
        ("Margem", f"{metrics.margem_percentual:.1%}"),
        ("Ticket medio", _currency(metrics.ticket_medio)),
    ]
    x_positions = [15, 63, 111, 159]
    for x, (label, value) in zip(x_positions, cards):
        pdf.set_fill_color(237, 245, 250)
        pdf.rounded_rect(x, 61, 38, 27, 3, style="F")
        pdf.set_text_color(84, 110, 122)
        pdf.set_font("Helvetica", "", 8)
        pdf.set_xy(x + 3, 66)
        pdf.cell(32, 5, label)
        pdf.set_text_color(11, 59, 96)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_xy(x + 3, 74)
        pdf.cell(32, 6, value)

    pdf.set_font("Helvetica", "B", 13)
    pdf.set_xy(15, 98)
    pdf.cell(0, 7, "Principais insights")
    pdf.set_text_color(38, 50, 56)
    pdf.set_font("Helvetica", "", 10)
    for insight in insights:
        pdf.set_x(18)
        pdf.multi_cell(172, 6, f"- {insight}")

    pdf.add_page()
    pdf.set_text_color(11, 59, 96)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_xy(15, 15)
    pdf.cell(0, 8, "Desempenho e tendencia")
    pdf.image(str(charts["receita_mensal"]), x=15, y=28, w=180)
    pdf.image(str(charts["receita_por_area"]), x=15, y=128, w=180)

    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(100, 116, 139)
    pdf.set_xy(15, 273)
    pdf.cell(0, 5, "Projeto de portfolio - dados ficticios para demonstracao.")
    pdf.output(str(output))
