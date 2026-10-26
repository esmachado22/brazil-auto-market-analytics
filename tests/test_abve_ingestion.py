import tempfile
import unittest
from pathlib import Path

from src.ingestion.abve import (
    ABVE_DEFAULT_REPORT_URL,
    AbveReport,
    build_report,
    build_spec,
    validate_html,
)
from src.ingestion.framework import IngestionError, IngestionRecord


class AbveIngestionTests(unittest.TestCase):
    def test_build_report_preserves_period_and_official_url(self) -> None:
        report = build_report("2026-08", ABVE_DEFAULT_REPORT_URL)

        self.assertEqual(report.reference_period, "2026-08")
        self.assertEqual(report.source_file, "abve_2026_08.html")
        self.assertTrue(report.source_url.startswith("https://abve.org.br/"))

    def test_build_spec_partitions_bronze_by_period(self) -> None:
        report = AbveReport(
            reference_period="2026-08",
            source_url=ABVE_DEFAULT_REPORT_URL,
            source_file="abve_2026_08.html",
        )

        spec = build_spec(report, destination_root=Path("data/bronze/abve"))

        self.assertEqual(spec.source_name, "ABVE")
        self.assertEqual(spec.destination_dir, Path("data/bronze/abve/2026-08"))

    def test_build_report_rejects_non_abve_url(self) -> None:
        with self.assertRaises(ValueError):
            build_report("2026-08", "https://example.org/report.html")

    def test_validate_html_requires_original_categories(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "abve_2026_08.html"
            path.write_text("<html>BEV PHEV HEV HEV Flex MHEV</html>", encoding="utf-8")
            record = IngestionRecord(
                source_name="ABVE",
                source_url=ABVE_DEFAULT_REPORT_URL,
                reference_period="2026-08",
                source_file=path.name,
                local_path=str(path),
                metadata_path=str(path) + ".metadata.json",
                file_hash="unused",
                file_size_bytes=path.stat().st_size,
                ingestion_timestamp="2026-10-26T00:00:00+00:00",
            )

            validate_html(record)

    def test_validate_html_rejects_missing_category(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "abve_2026_08.html"
            path.write_text("<html>BEV PHEV HEV HEV Flex</html>", encoding="utf-8")
            record = IngestionRecord(
                source_name="ABVE",
                source_url=ABVE_DEFAULT_REPORT_URL,
                reference_period="2026-08",
                source_file=path.name,
                local_path=str(path),
                metadata_path=str(path) + ".metadata.json",
                file_hash="unused",
                file_size_bytes=path.stat().st_size,
                ingestion_timestamp="2026-10-26T00:00:00+00:00",
            )

            with self.assertRaises(IngestionError):
                validate_html(record)


if __name__ == "__main__":
    unittest.main()
