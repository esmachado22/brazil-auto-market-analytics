import unittest

from src.transformations.fenabrave import (
    SourceMetadata,
    parse_ranking_words,
    parse_summary_lines,
    validate_silver,
)


class FenabraveSilverTests(unittest.TestCase):
    def setUp(self) -> None:
        self.metadata = SourceMetadata(
            source_name="FENABRAVE",
            source_url="https://example.org/report.pdf",
            reference_period="2026-01",
            source_file="2026_01_02.pdf",
            file_hash="abc123",
        )

    def test_parse_summary_converts_types_and_standardizes_segments(self) -> None:
        text = "A) Autos 125.136 210.714 125.136 123.344 123.344 -40,61 1,45 1,45\nTotal 366.713 492.473 366.713 341.394 341.394 -25,54 7,42 7,42"

        records = parse_summary_lines(text, metadata=self.metadata)

        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["segment_standardized"], "AUTOMOVEIS")
        self.assertEqual(records[0]["quantity_month"], 125136)
        self.assertEqual(records[0]["variation_vs_previous_month_pct"], -40.61)
        self.assertEqual(records[1]["segment_standardized"], "TOTAL")

    def test_parse_ranking_preserves_brand_model_and_quantity(self) -> None:
        words = [
            {"text": "1º", "x0": 76.0, "top": 100.0},
            {"text": "VW/T", "x0": 140.0, "top": 100.0},
            {"text": "CROSS", "x0": 180.0, "top": 100.0},
            {"text": "5.741", "x0": 245.0, "top": 100.0},
            {"text": "1º", "x0": 330.0, "top": 100.0},
            {"text": "FIAT/STRADA", "x0": 390.0, "top": 100.0},
            {"text": "10.541", "x0": 498.0, "top": 100.0},
        ]

        records = parse_ranking_words(words, metadata=self.metadata, source_page=6)

        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["brand_original"], "VW")
        self.assertEqual(records[0]["model_original"], "T CROSS")
        self.assertEqual(records[0]["quantity"], 5741)
        self.assertEqual(records[1]["category_standardized"], "COMERCIAIS_LEVES")

    def test_parse_summary_derives_total_when_report_has_only_components(self) -> None:
        text = "\n".join(
            (
                "A + B 100 90 190 80 160 11,11 25,00 18,75",
                "C + D 20 18 38 15 30 11,11 33,33 26,67",
                "E) Motos 50 45 95 40 80 11,11 25,00 18,75",
                "F) Impl. Rod. 5 4 9 3 7 25,00 66,67 28,57",
                "Outros 2 1 3 2 4 100,00 0,00 -25,00",
            )
        )

        records = parse_summary_lines(text, metadata=self.metadata)

        total = next(row for row in records if row["segment_standardized"] == "TOTAL")
        self.assertEqual(total["quantity_month"], 177)
        self.assertEqual(total["quantity_accumulated"], 335)

    def test_quality_validation_rejects_duplicate_keys(self) -> None:
        records = [
            {"reference_period": "2026-01", "source_file": "source.pdf", "rank": 1, "quantity": 10},
            {"reference_period": "2026-01", "source_file": "source.pdf", "rank": 1, "quantity": 11},
        ]

        quality = validate_silver(records, key_fields=("reference_period", "rank", "source_file"))

        self.assertEqual(quality["status"], "FAIL")
        self.assertEqual(quality["duplicate_count"], 1)


if __name__ == "__main__":
    unittest.main()
