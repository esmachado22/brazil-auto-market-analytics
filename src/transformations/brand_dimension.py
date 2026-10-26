"""Build a deterministic brand dimension from FENABRAVE Silver rankings."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any, Iterable, Mapping

from src.ingestion.framework import IngestionError


BRAND_ALIASES = {
    "VW": "VOLKSWAGEN",
    "M.BENZ": "MERCEDES-BENZ",
}


def normalize_brand(value: str | None) -> str:
    """Standardize casing, accents and safe whitespace without inventing identity."""

    if value is None or not value.strip():
        return "NAO_INFORMADA"
    without_accents = "".join(
        char for char in unicodedata.normalize("NFKD", value) if not unicodedata.combining(char)
    )
    normalized = re.sub(r"\s+", " ", without_accents).strip().upper()
    return BRAND_ALIASES.get(normalized, normalized)


def brand_key(brand_standardized: str) -> str:
    """Return a stable surrogate key for a canonical brand name."""

    digest = hashlib.sha256(brand_standardized.encode("utf-8")).hexdigest()[:12]
    return f"MARCA_{digest}"


def build_brand_dimension(records: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Group source brand names into one deterministic dimension row each."""

    grouped: dict[str, dict[str, Any]] = {}
    for record in records:
        original = str(record.get("brand_original") or "").strip()
        standardized = normalize_brand(original)
        group = grouped.setdefault(
            standardized,
            {
                "marca_key": brand_key(standardized),
                "brand_standardized": standardized,
                "brand_originals": set(),
                "source_names": set(),
                "reference_periods": set(),
                "source_files": set(),
            },
        )
        if original:
            group["brand_originals"].add(original)
        if record.get("source_name"):
            group["source_names"].add(str(record["source_name"]))
        if record.get("reference_period"):
            group["reference_periods"].add(str(record["reference_period"]))
        if record.get("source_file"):
            group["source_files"].add(str(record["source_file"]))

    rows: list[dict[str, Any]] = []
    for standardized in sorted(grouped):
        group = grouped[standardized]
        originals = sorted(group["brand_originals"])
        rows.append(
            {
                "marca_key": group["marca_key"],
                "brand_original": originals[0] if originals else "",
                "brand_originals": " | ".join(originals),
                "brand_standardized": standardized,
                "source_names": " | ".join(sorted(group["source_names"])),
                "reference_periods": " | ".join(sorted(group["reference_periods"])),
                "source_files": " | ".join(sorted(group["source_files"])),
            }
        )
    return rows


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise IngestionError(f"FENABRAVE Silver ranking not found: {path}")
    with path.open(encoding="utf-8", newline="") as file_obj:
        return list(csv.DictReader(file_obj))


def write_brand_dimension(rows: list[dict[str, Any]], output_path: Path) -> None:
    if not rows:
        raise IngestionError("Cannot write an empty brand dimension")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def build_from_silver(
    ranking_path: Path,
    *,
    output_path: Path = Path("data/gold/dim_marca.csv"),
) -> dict[str, Any]:
    """Build the brand dimension from the model ranking Silver dataset."""

    rows = build_brand_dimension(_read_csv(Path(ranking_path)))
    keys = [row["marca_key"] for row in rows]
    if len(keys) != len(set(keys)):
        raise IngestionError("Brand dimension contains duplicate keys")
    write_brand_dimension(rows, output_path)
    return {"status": "PASS", "row_count": len(rows), "output": str(output_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the brand dimension from FENABRAVE Silver.")
    parser.add_argument(
        "--ranking",
        type=Path,
        default=Path("data/silver/fenabrave/2026-01/model_rankings.csv"),
    )
    parser.add_argument("--output", type=Path, default=Path("data/gold/dim_marca.csv"))
    args = parser.parse_args()
    print(json.dumps(build_from_silver(args.ranking, output_path=args.output), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
