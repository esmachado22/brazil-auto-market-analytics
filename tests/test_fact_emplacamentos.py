import csv
import tempfile
import unittest
from pathlib import Path

from src.transformations.fact_emplacamentos import build_fact_records, build_from_silver


class FactEmplacamentosTests(unittest.TestCase):
    def setUp(self) -> None:
        self.ranking = [
            {
                "reference_period": "2026-01",
                "brand_original": "VW",
                "model_original": "POLO",
                "category_standardized": "AUTOMOVEIS",
                "rank": "1",
                "quantity": "5699",
                "source_name": "FENABRAVE",
                "source_url": "https://example.org/report.pdf",
                "source_file": "report.pdf",
                "source_page": "6",
                "source_hash": "abc",
            }
        ]
        self.model_dimension = [
            {
                "modelo_key": "MODELO_1",
                "marca_key": "MARCA_1",
                "brand_standardized": "VOLKSWAGEN",
                "model_standardized": "POLO",
            }
        ]

    def test_build_fact_links_model_and_preserves_unknown_technology(self) -> None:
        facts = build_fact_records(self.ranking, self.model_dimension)

        self.assertEqual(len(facts), 1)
        self.assertEqual(facts[0]["marca_key"], "MARCA_d0cfa362f594")
        self.assertEqual(facts[0]["modelo_key"], "MODELO_1")
        self.assertEqual(facts[0]["technology_standardized"], "NAO_INFORMADO")
        self.assertEqual(facts[0]["quantity"], 5699)

    def test_build_from_silver_writes_fact(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            ranking_path = root / "ranking.csv"
            model_path = root / "models.csv"
            output = root / "fact.csv"
            with ranking_path.open("w", newline="", encoding="utf-8") as file_obj:
                writer = csv.DictWriter(file_obj, fieldnames=self.ranking[0].keys())
                writer.writeheader()
                writer.writerow(self.ranking[0])
            with model_path.open("w", newline="", encoding="utf-8") as file_obj:
                writer = csv.DictWriter(file_obj, fieldnames=self.model_dimension[0].keys())
                writer.writeheader()
                writer.writerow(self.model_dimension[0])

            report = build_from_silver(ranking_path, model_path, output)

            self.assertEqual(report["status"], "PASS")
            self.assertTrue(output.is_file())

    def test_build_from_silver_reads_multiple_periods(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            silver_root = root / "silver"
            for period in ("2026-01", "2026-02"):
                period_root = silver_root / period
                period_root.mkdir(parents=True)
                ranking = dict(self.ranking[0])
                ranking["reference_period"] = period
                ranking["source_file"] = f"{period}.pdf"
                with (period_root / "model_rankings.csv").open("w", newline="", encoding="utf-8") as file_obj:
                    writer = csv.DictWriter(file_obj, fieldnames=ranking.keys())
                    writer.writeheader()
                    writer.writerow(ranking)

            model_path = root / "models.csv"
            output = root / "fact.csv"
            with model_path.open("w", newline="", encoding="utf-8") as file_obj:
                writer = csv.DictWriter(file_obj, fieldnames=self.model_dimension[0].keys())
                writer.writeheader()
                writer.writerow(self.model_dimension[0])

            report = build_from_silver(None, model_path, output, silver_root=silver_root)

            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["row_count"], 2)


if __name__ == "__main__":
    unittest.main()
