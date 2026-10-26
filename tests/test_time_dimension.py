import csv
import tempfile
import unittest
from pathlib import Path

from src.transformations.time_dimension import (
    build_from_silver,
    build_time_dimension,
    discover_periods,
    write_time_dimension,
)


class TimeDimensionTests(unittest.TestCase):
    def test_build_time_dimension_is_inclusive_and_has_quarters(self) -> None:
        rows = build_time_dimension("2025-12", "2026-02")

        self.assertEqual([row["reference_period"] for row in rows], ["2025-12", "2026-01", "2026-02"])
        self.assertEqual(rows[0]["quarter"], "Q4")
        self.assertEqual(rows[1]["quarter"], "Q1")
        self.assertEqual(rows[1]["year"], 2026)
        self.assertEqual(rows[1]["month"], 1)
        self.assertEqual(rows[1]["date_key"], "2026-01-01")

    def test_reversed_range_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            build_time_dimension("2026-02", "2026-01")

    def test_discover_periods_and_build_from_silver(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            path = root / "dataset.csv"
            path.write_text("reference_period,value\n2026-01,1\n2026-03,2\n", encoding="utf-8")

            self.assertEqual(discover_periods(root), ["2026-01", "2026-03"])
            rows = build_from_silver(root)
            self.assertEqual(len(rows), 3)
            self.assertEqual(rows[-1]["reference_period"], "2026-03")

    def test_write_time_dimension(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "dim_tempo.csv"
            write_time_dimension(build_time_dimension("2026-01", "2026-01"), path)

            with path.open(encoding="utf-8", newline="") as file_obj:
                rows = list(csv.DictReader(file_obj))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["reference_period"], "2026-01")


if __name__ == "__main__":
    unittest.main()
