import csv
import tempfile
import unittest
from pathlib import Path

from src.quality.validation import validate_csv, validate_records


class QualityValidationTests(unittest.TestCase):
    def test_valid_records_pass_all_checks(self) -> None:
        records = [
            {"reference_period": "2026-01", "category": "A", "quantity": "10", "source_file": "a.csv"},
            {"reference_period": "2026-02", "category": "A", "quantity": "20", "source_file": "a.csv"},
        ]

        report = validate_records(
            records,
            required_fields=("reference_period", "category", "quantity", "source_file"),
            key_fields=("reference_period", "category", "source_file"),
            quantity_field="quantity",
        )

        self.assertEqual(report["status"], "PASS")

    def test_required_nulls_invalid_period_negative_and_duplicates_fail(self) -> None:
        records = [
            {"reference_period": "2026-13", "category": "A", "quantity": "-1", "source_file": "a.csv"},
            {"reference_period": "2026-13", "category": "A", "quantity": "x", "source_file": "a.csv"},
        ]

        report = validate_records(
            records,
            required_fields=("reference_period", "category", "quantity", "source_file", "required"),
            key_fields=("reference_period", "category", "source_file"),
            quantity_field="quantity",
        )

        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["invalid_period_count"], 2)
        self.assertEqual(report["negative_quantity_count"], 1)
        self.assertEqual(report["invalid_quantity_count"], 1)
        self.assertEqual(report["duplicate_count"], 1)
        self.assertEqual(report["required_nulls"]["required"], 2)

    def test_validate_csv_reads_realistic_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "data.csv"
            with path.open("w", newline="", encoding="utf-8") as file_obj:
                writer = csv.DictWriter(file_obj, fieldnames=["reference_period", "category", "quantity", "source_file"])
                writer.writeheader()
                writer.writerow({"reference_period": "2026-01", "category": "A", "quantity": 1, "source_file": "a.csv"})

            report = validate_csv(
                path,
                required_fields=("reference_period", "category", "quantity", "source_file"),
                key_fields=("reference_period", "category", "source_file"),
                quantity_field="quantity",
            )

            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["row_count"], 1)


if __name__ == "__main__":
    unittest.main()
