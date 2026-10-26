import json
import logging
import tempfile
import unittest
from pathlib import Path

from src.ingestion import (
    IngestionError,
    IngestionFramework,
    SourceFileExistsError,
    SourceSpec,
    sha256_file,
)


class IngestionFrameworkTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        logger = logging.getLogger(f"test-ingestion-{id(self)}")
        logger.addHandler(logging.NullHandler())
        self.framework = IngestionFramework(logger=logger)
        self.spec = SourceSpec(
            source_name="TEST_SOURCE",
            source_url="https://example.invalid/source.csv",
            reference_period="2026-01",
            source_file="source.csv",
            destination_dir=self.root / "data" / "raw",
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_ingest_local_file_writes_file_hash_and_metadata(self) -> None:
        source = self.root / "download" / "source.csv"
        source.parent.mkdir()
        source.write_text("id,value\n1,10\n", encoding="utf-8")

        record = self.framework.ingest_local_file(source, self.spec)

        destination = self.root / "data" / "raw" / "source.csv"
        metadata_path = destination.with_name("source.csv.metadata.json")
        self.assertTrue(destination.exists())
        self.assertTrue(metadata_path.exists())
        self.assertEqual(record.file_hash, sha256_file(destination))
        self.assertEqual(record.file_size_bytes, destination.stat().st_size)
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        self.assertEqual(metadata["source_name"], "TEST_SOURCE")
        self.assertEqual(metadata["reference_period"], "2026-01")

    def test_existing_destination_is_not_overwritten(self) -> None:
        destination = self.root / "data" / "raw" / "source.csv"
        destination.parent.mkdir(parents=True)
        destination.write_text("original", encoding="utf-8")
        source = self.root / "source.csv"
        source.write_text("new", encoding="utf-8")

        with self.assertRaises(SourceFileExistsError):
            self.framework.ingest_local_file(source, self.spec)

        self.assertEqual(destination.read_text(encoding="utf-8"), "original")

    def test_missing_source_raises_ingestion_error(self) -> None:
        with self.assertRaises(IngestionError):
            self.framework.ingest_local_file(self.root / "missing.csv", self.spec)

    def test_source_file_cannot_escape_destination_directory(self) -> None:
        with self.assertRaises(ValueError):
            SourceSpec(
                source_name="TEST_SOURCE",
                source_url="https://example.invalid/source.csv",
                reference_period="2026-01",
                source_file="../source.csv",
                destination_dir=self.root / "data" / "raw",
            )


if __name__ == "__main__":
    unittest.main()

