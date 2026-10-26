import unittest
from pathlib import Path


class PriceAnalysisTests(unittest.TestCase):
    def test_all_required_price_queries_exist(self) -> None:
        sql = Path("sql/price_analysis.sql").read_text(encoding="utf-8")
        for section in (
            "preco_medio_por_tecnologia",
            "preco_por_marca",
            "preco_por_modelo",
            "volume_x_preco",
        ):
            self.assertIn(f"[{section}]", sql)

    def test_price_queries_use_gold_and_preserve_reference_semantics(self) -> None:
        sql = Path("sql/price_analysis.sql").read_text(encoding="utf-8")
        self.assertIn("gold.fato_precos", sql)
        self.assertIn("gold.fato_emplacamentos", sql)
        self.assertIn("price_type = 'REFERENCE'", sql)
        self.assertIn("LEFT JOIN prices", sql)
        self.assertNotIn("SELECT *", sql.upper())


if __name__ == "__main__":
    unittest.main()
