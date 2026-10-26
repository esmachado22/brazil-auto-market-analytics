"""Build the Gold fact table for FENABRAVE registrations."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from src.ingestion.framework import IngestionError
from src.transformations.brand_dimension import brand_key, normalize_brand
from src.transformations.model_dimension import model_key, normalize_model


def fact_key(reference_period: str, modelo_key_value: str, category: str, rank: str, source_file: str) -> str:
    value = "|".join((reference_period, modelo_key_value, category, rank, source_file))
    return f"EMPLACAMENTO_{hashlib.sha256(value.encode('utf-8')).hexdigest()[:16]}"


def build_fact_records(
    ranking_records: list[Mapping[str, Any]],
    model_dimension: list[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    model_keys = {
        (str(row["brand_standardized"]), str(row["model_standardized"])): str(row["modelo_key"])
        for row in model_dimension
    }
    facts: list[dict[str, Any]] = []
    for record in ranking_records:
        brand_standardized = normalize_brand(record.get("brand_original"))
        model_standardized = normalize_model(record.get("model_original"))
        model_lookup_key = (brand_standardized, model_standardized)
        modelo_key_value = model_keys.get(model_lookup_key)
        if not modelo_key_value:
            raise IngestionError(f"Model dimension relationship not found: {model_lookup_key}")
        category = str(record["category_standardized"])
        rank = str(record["rank"])
        quantity = int(record["quantity"])
        source_file = str(record["source_file"])
        facts.append(
            {
                "emplacamento_key": fact_key(
                    str(record["reference_period"]), modelo_key_value, category, rank, source_file
                ),
                "reference_period": str(record["reference_period"]),
                "marca_key": brand_key(brand_standardized),
                "modelo_key": modelo_key_value,
                "brand_standardized": brand_standardized,
                "model_standardized": model_standardized,
                "category_standardized": category,
                "technology_standardized": "NAO_INFORMADO",
                "rank": int(record["rank"]),
                "quantity": quantity,
                "source_name": str(record["source_name"]),
                "source_url": str(record["source_url"]),
                "source_file": source_file,
                "source_page": int(record["source_page"]),
                "source_hash": str(record["source_hash"]),
            }
        )
    return facts


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise IngestionError(f"Required Gold input not found: {path}")
    with path.open(encoding="utf-8", newline="") as file_obj:
        return list(csv.DictReader(file_obj))


def _read_rankings(silver_root: Path) -> list[dict[str, str]]:
    """Read every FENABRAVE ranking discovered under the Silver root."""

    paths = sorted(Path(silver_root).glob("*/model_rankings.csv"))
    if not paths:
        raise IngestionError(f"No FENABRAVE Silver rankings found under: {silver_root}")
    rows: list[dict[str, str]] = []
    for path in paths:
        rows.extend(_read_csv(path))
    return rows


def write_fact(rows: list[dict[str, Any]], output_path: Path) -> None:
    if not rows:
        raise IngestionError("Cannot write an empty emplacamentos fact")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def build_from_silver(
    ranking_path: Path | None = None,
    model_dimension_path: Path = Path("data/gold/dim_modelo.csv"),
    output_path: Path = Path("data/gold/fato_emplacamentos.csv"),
    *,
    silver_root: Path | None = None,
) -> dict[str, Any]:
    if ranking_path is not None and silver_root is not None:
        raise ValueError("Use ranking_path or silver_root, not both")
    ranking_records = _read_csv(Path(ranking_path)) if ranking_path is not None else _read_rankings(
        silver_root or Path("data/silver/fenabrave")
    )
    model_dimension = _read_csv(Path(model_dimension_path))
    facts = build_fact_records(ranking_records, model_dimension)
    keys = [row["emplacamento_key"] for row in facts]
    if len(keys) != len(set(keys)):
        raise IngestionError("Fato de emplacamentos contains duplicate keys")
    if any(row["quantity"] < 0 for row in facts):
        raise IngestionError("Fato de emplacamentos contains negative quantities")
    write_fact(facts, output_path)
    return {"status": "PASS", "row_count": len(facts), "output": str(output_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the FENABRAVE emplacamentos fact.")
    parser.add_argument("--ranking", type=Path, help="Single ranking CSV; omit to read all Silver periods")
    parser.add_argument("--silver-root", type=Path, default=Path("data/silver/fenabrave"))
    parser.add_argument("--model-dimension", type=Path, default=Path("data/gold/dim_modelo.csv"))
    parser.add_argument("--output", type=Path, default=Path("data/gold/fato_emplacamentos.csv"))
    args = parser.parse_args()
    print(
        json.dumps(
            build_from_silver(
                args.ranking,
                args.model_dimension,
                args.output,
                silver_root=None if args.ranking else args.silver_root,
            ),
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
