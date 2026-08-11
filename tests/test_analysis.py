import unittest

import pandas as pd

from src.analysis import calculate_metrics, prepare_transactions, summarize_monthly


class AnalysisTest(unittest.TestCase):
    def setUp(self):
        self.raw = pd.DataFrame(
            [
                ["TX-1", "2026-01-10", "Comercial", "Direto", "Sudeste", "Alfa", "Ana", 1000, 50, 600],
                ["TX-2", "2026-01-20", "Tecnologia", "Digital", "Sul", "Beta", "Bruno", 2000, 100, 1200],
                ["TX-3", "2026-02-05", "Comercial", "Direto", "Sudeste", "Alfa", "Ana", 1500, 0, 800],
            ],
            columns=["id_transacao", "data", "area", "canal", "regiao", "cliente", "responsavel", "receita_bruta", "desconto", "custo"],
        )

    def test_calculates_revenue_and_margin(self):
        prepared = prepare_transactions(self.raw)
        self.assertEqual(950, prepared.loc[0, "receita_liquida"])
        self.assertEqual(350, prepared.loc[0, "margem_bruta"])

    def test_monthly_growth_and_metrics(self):
        prepared = prepare_transactions(self.raw)
        monthly = summarize_monthly(prepared)
        metrics = calculate_metrics(prepared, monthly)
        self.assertEqual(2, len(monthly))
        self.assertAlmostEqual(-0.47, float(monthly.iloc[1]["crescimento_receita"]), places=2)
        self.assertEqual(3, metrics.total_transacoes)

    def test_rejects_duplicate_ids(self):
        duplicated = pd.concat([self.raw, self.raw.iloc[[0]]], ignore_index=True)
        with self.assertRaises(ValueError):
            prepare_transactions(duplicated)
