import csv
import tempfile
import unittest
from pathlib import Path

from src.ingestion.fipe import IngestionError, is_official_url, validate_snapshot_row
from src.transformations.fipe import build_price_ranges, build_price_tables, price_key


class FipePriceTests(unittest.TestCase):
    def _row(self) -> dict[str, str]:
        return {
            "reference_period": "2026-10",
            "source_url": "https://veiculos.fipe.org.br/?carro/toyota/5-2020/002135-=",
            "fipe_code": "002135-0",
            "brand_original": "Toyota",
            "model_original": "Corolla",
            "model_year": "2020",
            "price_brl": "123.456,78",
            "consulted_at": "2026-10-26T00:00:00-03:00",
        }

    def test_only_official_https_hosts_are_accepted(self) -> None:
        self.assertTrue(is_official_url(self._row()["source_url"]))
        self.assertFalse(is_official_url("https://example.org/fipe"))

    def test_invalid_source_is_rejected(self) -> None:
        row = self._row()
        row["source_url"] = "https://example.org/fipe"
        with self.assertRaises(IngestionError):
            validate_snapshot_row(row)

    def test_build_price_tables_marks_reference_price(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            bronze = root / "bronze/fipe/2026-10"
            bronze.mkdir(parents=True)
            path = bronze / "snapshot.csv"
            with path.open("w", encoding="utf-8", newline="") as file_obj:
                writer = csv.DictWriter(file_obj, fieldnames=list(self._row()))
                writer.writeheader()
                writer.writerow(self._row())
            path.with_name(path.name + ".metadata.json").write_text(
                '{"source_file":"snapshot.csv","file_hash":"hash"}', encoding="utf-8"
            )

            report = build_price_tables("2026-10", bronze_root=root / "bronze/fipe", silver_root=root / "silver/fipe", gold_root=root / "gold")

            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["price_type"], "REFERENCE_RANGE_CENTRAL")
            with (root / "gold/fato_precos.csv").open(encoding="utf-8", newline="") as file_obj:
                row = next(csv.DictReader(file_obj))
            self.assertEqual(row["price_type"], "REFERENCE_RANGE_CENTRAL")
            self.assertEqual(row["price_brl"], "123456.78")
            self.assertEqual(row["price_min_brl"], "123456.78")
            self.assertEqual(row["price_max_brl"], "123456.78")
            self.assertEqual(row["variant_count"], "1")
            self.assertTrue(price_key(self._row()).startswith("PRECO_"))

    def test_build_price_ranges_keeps_min_max_and_midpoint(self) -> None:
        rows = [self._row(), {**self._row(), "fipe_code": "002135-1", "price_brl": "150.000,00"}]

        ranges = build_price_ranges(
            rows,
            metadata={"source_file": "snapshot.csv", "file_hash": "hash"},
            source_path=Path("snapshot.csv"),
        )

        self.assertEqual(len(ranges), 1)
        self.assertEqual(ranges[0]["variant_count"], 2)
        self.assertEqual(ranges[0]["price_min_brl"], 123456.78)
        self.assertEqual(ranges[0]["price_max_brl"], 150000.0)
        self.assertEqual(ranges[0]["price_central_brl"], 136728.39)


if __name__ == "__main__":
    unittest.main()
