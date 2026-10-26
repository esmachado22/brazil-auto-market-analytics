"""Generic ingestion framework for public data sources."""

from .framework import (
    IngestionError,
    IngestionFramework,
    IngestionRecord,
    SourceFileExistsError,
    SourceSpec,
    configure_logger,
    ingestion_key,
    sha256_file,
)

__all__ = [
    "IngestionError",
    "IngestionFramework",
    "IngestionRecord",
    "SourceFileExistsError",
    "SourceSpec",
    "configure_logger",
    "ingestion_key",
    "sha256_file",
]

