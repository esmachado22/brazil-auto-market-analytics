import unittest

from src.transformations.abve import SourceMetadata, extract_text, parse_abve_text, validate_silver


class AbveSilverTests(unittest.TestCase):
    def setUp(self) -> None:
        self.metadata = SourceMetadata(
            source_name="ABVE",
            source_url="https://example.org/article.html",
            reference_period="2026-08",
            source_file="abve_2026_08.html",
            file_hash="abc123",
        )

    def test_extract_and_parse_original_categories(self) -> None:
        html = "<article>BEV: 27.166 (47,3%) PHEV: 20.535 (35,8%) HEV: 4.445 (7,8%) HEV Flex: 5.240 (9,1%) TOTAL: 57.386. Os MHEV) venderam 6.669 unidades. MHEV 48V com 4.017 unidades. MHEV 12V somaram 2.652 unidades.</article>"

        records = parse_abve_text(extract_text(html), metadata=self.metadata)
        by_category = {record["category_original"]: record for record in records}

        self.assertEqual(by_category["BEV"]["quantity"], 27166)
        self.assertEqual(by_category["HEV Flex"]["technology_standardized"], "HIBRIDO")
        self.assertFalse(by_category["MHEV"]["included_in_electrified_total"])
        self.assertEqual(by_category["MHEV 48V"]["quantity"], 4017)

    def test_quality_reconciles_electrified_and_mhev_totals(self) -> None:
        text = "BEV: 27.166 PHEV: 20.535 HEV: 4.445 HEV Flex: 5.240 TOTAL: 57.386 Os MHEV) venderam 6.669 unidades. MHEV 48V com 4.017 unidades. MHEV 12V somaram 2.652 unidades."
        records = parse_abve_text(text, metadata=self.metadata)

        quality = validate_silver(records)

        self.assertEqual(quality["status"], "PASS")
        self.assertEqual(quality["component_total"], 57386)
        self.assertTrue(quality["mhev_reconciles"])

    def test_quality_rejects_duplicate_categories(self) -> None:
        text = "BEV: 10 PHEV: 20 HEV: 30 HEV Flex: 40 TOTAL: 100"
        records = parse_abve_text(text, metadata=self.metadata)
        records.append(dict(records[0]))

        quality = validate_silver(records)

        self.assertEqual(quality["status"], "FAIL")
        self.assertEqual(quality["duplicate_count"], 1)


if __name__ == "__main__":
    unittest.main()
