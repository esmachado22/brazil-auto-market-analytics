import csv
import tempfile
import unittest
from pathlib import Path

from src.transformations.brand_dimension import (
    brand_key,
    build_brand_dimension,
    build_from_silver,
    normalize_brand,
)


class BrandDimensionTests(unittest.TestCase):
    def test_normalize_brand_preserves_unknown_identity(self) -> None:
        self.assertEqual(normalize_brand("VW"), "VOLKSWAGEN")
        self.assertEqual(normalize_brand("M.Benz"), "MERCEDES-BENZ")
        self.assertEqual(normalize_brand("CAOA Chery"), "CAOA CHERY")
        self.assertEqual(normalize_brand(None), "NAO_INFORMADA")

    def test_brand_key_is_deterministic(self) -> None:
        self.assertEqual(brand_key("VOLKSWAGEN"), brand_key("VOLKSWAGEN"))
        self.assertNotEqual(brand_key("VOLKSWAGEN"), brand_key("TOYOTA"))

    def test_build_dimension_groups_original_aliases(self) -> None:
        rows = build_brand_dimension(
            [
                {"brand_original": "VW", "source_name": "FENABRAVE", "reference_period": "2026-01", "source_file": "a.pdf"},
                {"brand_original": "VW", "source_name": "FENABRAVE", "reference_period": "2026-01", "source_file": "a.pdf"},
                {"brand_original": "TOYOTA", "source_name": "FENABRAVE", "reference_period": "2026-01", "source_file": "a.pdf"},
            ]
        )

        self.assertEqual(len(rows), 2)
        volkswagen = next(row for row in rows if row["brand_standardized"] == "VOLKSWAGEN")
        self.assertEqual(volkswagen["brand_originals"], "VW")

    def test_build_from_silver_writes_unique_dimension(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            ranking = root / "model_rankings.csv"
            with ranking.open("w", newline="", encoding="utf-8") as file_obj:
                writer = csv.DictWriter(file_obj, fieldnames=["brand_original", "source_name", "reference_period", "source_file"])
                writer.writeheader()
                writer.writerow({"brand_original": "VW", "source_name": "FENABRAVE", "reference_period": "2026-01", "source_file": "a.pdf"})
                writer.writerow({"brand_original": "TOYOTA", "source_name": "FENABRAVE", "reference_period": "2026-01", "source_file": "a.pdf"})
            output = root / "dim_marca.csv"

            report = build_from_silver(ranking, output_path=output)

            self.assertEqual(report["status"], "PASS")
            self.assertTrue(output.is_file())


if __name__ == "__main__":
    unittest.main()
