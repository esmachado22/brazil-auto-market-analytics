import unittest
from pathlib import Path


class AnalyticsQueriesTests(unittest.TestCase):
    def test_required_query_sections_exist(self) -> None:
        sql = Path("sql/analysis_queries.sql").read_text(encoding="utf-8")
        sections = (
            "top_10_modelos", "top_10_marcas", "volume_mensal_oficial",
            "market_share_segmentos", "crescimento_mensal_oficial",
            "combustao_hibrido_eletrico", "tecnologias_abve", "evolucao_eletrificados",
        )
        for section in sections:
            self.assertIn(f"[{section}]", sql)

    def test_queries_use_traceable_tables_and_no_select_star(self) -> None:
        sql = Path("sql/analysis_queries.sql").read_text(encoding="utf-8")
        self.assertIn("gold.fato_emplacamentos", sql)
        self.assertIn("gold.fato_eletrificados", sql)
        self.assertIn("silver.fenabrave_segment_totals", sql)
        self.assertNotIn("SELECT *", sql.upper())


if __name__ == "__main__":
    unittest.main()
