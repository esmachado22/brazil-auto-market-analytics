"""Validate Gold dimensions, facts and source reconciliations."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping


def _read_csv(path: Path) -> list[dict[str, str]]:
    with Path(path).open(encoding="utf-8", newline="") as file_obj:
        return list(csv.DictReader(file_obj))


def _unique_count(records: Iterable[Mapping[str, Any]], field: str) -> tuple[int, int]:
    values = [record.get(field) for record in records]
    return len(values), len(set(values))


def validate_gold_records(
    *,
    time_rows: list[Mapping[str, Any]],
    brand_rows: list[Mapping[str, Any]],
    model_rows: list[Mapping[str, Any]],
    registration_rows: list[Mapping[str, Any]],
    electrified_rows: list[Mapping[str, Any]],
    segment_rows: list[Mapping[str, Any]],
) -> dict[str, Any]:
    """Validate Gold relationships and the source-level totals available in the MVP."""

    issues: list[str] = []
    time_keys = {row.get("reference_period") for row in time_rows}
    brand_keys = {row.get("marca_key") for row in brand_rows}
    model_keys = {row.get("modelo_key") for row in model_rows}
    model_brand_keys = {row.get("marca_key") for row in model_rows}

    checks: dict[str, Any] = {}
    for name, rows, field in (
        ("dim_tempo", time_rows, "reference_period"),
        ("dim_marca", brand_rows, "marca_key"),
        ("dim_modelo", model_rows, "modelo_key"),
        ("fato_emplacamentos", registration_rows, "emplacamento_key"),
        ("fato_eletrificados", electrified_rows, "eletrificado_key"),
    ):
        row_count, unique_count = _unique_count(rows, field)
        checks[f"{name}_keys_unique"] = row_count == unique_count
        if row_count != unique_count:
            issues.append(f"duplicate_keys:{name}")

    invalid_model_brand = sum(1 for row in model_rows if row.get("marca_key") not in brand_keys)
    invalid_registration_model = sum(1 for row in registration_rows if row.get("modelo_key") not in model_keys)
    invalid_registration_brand = sum(1 for row in registration_rows if row.get("marca_key") not in brand_keys)
    invalid_model_brand_relationship = sum(1 for row in model_rows if row.get("marca_key") not in brand_keys)
    checks["model_brand_foreign_keys"] = invalid_model_brand == 0
    checks["registration_model_foreign_keys"] = invalid_registration_model == 0
    checks["registration_brand_foreign_keys"] = invalid_registration_brand == 0
    checks["model_brand_relationships"] = invalid_model_brand_relationship == 0
    for label, count in (
        ("invalid_model_brand_fk", invalid_model_brand),
        ("invalid_registration_model_fk", invalid_registration_model),
        ("invalid_registration_brand_fk", invalid_registration_brand),
    ):
        if count:
            issues.append(f"{label}:{count}")

    fact_periods = {row.get("reference_period") for row in registration_rows + electrified_rows}
    missing_periods = sorted(period for period in fact_periods if period not in time_keys)
    checks["fact_periods_in_time_dimension"] = not missing_periods
    if missing_periods:
        issues.append(f"missing_time_periods:{','.join(missing_periods)}")

    component_categories = {"BEV", "PHEV", "HEV", "HEV Flex"}
    electrified_by_category = {row.get("category_original"): int(row.get("quantity", 0)) for row in electrified_rows}
    component_total = sum(electrified_by_category.get(category, 0) for category in component_categories)
    published_total = electrified_by_category.get("TOTAL")
    checks["abve_total_reconciles"] = published_total == component_total
    if published_total != component_total:
        issues.append("abve_total_mismatch")

    source_total_rows = [row for row in segment_rows if row.get("segment_standardized") == "TOTAL"]
    source_total = int(source_total_rows[0]["quantity_month"]) if source_total_rows else None
    checks["fenabrave_source_total_present"] = source_total is not None
    if source_total is None:
        issues.append("fenabrave_source_total_missing")

    checks["registration_fact_is_ranked_subset"] = all(
        int(row.get("rank", 0)) > 0 and int(row.get("quantity", 0)) >= 0 for row in registration_rows
    )
    if not checks["registration_fact_is_ranked_subset"]:
        issues.append("invalid_registration_rank_or_quantity")

    return {
        "status": "PASS" if not issues else "FAIL",
        "issues": issues,
        "checks": checks,
        "row_counts": {
            "dim_tempo": len(time_rows),
            "dim_marca": len(brand_rows),
            "dim_modelo": len(model_rows),
            "fato_emplacamentos": len(registration_rows),
            "fato_eletrificados": len(electrified_rows),
            "segment_totals": len(segment_rows),
        },
        "reconciliations": {
            "abve_component_total": component_total,
            "abve_published_total": published_total,
            "fenabrave_published_total": source_total,
        },
    }


def validate_gold_root(root: Path = Path("data")) -> dict[str, Any]:
    root = Path(root)
    gold = root / "gold"
    silver = root / "silver"
    return validate_gold_records(
        time_rows=_read_csv(gold / "dim_tempo.csv"),
        brand_rows=_read_csv(gold / "dim_marca.csv"),
        model_rows=_read_csv(gold / "dim_modelo.csv"),
        registration_rows=_read_csv(gold / "fato_emplacamentos.csv"),
        electrified_rows=_read_csv(gold / "fato_eletrificados.csv"),
        segment_rows=_read_csv(silver / "fenabrave/2026-01/segment_totals.csv"),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the Gold analytical model.")
    parser.add_argument("--root", type=Path, default=Path("data"))
    parser.add_argument("--output", type=Path, default=Path("data/gold/model_validation_report.json"))
    args = parser.parse_args()
    report = validate_gold_root(args.root)
    output = json.dumps(report, ensure_ascii=False, indent=2)
    print(output)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output + "\n", encoding="utf-8")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
