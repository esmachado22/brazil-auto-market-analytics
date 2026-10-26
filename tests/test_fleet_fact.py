import csv
import gzip
import tempfile
import unittest
from pathlib import Path

from src.transformations.fleet_fact import build_fleet_fact, fleet_key


class FleetFactTests(unittest.TestCase):
    def test_fleet_key_is_deterministic(self) -> None:
        row = {"reference_period": "2026-09", "uf": "SP", "municipio": "SAO PAULO", "brand_original": "TOYOTA", "model_original": "COROLLA", "year_manufacture": "2020"}
        self.assertEqual(fleet_key(row), fleet_key(dict(row)))

    def test_build_fact_marks_rows_as_stock(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "silver/senatran/2026-09/fleet_brand_model.csv.gz"
            source.parent.mkdir(parents=True)
            with gzip.open(source, "wt", encoding="utf-8", newline="") as file_obj:
                writer = csv.DictWriter(file_obj, fieldnames=["reference_period", "source_name", "source_url", "source_file", "source_hash", "uf", "municipio", "brand_original", "model_original", "year_manufacture", "quantity"])
                writer.writeheader()
                writer.writerow({"reference_period": "2026-09", "source_name": "SENATRAN_RENAVAM", "source_url": "https://example.org", "source_file": "frota.zip", "source_hash": "hash", "uf": "SP", "municipio": "SAO PAULO", "brand_original": "TOYOTA", "model_original": "COROLLA", "year_manufacture": "2020", "quantity": "10"})

            report = build_fleet_fact("2026-09", silver_root=root / "silver/senatran", gold_root=root / "gold")

            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["measure_type"], "ESTOQUE")
            with gzip.open(root / "gold/fato_frota.csv.gz", "rt", encoding="utf-8", newline="") as file_obj:
                row = next(csv.DictReader(file_obj))
            self.assertEqual(row["measure_type"], "ESTOQUE")
            self.assertEqual(row["quantity"], "10")


if __name__ == "__main__":
    unittest.main()
