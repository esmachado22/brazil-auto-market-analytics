import tempfile
import unittest
from pathlib import Path

from src.ingestion.fenabrave import (
    FenabraveReport,
    build_spec,
    discover_reports,
    validate_pdf,
)
from src.ingestion.framework import IngestionError, IngestionRecord


class FenabraveIngestionTests(unittest.TestCase):
    def test_discover_reports_extracts_unique_monthly_pdfs(self) -> None:
        html = """
        <a href="/portal/files/2026_02_02.pdf">Download</a>
        <a href="/portal/files/2026_01_02.pdf">Download</a>
        <a href="/portal/files/2026_01_02.pdf">Duplicate</a>
        <a href="http://www.fenabrave.org.br/portal/files/2025_12_02.pdf">HTTP link</a>
        <a href="https://example.org/not-a-report.pdf">Other</a>
        <a href="/portal/files/manual.pdf">Manual</a>
        """

        reports = discover_reports(html)

        self.assertEqual(
            [report.reference_period for report in reports],
            ["2025-12", "2026-01", "2026-02"],
        )
        self.assertEqual(reports[1].source_file, "2026_01_02.pdf")
        self.assertEqual(
            reports[0].source_url,
            "https://www.fenabrave.org.br/portal/files/2025_12_02.pdf",
        )

    def test_build_spec_uses_period_partition_in_bronze(self) -> None:
        report = FenabraveReport(
            reference_period="2026-01",
            source_url="https://example.org/2026_01_02.pdf",
            source_file="2026_01_02.pdf",
        )

        spec = build_spec(report, destination_root=Path("data/bronze/fenabrave"))

        self.assertEqual(spec.source_name, "FENABRAVE")
        self.assertEqual(spec.destination_dir, Path("data/bronze/fenabrave/2026-01"))

    def test_validate_pdf_rejects_non_pdf(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "report.pdf"
            path.write_bytes(b"not a pdf")
            record = IngestionRecord(
                source_name="FENABRAVE",
                source_url="https://example.org/report.pdf",
                reference_period="2026-01",
                source_file="report.pdf",
                local_path=str(path),
                metadata_path=str(path) + ".metadata.json",
                file_hash="unused",
                file_size_bytes=path.stat().st_size,
                ingestion_timestamp="2026-10-26T00:00:00+00:00",
            )

            with self.assertRaises(IngestionError):
                validate_pdf(record)

    def test_validate_pdf_accepts_pdf_signature(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "report.pdf"
            path.write_bytes(b"%PDF-1.7\nexample")
            record = IngestionRecord(
                source_name="FENABRAVE",
                source_url="https://example.org/report.pdf",
                reference_period="2026-01",
                source_file="report.pdf",
                local_path=str(path),
                metadata_path=str(path) + ".metadata.json",
                file_hash="unused",
                file_size_bytes=path.stat().st_size,
                ingestion_timestamp="2026-10-26T00:00:00+00:00",
            )

            validate_pdf(record)


if __name__ == "__main__":
    unittest.main()
