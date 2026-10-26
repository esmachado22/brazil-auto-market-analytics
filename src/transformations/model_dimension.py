"""Build the model dimension and its relationship to the brand dimension."""

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
from src.transformations.brand_dimension import brand_key, normalize_brand


def normalize_model(value: str | None) -> str:
    if value is None or not value.strip():
        return "NAO_INFORMADO"
    without_accents = "".join(
        char for char in unicodedata.normalize("NFKD", value) if not unicodedata.combining(char)
    )
    return re.sub(r"\s+", " ", without_accents).strip().upper()


def model_key(marca_key: str, model_standardized: str) -> str:
    digest = hashlib.sha256(f"{marca_key}|{model_standardized}".encode("utf-8")).hexdigest()[:12]
    return f"MODELO_{digest}"


def build_model_dimension(records: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], dict[str, Any]] = {}
    for record in records:
        original_brand = str(record.get("brand_original") or "").strip()
        original_model = str(record.get("model_original") or "").strip()
        brand_standardized = normalize_brand(original_brand)
        model_standardized = normalize_model(original_model)
        marca_key = brand_key(brand_standardized)
        grouping_key = (brand_standardized, model_standardized)
        group = grouped.setdefault(
            grouping_key,
            {
                "modelo_key": model_key(marca_key, model_standardized),
                "marca_key": marca_key,
                "brand_standardized": brand_standardized,
                "model_originals": set(),
                "model_standardized": model_standardized,
                "categories": set(),
                "source_names": set(),
                "reference_periods": set(),
                "source_files": set(),
            },
        )
        if original_model:
            group["model_originals"].add(original_model)
        if record.get("category_standardized"):
            group["categories"].add(str(record["category_standardized"]))
        if record.get("source_name"):
            group["source_names"].add(str(record["source_name"]))
        if record.get("reference_period"):
            group["reference_periods"].add(str(record["reference_period"]))
        if record.get("source_file"):
            group["source_files"].add(str(record["source_file"]))

    rows: list[dict[str, Any]] = []
    for _, group in sorted(grouped.items()):
        originals = sorted(group["model_originals"])
        rows.append(
            {
                "modelo_key": group["modelo_key"],
                "marca_key": group["marca_key"],
                "brand_standardized": group["brand_standardized"],
                "model_original": originals[0] if originals else "",
                "model_originals": " | ".join(originals),
                "model_standardized": group["model_standardized"],
                "categories": " | ".join(sorted(group["categories"])),
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


def write_model_dimension(rows: list[dict[str, Any]], output_path: Path) -> None:
    if not rows:
        raise IngestionError("Cannot write an empty model dimension")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def build_from_silver(
    ranking_path: Path,
    *,
    output_path: Path = Path("data/gold/dim_modelo.csv"),
) -> dict[str, Any]:
    rows = build_model_dimension(_read_csv(Path(ranking_path)))
    keys = [row["modelo_key"] for row in rows]
    relationships = [row["marca_key"] for row in rows]
    if len(keys) != len(set(keys)):
        raise IngestionError("Model dimension contains duplicate keys")
    if any(not relationship for relationship in relationships):
        raise IngestionError("Model dimension contains missing brand relationships")
    write_model_dimension(rows, output_path)
    return {"status": "PASS", "row_count": len(rows), "output": str(output_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the model dimension from FENABRAVE Silver.")
    parser.add_argument(
        "--ranking",
        type=Path,
        default=Path("data/silver/fenabrave/2026-01/model_rankings.csv"),
    )
    parser.add_argument("--output", type=Path, default=Path("data/gold/dim_modelo.csv"))
    args = parser.parse_args()
    print(json.dumps(build_from_silver(args.ranking, output_path=args.output), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
