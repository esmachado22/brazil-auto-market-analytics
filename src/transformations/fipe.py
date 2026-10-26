"""Build Silver and Gold reference-price tables from FIPE snapshots."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

from src.ingestion.fipe import SNAPSHOT_COLUMNS, validate_snapshot_row
from src.ingestion.framework import sha256_file


SILVER_COLUMNS = SNAPSHOT_COLUMNS + ["price_type"]
FACT_COLUMNS = [
    "preco_key",
    "reference_period",
    "fipe_code",
    "brand_original",
    "model_original",
    "model_year",
    "price_brl",
    "price_type",
    "source_url",
    "source_file",
    "source_hash",
    "consulted_at",
]


def _parse_price(value: str) -> float:
    return float(value.replace(".", "").replace(",", "."))


def price_key(row: dict[str, str]) -> str:
    raw = "|".join(row.get(column, "") for column in ("reference_period", "fipe_code", "model_year"))
    return "PRECO_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def build_price_tables(
    period: str,
    *,
    bronze_root: Path = Path("data/bronze/fipe"),
    silver_root: Path = Path("data/silver/fipe"),
    gold_root: Path = Path("data/gold"),
) -> dict[str, Any]:
    """Validate a Bronze snapshot and create Silver plus Gold price tables."""

    bronze_period = Path(bronze_root) / period
    source_files = list(bronze_period.glob("*.csv"))
    if not source_files:
        raise FileNotFoundError(f"FIPE Bronze snapshot not found for {period}")
    source_path = source_files[0]
    metadata_path = source_path.with_name(source_path.name + ".metadata.json")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    with source_path.open(encoding="utf-8-sig", newline="") as file_obj:
        rows = list(csv.DictReader(file_obj))
    for row in rows:
        validate_snapshot_row(row)
    silver_path = Path(silver_root) / period / "reference_prices.csv"
    silver_path.parent.mkdir(parents=True, exist_ok=True)
    with silver_path.open("w", encoding="utf-8", newline="") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=SILVER_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({**row, "price_type": "REFERENCE"})

    fact_path = Path(gold_root) / "fato_precos.csv"
    fact_path.parent.mkdir(parents=True, exist_ok=True)
    with fact_path.open("w", encoding="utf-8", newline="") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=FACT_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "preco_key": price_key(row),
                    "reference_period": row["reference_period"],
                    "fipe_code": row["fipe_code"],
                    "brand_original": row["brand_original"],
                    "model_original": row["model_original"],
                    "model_year": row["model_year"],
                    "price_brl": _parse_price(row["price_brl"]),
                    "price_type": "REFERENCE",
                    "source_url": row["source_url"],
                    "source_file": metadata.get("source_file", source_path.name),
                    "source_hash": metadata.get("file_hash", sha256_file(source_path)),
                    "consulted_at": row["consulted_at"],
                }
            )

    report = {
        "status": "PASS",
        "reference_period": period,
        "rows": len(rows),
        "silver_path": str(silver_path),
        "gold_path": str(fact_path),
        "price_type": "REFERENCE",
        "limitations": [
            "FIPE values are average reference prices, not effective transaction prices.",
            "The official channel does not provide an API or bulk database; ingestion accepts manually captured query snapshots only.",
            "The vehicle year is model year according to FIPE, not necessarily manufacturing year.",
        ],
    }
    (Path(gold_root) / "fato_precos_validation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Build FIPE Silver and Gold reference-price tables.")
    parser.add_argument("--period", required=True)
    parser.add_argument("--bronze-root", type=Path, default=Path("data/bronze/fipe"))
    parser.add_argument("--silver-root", type=Path, default=Path("data/silver/fipe"))
    parser.add_argument("--gold-root", type=Path, default=Path("data/gold"))
    args = parser.parse_args()
    print(json.dumps(build_price_tables(args.period, bronze_root=args.bronze_root, silver_root=args.silver_root, gold_root=args.gold_root), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
