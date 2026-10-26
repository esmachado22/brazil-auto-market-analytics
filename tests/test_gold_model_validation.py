import unittest

from src.quality.gold_model import validate_gold_records


class GoldModelValidationTests(unittest.TestCase):
    def _records(self) -> dict[str, list[dict[str, str]]]:
        return {
            "time_rows": [{"reference_period": "2026-01"}],
            "brand_rows": [{"marca_key": "MARCA_1"}],
            "model_rows": [{"modelo_key": "MODELO_1", "marca_key": "MARCA_1"}],
            "registration_rows": [{"emplacamento_key": "E1", "reference_period": "2026-01", "modelo_key": "MODELO_1", "marca_key": "MARCA_1", "rank": "1", "quantity": "10"}],
            "electrified_rows": [
                {"eletrificado_key": "X1", "reference_period": "2026-01", "category_original": "BEV", "quantity": "5"},
                {"eletrificado_key": "X2", "reference_period": "2026-01", "category_original": "PHEV", "quantity": "3"},
                {"eletrificado_key": "X3", "reference_period": "2026-01", "category_original": "HEV", "quantity": "1"},
                {"eletrificado_key": "X4", "reference_period": "2026-01", "category_original": "HEV Flex", "quantity": "1"},
                {"eletrificado_key": "X5", "reference_period": "2026-01", "category_original": "TOTAL", "quantity": "10"},
            ],
            "segment_rows": [{"segment_standardized": "TOTAL", "quantity_month": "100"}],
        }

    def test_valid_model_passes_relationships_and_reconciliation(self) -> None:
        report = validate_gold_records(**self._records())

        self.assertEqual(report["status"], "PASS")
        self.assertTrue(report["checks"]["abve_total_reconciles"])

    def test_missing_model_foreign_key_fails(self) -> None:
        records = self._records()
        records["registration_rows"][0]["modelo_key"] = "MISSING"

        report = validate_gold_records(**records)

        self.assertEqual(report["status"], "FAIL")
        self.assertIn("invalid_registration_model_fk:1", report["issues"])


if __name__ == "__main__":
    unittest.main()
