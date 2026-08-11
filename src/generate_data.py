from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


AREAS = ["Comercial", "Tecnologia", "Operacoes", "Marketing"]
CANAIS = ["Direto", "Parceiros", "Digital"]
REGIOES = ["Sudeste", "Sul", "Nordeste", "Centro-Oeste"]
CLIENTES = [
    "Alfa Industria",
    "Beta Logistica",
    "Crescer Educacao",
    "Delta Varejo",
    "Evo Saude",
    "Foco Energia",
    "Gama Servicos",
    "Horizonte Tech",
]
RESPONSAVEIS = ["Ana", "Bruno", "Carla", "Diego", "Elisa", "Felipe"]


def generate_transactions(seed: int = 42, months: int = 12) -> pd.DataFrame:
    """Cria transacoes sinteticas com sazonalidade e margem por area."""
    rng = np.random.default_rng(seed)
    periods = pd.period_range("2025-07", periods=months, freq="M")
    rows: list[dict[str, object]] = []
    transaction_id = 1000

    area_factor = {"Comercial": 1.20, "Tecnologia": 1.10, "Operacoes": 0.95, "Marketing": 0.78}
    margin_rate = {"Comercial": 0.44, "Tecnologia": 0.38, "Operacoes": 0.31, "Marketing": 0.27}

    for period_index, period in enumerate(periods):
        seasonality = 1 + (period_index * 0.018) + (0.07 if period.month in {11, 12} else 0)
        for _ in range(54):
            area = str(rng.choice(AREAS, p=[0.32, 0.28, 0.25, 0.15]))
            gross_value = float(rng.normal(17500 * area_factor[area] * seasonality, 3800))
            revenue = max(4500, round(gross_value, 2))
            discount = round(revenue * float(rng.uniform(0.01, 0.08)), 2)
            gross_margin = margin_rate[area] + float(rng.normal(0, 0.025))
            cost = round((revenue - discount) * (1 - gross_margin), 2)
            day = int(rng.integers(1, 26))

            rows.append(
                {
                    "id_transacao": f"TX-{transaction_id}",
                    "data": pd.Timestamp(period.year, period.month, day),
                    "area": area,
                    "canal": str(rng.choice(CANAIS)),
                    "regiao": str(rng.choice(REGIOES)),
                    "cliente": str(rng.choice(CLIENTES)),
                    "responsavel": str(rng.choice(RESPONSAVEIS)),
                    "receita_bruta": revenue,
                    "desconto": discount,
                    "custo": cost,
                }
            )
            transaction_id += 1

    return pd.DataFrame(rows).sort_values("data").reset_index(drop=True)


def save_transactions(frame: pd.DataFrame, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output, index=False, encoding="utf-8-sig")


if __name__ == "__main__":
    destination = Path("data/raw/transacoes.csv")
    save_transactions(generate_transactions(), destination)
    print(f"Base sintetica salva em {destination}")
