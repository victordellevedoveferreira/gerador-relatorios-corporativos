from __future__ import annotations

from dataclasses import asdict, dataclass

import pandas as pd


REQUIRED_COLUMNS = {
    "id_transacao",
    "data",
    "area",
    "canal",
    "regiao",
    "cliente",
    "responsavel",
    "receita_bruta",
    "desconto",
    "custo",
}


@dataclass(frozen=True)
class ExecutiveMetrics:
    receita_liquida: float
    margem_bruta: float
    margem_percentual: float
    ticket_medio: float
    crescimento_mensal: float
    total_transacoes: int

    def to_dict(self) -> dict[str, float | int]:
        return asdict(self)


def prepare_transactions(frame: pd.DataFrame) -> pd.DataFrame:
    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(f"Colunas obrigatorias ausentes: {sorted(missing)}")

    result = frame.copy()
    result["data"] = pd.to_datetime(result["data"], errors="coerce")
    if result["data"].isna().any():
        raise ValueError("Existem datas invalidas na base.")
    if result["id_transacao"].duplicated().any():
        raise ValueError("Existem identificadores de transacao duplicados.")

    numeric_columns = ["receita_bruta", "desconto", "custo"]
    for column in numeric_columns:
        result[column] = pd.to_numeric(result[column], errors="coerce")
    if result[numeric_columns].isna().any().any():
        raise ValueError("Existem valores financeiros invalidos na base.")

    result["receita_liquida"] = result["receita_bruta"] - result["desconto"]
    result["margem_bruta"] = result["receita_liquida"] - result["custo"]
    if (result["receita_liquida"] <= 0).any():
        raise ValueError("A receita liquida deve ser maior que zero.")
    result["margem_percentual"] = result["margem_bruta"] / result["receita_liquida"]
    result["mes"] = result["data"].dt.to_period("M").astype(str)
    return result.sort_values("data").reset_index(drop=True)


def summarize_monthly(frame: pd.DataFrame) -> pd.DataFrame:
    monthly = (
        frame.groupby("mes", as_index=False)
        .agg(
            receita_liquida=("receita_liquida", "sum"),
            margem_bruta=("margem_bruta", "sum"),
            transacoes=("id_transacao", "count"),
        )
        .sort_values("mes")
    )
    monthly["margem_percentual"] = monthly["margem_bruta"] / monthly["receita_liquida"]
    monthly["crescimento_receita"] = monthly["receita_liquida"].pct_change().fillna(0)
    return monthly


def summarize_areas(frame: pd.DataFrame) -> pd.DataFrame:
    areas = (
        frame.groupby("area", as_index=False)
        .agg(receita_liquida=("receita_liquida", "sum"), margem_bruta=("margem_bruta", "sum"))
        .sort_values("receita_liquida", ascending=False)
    )
    areas["margem_percentual"] = areas["margem_bruta"] / areas["receita_liquida"]
    return areas


def summarize_clients(frame: pd.DataFrame) -> pd.DataFrame:
    return (
        frame.groupby("cliente", as_index=False)
        .agg(receita_liquida=("receita_liquida", "sum"), margem_bruta=("margem_bruta", "sum"))
        .sort_values("receita_liquida", ascending=False)
        .head(5)
    )


def calculate_metrics(frame: pd.DataFrame, monthly: pd.DataFrame) -> ExecutiveMetrics:
    latest_growth = float(monthly.iloc[-1]["crescimento_receita"]) if len(monthly) > 1 else 0.0
    revenue = float(frame["receita_liquida"].sum())
    margin = float(frame["margem_bruta"].sum())
    return ExecutiveMetrics(
        receita_liquida=revenue,
        margem_bruta=margin,
        margem_percentual=margin / revenue,
        ticket_medio=revenue / len(frame),
        crescimento_mensal=latest_growth,
        total_transacoes=int(len(frame)),
    )


def build_insights(metrics: ExecutiveMetrics, monthly: pd.DataFrame, areas: pd.DataFrame, clients: pd.DataFrame) -> list[str]:
    best_area = areas.iloc[0]
    best_client = clients.iloc[0]
    latest_month = monthly.iloc[-1]
    previous_month = monthly.iloc[-2] if len(monthly) > 1 else latest_month
    direction = "cresceu" if metrics.crescimento_mensal >= 0 else "recuou"
    return [
        f"A receita do ultimo mes {direction} {abs(metrics.crescimento_mensal):.1%} frente ao mes anterior.",
        f"{best_area['area']} lidera a receita com R$ {best_area['receita_liquida']:,.0f} no periodo.",
        f"{best_client['cliente']} e o principal cliente, com R$ {best_client['receita_liquida']:,.0f} em receita liquida.",
        f"A margem consolidada foi de {metrics.margem_percentual:.1%}; o ultimo mes fechou em R$ {latest_month['margem_bruta']:,.0f} de margem bruta.",
        f"Foram processadas {metrics.total_transacoes} transacoes, com ticket medio de R$ {metrics.ticket_medio:,.0f}.",
    ]
