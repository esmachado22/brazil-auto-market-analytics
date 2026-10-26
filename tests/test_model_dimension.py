import csv
import tempfile
import unittest
from pathlib import Path

from src.transformations.model_dimension import build_from_silver, build_model_dimension, model_key, normalize_model


class ModelDimensionTests(unittest.TestCase):
    def test_normalize_model_and_key(self) -> None:
        self.assertEqual(normalize_model("  T-Cross "), "T-CROSS")
        self.assertEqual(model_key("MARCA_1", "T-CROSS"), model_key("MARCA_1", "T-CROSS"))

    def test_build_dimension_links_model_to_brand(self) -> None:
        rows = build_model_dimension(
            [
                {"brand_original": "VW", "model_original": "T CROSS", "category_standardized": "AUTOMOVEIS", "source_name": "FENABRAVE", "reference_period": "2026-01", "source_file": "a.pdf"},
                {"brand_original": "VW", "model_original": "T CROSS", "category_standardized": "AUTOMOVEIS", "source_name": "FENABRAVE", "reference_period": "2026-01", "source_file": "a.pdf"},
            ]
        )

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["brand_standardized"], "VOLKSWAGEN")
        self.assertEqual(rows[0]["model_standardized"], "T CROSS")
        self.assertTrue(rows[0]["marca_key"].startswith("MARCA_"))

    def test_build_from_silver_writes_dimension(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            ranking = root / "ranking.csv"
            with ranking.open("w", newline="", encoding="utf-8") as file_obj:
                writer = csv.DictWriter(file_obj, fieldnames=["brand_original", "model_original", "category_standardized", "source_name", "reference_period", "source_file"])
                writer.writeheader()
                writer.writerow({"brand_original": "VW", "model_original": "POLO", "category_standardized": "AUTOMOVEIS", "source_name": "FENABRAVE", "reference_period": "2026-01", "source_file": "a.pdf"})
            output = root / "dim_modelo.csv"

            report = build_from_silver(ranking, output_path=output)

            self.assertEqual(report["status"], "PASS")
            self.assertTrue(output.is_file())


if __name__ == "__main__":
    unittest.main()
