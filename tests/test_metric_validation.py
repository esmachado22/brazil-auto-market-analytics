import unittest

from src.quality.metric_validation import validate_metric_records


class MetricValidationTests(unittest.TestCase):
    def _records(self) -> dict[str, list[dict[str, str]]]:
        return {
            "fenabrave_segment_rows": [{"segment_standardized": "TOTAL", "quantity_month": "100"}],
            "fenabrave_registration_rows": [{"quantity": "60"}],
            "abve_source_rows": [
                {"category_original": "BEV", "aggregation_level": "TECHNOLOGY", "included_in_electrified_total": "True", "quantity": "6"},
                {"category_original": "PHEV", "aggregation_level": "TECHNOLOGY", "included_in_electrified_total": "True", "quantity": "2"},
                {"category_original": "TOTAL", "aggregation_level": "TOTAL", "included_in_electrified_total": "False", "quantity": "8"},
                {"category_original": "MHEV", "aggregation_level": "TECHNOLOGY", "included_in_electrified_total": "False", "quantity": "3"},
                {"category_original": "MHEV 48V", "aggregation_level": "SUBCATEGORY", "included_in_electrified_total": "False", "quantity": "2"},
                {"category_original": "MHEV 12V", "aggregation_level": "SUBCATEGORY", "included_in_electrified_total": "False", "quantity": "1"},
            ],
            "abve_gold_rows": [
                {"category_original": "BEV", "aggregation_level": "TECHNOLOGY", "included_in_electrified_total": "True", "quantity": "6"},
                {"category_original": "PHEV", "aggregation_level": "TECHNOLOGY", "included_in_electrified_total": "True", "quantity": "2"},
                {"category_original": "TOTAL", "aggregation_level": "TOTAL", "included_in_electrified_total": "False", "quantity": "8"},
            ],
        }

    def test_valid_metrics_pass_and_keep_ranked_subset_note(self) -> None:
        report = validate_metric_records(**self._records())

        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["comparisons"][-2]["source_value"], 8)
        self.assertTrue(report["limitations"])

    def test_abve_mismatch_fails(self) -> None:
        records = self._records()
        records["abve_gold_rows"][0]["quantity"] = "7"

        report = validate_metric_records(**records)

        self.assertEqual(report["status"], "FAIL")
        self.assertIn("abve_category_mismatch:BEV", report["issues"])


if __name__ == "__main__":
    unittest.main()
