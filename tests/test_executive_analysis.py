import unittest

from src.analysis.executive_analysis import AnalysisInputError, build_executive_analysis


class ExecutiveAnalysisTests(unittest.TestCase):
    def test_output_has_required_structured_fields_and_derived_movement(self) -> None:
        result = build_executive_analysis(
            [
                {"periodo": "2026-08", "metrica": "electrified_volume", "nome": "BEV", "valor": 27166, "fonte": "ABVE"},
                {"periodo": "2026-08", "metrica": "growth_pct", "nome": "BEV", "valor": 12.5, "fonte": "ABVE"},
            ]
        )
        self.assertEqual(result["periodo"], "2026-08")
        self.assertEqual(set(result), {"periodo", "resumo", "principais_movimentos", "dados_observados", "alertas"})
        self.assertEqual(result["principais_movimentos"][0]["direcao"], "crescimento")
        self.assertEqual(result["dados_observados"][0]["valor"], 27166.0)

    def test_unknown_metric_is_rejected_instead_of_invented(self) -> None:
        with self.assertRaises(AnalysisInputError):
            build_executive_analysis(
                [{"periodo": "2026-08", "metrica": "market_size_guess", "nome": "x", "valor": 1, "fonte": "unknown"}]
            )

    def test_mixed_periods_are_rejected(self) -> None:
        records = [
            {"periodo": "2026-07", "metrica": "volume", "nome": "total", "valor": 1, "fonte": "FENABRAVE"},
            {"periodo": "2026-08", "metrica": "volume", "nome": "total", "valor": 2, "fonte": "FENABRAVE"},
        ]
        with self.assertRaises(AnalysisInputError):
            build_executive_analysis(records)


if __name__ == "__main__":
    unittest.main()
