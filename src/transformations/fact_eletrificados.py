"""Build the Gold fact table for ABVE electrified vehicles."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from src.ingestion.framework import IngestionError


def electrified_key(reference_period: str, category: str, source_file: str) -> str:
    value = "|".join((reference_period, category, source_file))
    return f"ELETRIFICADO_{hashlib.sha256(value.encode('utf-8')).hexdigest()[:16]}"


def build_fact_records(records: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    facts: list[dict[str, Any]] = []
    for record in records:
        category = str(record["category_original"])
        reference_period = str(record["reference_period"])
        source_file = str(record["source_file"])
        facts.append(
            {
                "eletrificado_key": electrified_key(reference_period, category, source_file),
                "reference_period": reference_period,
                "category_original": category,
                "technology_standardized": str(record["technology_standardized"]),
                "aggregation_level": str(record["aggregation_level"]),
                "is_component": str(record["is_component"]).lower() == "true" if isinstance(record["is_component"], str) else bool(record["is_component"]),
                "included_in_electrified_total": str(record["included_in_electrified_total"]).lower() == "true" if isinstance(record["included_in_electrified_total"], str) else bool(record["included_in_electrified_total"]),
                "quantity": int(record["quantity"]),
                "share_pct": record.get("share_pct") if record.get("share_pct") not in ("", None) else None,
                "source_name": str(record["source_name"]),
                "source_url": str(record["source_url"]),
                "source_file": source_file,
                "source_locator": str(record["source_locator"]),
                "source_hash": str(record["source_hash"]),
            }
        )
    return facts


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise IngestionError(f"ABVE Silver technology file not found: {path}")
    with path.open(encoding="utf-8", newline="") as file_obj:
        return list(csv.DictReader(file_obj))


def write_fact(rows: list[dict[str, Any]], output_path: Path) -> None:
    if not rows:
        raise IngestionError("Cannot write an empty electrified fact")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def build_from_silver(
    technology_path: Path = Path("data/silver/abve/2026-08/technology_monthly.csv"),
    output_path: Path = Path("data/gold/fato_eletrificados.csv"),
) -> dict[str, Any]:
    records = _read_csv(Path(technology_path))
    facts = build_fact_records(records)
    keys = [row["eletrificado_key"] for row in facts]
    if len(keys) != len(set(keys)):
        raise IngestionError("Fato de eletrificados contains duplicate keys")
    if any(row["quantity"] < 0 for row in facts):
        raise IngestionError("Fato de eletrificados contains negative quantities")
    write_fact(facts, output_path)
    return {"status": "PASS", "row_count": len(facts), "output": str(output_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the ABVE eletrificados fact.")
    parser.add_argument("--technology", type=Path, default=Path("data/silver/abve/2026-08/technology_monthly.csv"))
    parser.add_argument("--output", type=Path, default=Path("data/gold/fato_eletrificados.csv"))
    args = parser.parse_args()
    print(json.dumps(build_from_silver(args.technology, args.output), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
