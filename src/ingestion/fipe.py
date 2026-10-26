"""Validated ingestion of manual snapshots from the official Tabela FIPE channel."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from .framework import IngestionError, IngestionFramework, IngestionRecord, SourceSpec


FIPE_OFFICIAL_URL = "https://www.fipe.org.br/pt-br/indices/veiculos"
FIPE_QUERY_HOSTS = {"fipe.org.br", "www.fipe.org.br", "veiculos.fipe.org.br"}
SNAPSHOT_COLUMNS = [
    "reference_period",
    "source_url",
    "fipe_code",
    "brand_original",
    "model_original",
    "model_year",
    "price_brl",
    "consulted_at",
]


@dataclass(frozen=True)
class FipeSnapshotSpec:
    reference_period: str
    source_url: str
    source_file: str


def is_official_url(source_url: str) -> bool:
    parsed = urlparse(source_url)
    return parsed.scheme == "https" and (parsed.hostname or "").lower() in FIPE_QUERY_HOSTS


def validate_snapshot_row(row: dict[str, str]) -> None:
    """Validate one manually captured official FIPE query result."""

    missing = [column for column in SNAPSHOT_COLUMNS if not row.get(column, "").strip()]
    if missing:
        raise IngestionError(f"FIPE snapshot missing fields: {', '.join(missing)}")
    if not is_official_url(row["source_url"]):
        raise IngestionError(f"FIPE snapshot source is not an official HTTPS URL: {row['source_url']}")
    try:
        year = int(row["model_year"])
        price = float(row["price_brl"].replace(".", "").replace(",", "."))
    except ValueError as exc:
        raise IngestionError("FIPE model_year and price_brl must be numeric") from exc
    if year < 1900 or price <= 0:
        raise IngestionError("FIPE model_year or price_brl is outside the accepted range")


def validate_snapshot_file(path: Path) -> list[dict[str, str]]:
    """Read and validate a non-empty manual snapshot CSV."""

    with Path(path).open(encoding="utf-8-sig", newline="") as file_obj:
        rows = list(csv.DictReader(file_obj))
    if not rows:
        raise IngestionError(f"FIPE snapshot has no data rows: {path}")
    for row in rows:
        validate_snapshot_row(row)
    return rows


def ingest_snapshot(
    input_path: Path,
    *,
    reference_period: str,
    source_url: str,
    destination_root: Path = Path("data/bronze/fipe"),
) -> IngestionRecord:
    """Store a manually captured official FIPE snapshot in Bronze with provenance."""

    if not is_official_url(source_url):
        raise IngestionError("FIPE source URL must be an official HTTPS FIPE URL")
    rows = validate_snapshot_file(input_path)
    if any(row["reference_period"] != reference_period for row in rows):
        raise IngestionError("FIPE snapshot rows contain a different reference period")
    framework = IngestionFramework()
    spec = SourceSpec(
        source_name="FIPE_TABELA",
        source_url=source_url,
        reference_period=reference_period,
        source_file=Path(input_path).name,
        destination_dir=Path(destination_root) / reference_period,
    )
    record = framework.ingest_local_file(Path(input_path), spec)
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest a validated manual FIPE snapshot into Bronze.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--period", required=True)
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--destination-root", type=Path, default=Path("data/bronze/fipe"))
    args = parser.parse_args()
    record = ingest_snapshot(
        args.input,
        reference_period=args.period,
        source_url=args.source_url,
        destination_root=args.destination_root,
    )
    print(json.dumps(record.__dict__, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
