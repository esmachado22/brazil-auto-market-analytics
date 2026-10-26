import csv
import tempfile
import unittest
from pathlib import Path

from src.transformations.fact_eletrificados import build_fact_records, build_from_silver


class FactEletrificadosTests(unittest.TestCase):
    def setUp(self) -> None:
        self.record = {
            "reference_period": "2026-08",
            "category_original": "MHEV",
            "technology_standardized": "HIBRIDO",
            "aggregation_level": "TECHNOLOGY",
            "is_component": "False",
            "included_in_electrified_total": "False",
            "quantity": "6669",
            "share_pct": "",
            "source_name": "ABVE",
            "source_url": "https://example.org/article.html",
            "source_file": "abve.html",
            "source_locator": "article_body:mhev_summary",
            "source_hash": "abc",
        }

    def test_build_fact_preserves_mhev_exclusion(self) -> None:
        facts = build_fact_records([self.record])

        self.assertEqual(len(facts), 1)
        self.assertFalse(facts[0]["included_in_electrified_total"])
        self.assertEqual(facts[0]["quantity"], 6669)

    def test_build_from_silver_writes_fact(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            technology = root / "technology.csv"
            with technology.open("w", newline="", encoding="utf-8") as file_obj:
                writer = csv.DictWriter(file_obj, fieldnames=self.record.keys())
                writer.writeheader()
                writer.writerow(self.record)
            output = root / "fact.csv"

            report = build_from_silver(technology, output)

            self.assertEqual(report["status"], "PASS")
            self.assertTrue(output.is_file())


if __name__ == "__main__":
    unittest.main()
