"""Generic, source-agnostic ingestion utilities.

Source-specific collectors should provide a :class:`SourceSpec` and call the
framework. Downloading, copying, hashing, metadata and error handling stay in
this module so new sources do not duplicate that logic.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from shutil import copyfileobj
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


LOGGER_NAME = "brazil_auto_market_analytics.ingestion"
CHUNK_SIZE = 1024 * 1024


class IngestionError(RuntimeError):
    """Base error for expected ingestion failures."""


class SourceFileExistsError(IngestionError):
    """Raised when ingestion would overwrite an existing source file."""


@dataclass(frozen=True)
class SourceSpec:
    """Description of one source file to be ingested."""

    source_name: str
    source_url: str
    reference_period: str
    source_file: str
    destination_dir: Path

    def __post_init__(self) -> None:
        if not self.source_name.strip():
            raise ValueError("source_name must not be empty")
        if not self.reference_period.strip():
            raise ValueError("reference_period must not be empty")
        if Path(self.source_file).name != self.source_file:
            raise ValueError("source_file must be a file name, not a path")


@dataclass(frozen=True)
class IngestionRecord:
    """Audit record written after a source file is stored successfully."""

    source_name: str
    source_url: str
    reference_period: str
    source_file: str
    local_path: str
    metadata_path: str
    file_hash: str
    file_size_bytes: int
    ingestion_timestamp: str
    ingestion_key: str = ""


def configure_logger(log_path: Path | None = None) -> logging.Logger:
    """Return the shared ingestion logger, optionally adding a file handler."""

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s")
        )
        logger.addHandler(console_handler)

    if log_path is not None:
        resolved_log_path = Path(log_path)
        resolved_log_path.parent.mkdir(parents=True, exist_ok=True)
        existing_paths = {
            Path(handler.baseFilename).resolve()
            for handler in logger.handlers
            if isinstance(handler, logging.FileHandler)
        }
        if resolved_log_path.resolve() not in existing_paths:
            file_handler = logging.FileHandler(resolved_log_path, encoding="utf-8")
            file_handler.setFormatter(
                logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s")
            )
            logger.addHandler(file_handler)

    return logger


def sha256_file(path: Path, chunk_size: int = CHUNK_SIZE) -> str:
    """Calculate the SHA-256 hash of a local file."""

    digest = hashlib.sha256()
    with Path(path).open("rb") as file_obj:
        for chunk in iter(lambda: file_obj.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ingestion_key(spec: SourceSpec) -> str:
    """Build the stable key used to prevent duplicate ingestion."""

    return f"{spec.source_name}|{spec.reference_period}|{spec.source_file}"


class IngestionFramework:
    """Store source files while preserving provenance and audit metadata."""

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self.logger = logger or configure_logger()

    def ingest_local_file(
        self,
        source_path: Path,
        spec: SourceSpec,
    ) -> IngestionRecord:
        """Copy an already downloaded source file into the destination layer."""

        source_path = Path(source_path)
        if not source_path.is_file():
            raise IngestionError(f"Source file does not exist: {source_path}")

        destination, existing_record = self._prepare_destination(spec)
        if existing_record is not None:
            return existing_record
        self.logger.info("Ingesting local file %s", source_path)
        try:
            with source_path.open("rb") as source_stream, destination.with_suffix(
                destination.suffix + ".part"
            ).open("wb") as destination_stream:
                copyfileobj(source_stream, destination_stream, length=CHUNK_SIZE)
            partial_path = destination.with_suffix(destination.suffix + ".part")
            partial_path.replace(destination)
        except OSError as exc:
            partial_path = destination.with_suffix(destination.suffix + ".part")
            partial_path.unlink(missing_ok=True)
            self.logger.exception("Failed to copy %s", source_path)
            raise IngestionError(f"Could not store {source_path}") from exc

        return self._write_metadata(spec, destination)

    def download(
        self,
        spec: SourceSpec,
        *,
        timeout_seconds: int = 60,
    ) -> IngestionRecord:
        """Download one source file using the standard library HTTP client."""

        destination, existing_record = self._prepare_destination(spec)
        if existing_record is not None:
            return existing_record
        partial_path = destination.with_suffix(destination.suffix + ".part")
        request = Request(spec.source_url, headers={"User-Agent": "BrazilAutoMarketAnalytics/1.0"})
        self.logger.info("Downloading %s", spec.source_url)

        try:
            with urlopen(request, timeout=timeout_seconds) as response, partial_path.open("wb") as output:
                copyfileobj(response, output, length=CHUNK_SIZE)
            partial_path.replace(destination)
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            partial_path.unlink(missing_ok=True)
            self.logger.exception("Failed to download %s", spec.source_url)
            raise IngestionError(f"Could not download {spec.source_url}") from exc

        return self._write_metadata(spec, destination)

    def _prepare_destination(self, spec: SourceSpec) -> tuple[Path, IngestionRecord | None]:
        destination_dir = Path(spec.destination_dir)
        destination_dir.mkdir(parents=True, exist_ok=True)
        destination = destination_dir / spec.source_file
        if destination.exists():
            return destination, self._load_existing_record(spec, destination)
        metadata_path = destination.with_name(destination.name + ".metadata.json")
        if metadata_path.exists():
            raise SourceFileExistsError(
                f"Metadata exists without its source file: {metadata_path}"
            )
        return destination, None

    def _load_existing_record(self, spec: SourceSpec, destination: Path) -> IngestionRecord:
        metadata_path = destination.with_name(destination.name + ".metadata.json")
        if not metadata_path.is_file():
            raise SourceFileExistsError(
                f"Destination already exists without metadata: {destination}"
            )

        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            metadata_key = metadata.get("ingestion_key")
            existing_key = metadata_key or ingestion_key(spec)
            record = IngestionRecord(
                source_name=metadata["source_name"],
                source_url=metadata["source_url"],
                reference_period=metadata["reference_period"],
                source_file=metadata["source_file"],
                local_path=metadata["local_path"],
                metadata_path=metadata["metadata_path"],
                file_hash=metadata["file_hash"],
                file_size_bytes=metadata["file_size_bytes"],
                ingestion_timestamp=metadata["ingestion_timestamp"],
                ingestion_key=existing_key,
            )
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise SourceFileExistsError(
                f"Could not validate existing metadata: {metadata_path}"
            ) from exc

        expected_key = ingestion_key(spec)
        if (
            record.ingestion_key != expected_key
            or record.source_name != spec.source_name
            or record.source_url != spec.source_url
            or record.reference_period != spec.reference_period
            or record.source_file != spec.source_file
            or record.file_hash != sha256_file(destination)
        ):
            raise SourceFileExistsError(
                f"Existing destination has different provenance: {destination}"
            )

        if not metadata_key:
            metadata["ingestion_key"] = expected_key
            metadata_path.write_text(
                json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

        self.logger.info("Idempotent ingestion already present: %s", destination)
        return record

    def _write_metadata(self, spec: SourceSpec, destination: Path) -> IngestionRecord:
        ingestion_timestamp = datetime.now(timezone.utc).isoformat()
        record = IngestionRecord(
            source_name=spec.source_name,
            source_url=spec.source_url,
            reference_period=spec.reference_period,
            source_file=spec.source_file,
            local_path=str(destination),
            metadata_path=str(destination.with_name(destination.name + ".metadata.json")),
            file_hash=sha256_file(destination),
            file_size_bytes=destination.stat().st_size,
            ingestion_timestamp=ingestion_timestamp,
            ingestion_key=ingestion_key(spec),
        )
        metadata_path = Path(record.metadata_path)
        metadata_path.write_text(
            json.dumps(asdict(record), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        self.logger.info(
            "Stored %s (%d bytes, sha256=%s)",
            destination,
            record.file_size_bytes,
            record.file_hash,
        )
        return record

