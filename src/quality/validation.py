"""Generic quality checks for Silver datasets."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any, Iterable, Mapping


PERIOD_PATTERN = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


def _is_null(value: Any) -> bool:
    return value is None or str(value).strip() == ""


def _to_number(value: Any) -> float | None:
    if _is_null(value):
        return None
    try:
        return float(str(value).replace(",", "."))
    except ValueError:
        return None


def validate_records(
    records: Iterable[Mapping[str, Any]],
    *,
    required_fields: tuple[str, ...],
    key_fields: tuple[str, ...],
    quantity_field: str | None = None,
    period_field: str = "reference_period",
) -> dict[str, Any]:
    """Run required-field, period, quantity and duplicate-key checks."""

    records = list(records)
    required_nulls = {field: 0 for field in required_fields}
    invalid_period_count = 0
    invalid_quantity_count = 0
    negative_quantity_count = 0
    duplicate_keys: list[list[Any]] = []
    seen_keys: set[tuple[Any, ...]] = set()

    for record in records:
        for field in required_fields:
            if _is_null(record.get(field)):
                required_nulls[field] += 1

        period = record.get(period_field)
        if not _is_null(period) and not PERIOD_PATTERN.fullmatch(str(period).strip()):
            invalid_period_count += 1

        if quantity_field is not None:
            quantity = _to_number(record.get(quantity_field))
            if quantity is None:
                invalid_quantity_count += 1
            elif quantity < 0:
                negative_quantity_count += 1

        key = tuple(record.get(field) for field in key_fields)
        if any(_is_null(value) for value in key):
            continue
        if key in seen_keys:
            duplicate_keys.append(list(key))
        seen_keys.add(key)

    required_null_count = sum(required_nulls.values())
    status = (
        "PASS"
        if required_null_count == 0
        and invalid_period_count == 0
        and invalid_quantity_count == 0
        and negative_quantity_count == 0
        and not duplicate_keys
        else "FAIL"
    )
    return {
        "status": status,
        "row_count": len(records),
        "required_nulls": required_nulls,
        "required_null_count": required_null_count,
        "invalid_period_count": invalid_period_count,
        "invalid_quantity_count": invalid_quantity_count,
        "negative_quantity_count": negative_quantity_count,
        "duplicate_count": len(duplicate_keys),
        "duplicate_keys": duplicate_keys,
        "required_fields": list(required_fields),
        "key_fields": list(key_fields),
        "quantity_field": quantity_field,
    }


def validate_csv(
    path: Path,
    *,
    required_fields: tuple[str, ...],
    key_fields: tuple[str, ...],
    quantity_field: str | None = None,
) -> dict[str, Any]:
    """Load a CSV and run the generic checks."""

    path = Path(path)
    if not path.is_file():
        return {"status": "FAIL", "path": str(path), "error": "file_not_found"}
    with path.open(encoding="utf-8", newline="") as file_obj:
        records = list(csv.DictReader(file_obj))
    report = validate_records(
        records,
        required_fields=required_fields,
        key_fields=key_fields,
        quantity_field=quantity_field,
    )
    report["path"] = str(path)
    return report


def validate_project_silver(root: Path = Path("data/silver")) -> dict[str, Any]:
    """Validate the FENABRAVE and ABVE Silver outputs for the MVP."""

    root = Path(root)
    configs = {
        "fenabrave_segment_totals": {
            "path": root / "fenabrave/2026-01/segment_totals.csv",
            "required_fields": ("reference_period", "segment_standardized", "source_file", "quantity_month"),
            "key_fields": ("reference_period", "segment_standardized", "source_file"),
            "quantity_field": "quantity_month",
        },
        "fenabrave_model_rankings": {
            "path": root / "fenabrave/2026-01/model_rankings.csv",
            "required_fields": ("reference_period", "category_standardized", "rank", "source_file", "quantity"),
            "key_fields": ("reference_period", "category_standardized", "rank", "source_file"),
            "quantity_field": "quantity",
        },
        "abve_technology_monthly": {
            "path": root / "abve/2026-08/technology_monthly.csv",
            "required_fields": ("reference_period", "category_original", "technology_standardized", "source_file", "quantity"),
            "key_fields": ("reference_period", "category_original", "source_file"),
            "quantity_field": "quantity",
        },
    }
    reports = {
        name: validate_csv(
            config["path"],
            required_fields=config["required_fields"],
            key_fields=config["key_fields"],
            quantity_field=config["quantity_field"],
        )
        for name, config in configs.items()
    }
    return {
        "status": "PASS" if all(report["status"] == "PASS" for report in reports.values()) else "FAIL",
        "datasets": reports,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Silver data-quality checks.")
    parser.add_argument("--root", type=Path, default=Path("data/silver"))
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    report = validate_project_silver(args.root)
    output = json.dumps(report, ensure_ascii=False, indent=2)
    print(output)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output + "\n", encoding="utf-8")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
