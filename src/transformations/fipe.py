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
from src.transformations.brand_dimension import normalize_brand
from src.transformations.model_dimension import normalize_model


SILVER_COLUMNS = SNAPSHOT_COLUMNS + ["price_type"]
FACT_COLUMNS = [
    "preco_key",
    "reference_period",
    "brand_original",
    "brand_standardized",
    "model_original",
    "model_standardized",
    "model_year",
    "fipe_codes",
    "variant_count",
    "price_min_brl",
    "price_max_brl",
    "price_central_brl",
    "price_brl",
    "price_type",
    "source_url",
    "source_file",
    "source_hash",
    "consulted_at",
]


def _parse_price(value: str) -> float:
    cleaned = value.strip()
    if "," in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")
    else:
        cleaned = cleaned.replace(",", "")
    return float(cleaned)


def price_key(row: dict[str, str]) -> str:
    raw = "|".join(row.get(column, "") for column in ("reference_period", "fipe_code", "model_year"))
    return "PRECO_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def range_price_key(reference_period: str, brand_standardized: str, model_standardized: str, model_year: str) -> str:
    raw = "|".join((reference_period, brand_standardized, model_standardized, model_year))
    return "PRECO_FAIXA_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def _group_key(row: dict[str, str]) -> tuple[str, str, str, str]:
    return (
        row["reference_period"],
        normalize_brand(row["brand_original"]),
        normalize_model(row["model_original"]),
        row["model_year"],
    )


def build_price_ranges(rows: list[dict[str, str]], *, metadata: dict[str, Any], source_path: Path) -> list[dict[str, Any]]:
    """Aggregate FIPE variants into one transparent price range per model/year."""

    grouped: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for row in rows:
        key = _group_key(row)
        group = grouped.setdefault(
            key,
            {
                "reference_period": row["reference_period"],
                "brand_standardized": key[1],
                "model_standardized": key[2],
                "model_year": row["model_year"],
                "brand_originals": set(),
                "model_originals": set(),
                "fipe_codes": set(),
                "prices": [],
                "source_urls": set(),
                "consulted_at": set(),
            },
        )
        group["brand_originals"].add(row["brand_original"])
        group["model_originals"].add(row["model_original"])
        group["fipe_codes"].add(row["fipe_code"])
        group["prices"].append(_parse_price(row["price_brl"]))
        group["source_urls"].add(row["source_url"])
        group["consulted_at"].add(row["consulted_at"])

    source_hash = metadata.get("file_hash") or sha256_file(source_path)
    source_file = metadata.get("source_file") or source_path.name
    output: list[dict[str, Any]] = []
    for key, group in sorted(grouped.items()):
        price_min = min(group["prices"])
        price_max = max(group["prices"])
        price_central = round((price_min + price_max) / 2, 2)
        output.append(
            {
                "preco_key": range_price_key(*key),
                "reference_period": group["reference_period"],
                "brand_original": " | ".join(sorted(group["brand_originals"])),
                "brand_standardized": group["brand_standardized"],
                "model_original": " | ".join(sorted(group["model_originals"])),
                "model_standardized": group["model_standardized"],
                "model_year": group["model_year"],
                "fipe_codes": " | ".join(sorted(group["fipe_codes"])),
                "variant_count": len(group["prices"]),
                "price_min_brl": price_min,
                "price_max_brl": price_max,
                "price_central_brl": price_central,
                # Compatibility alias used by the existing SQL queries.
                "price_brl": price_central,
                "price_type": "REFERENCE_RANGE_CENTRAL",
                "source_url": " | ".join(sorted(group["source_urls"])),
                "source_file": source_file,
                "source_hash": source_hash,
                "consulted_at": " | ".join(sorted(group["consulted_at"])),
            }
        )
    return output


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
    range_rows = build_price_ranges(rows, metadata=metadata, source_path=source_path)
    fact_path.parent.mkdir(parents=True, exist_ok=True)
    with fact_path.open("w", encoding="utf-8", newline="") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=FACT_COLUMNS)
        writer.writeheader()
        writer.writerows(range_rows)

    report = {
        "status": "PASS",
        "reference_period": period,
        "variant_rows": len(rows),
        "model_rows": len(range_rows),
        "silver_path": str(silver_path),
        "gold_path": str(fact_path),
        "price_type": "REFERENCE_RANGE_CENTRAL",
        "limitations": [
            "price_central_brl is the midpoint of the minimum and maximum FIPE variant prices; it is not an official weighted average.",
            "FIPE values are reference prices, not effective transaction prices.",
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
