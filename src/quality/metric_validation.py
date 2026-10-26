"""Compare analytical metrics with the published source metrics."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Mapping


def _read_csv(path: Path) -> list[dict[str, str]]:
    with Path(path).open(encoding="utf-8", newline="") as file_obj:
        return list(csv.DictReader(file_obj))


def _quantity(row: Mapping[str, Any]) -> int:
    return int(row.get("quantity", row.get("quantity_month", 0)) or 0)


def _round_pct(value: float | None) -> float | None:
    return None if value is None else round(value, 2)


def validate_metric_records(
    *,
    fenabrave_segment_rows: list[Mapping[str, Any]],
    fenabrave_registration_rows: list[Mapping[str, Any]],
    abve_source_rows: list[Mapping[str, Any]],
    abve_gold_rows: list[Mapping[str, Any]],
) -> dict[str, Any]:
    """Validate source totals while preserving known source-grain limitations."""

    issues: list[str] = []
    comparisons: list[dict[str, Any]] = []
    limitations: list[str] = []

    fenabrave_total_rows = [
        row for row in fenabrave_segment_rows if row.get("segment_standardized") == "TOTAL"
    ]
    source_by_period: dict[str, int] = {}
    for row in fenabrave_total_rows:
        period = str(row.get("reference_period") or "2026-01")
        source_by_period[period] = _quantity(row)
    ranked_by_period: dict[str, int] = {}
    for row in fenabrave_registration_rows:
        period = str(row.get("reference_period") or "2026-01")
        ranked_by_period[period] = ranked_by_period.get(period, 0) + _quantity(row)

    fenabrave_periods = sorted(set(source_by_period) | set(ranked_by_period))
    for period in fenabrave_periods:
        source_total = source_by_period.get(period)
        ranked_total = ranked_by_period.get(period, 0)
        coverage_pct = _round_pct(ranked_total / source_total * 100) if source_total else None
        fenabrave_status = source_total is not None and 0 <= ranked_total <= source_total
        comparisons.append(
            {
                "metric": f"fenabrave_{period.replace('-', '_')}_total",
                "source_value": source_total,
                "gold_value": ranked_total,
                "delta": None if source_total is None else ranked_total - source_total,
                "status": "PASS" if fenabrave_status else "FAIL",
                "coverage_pct": coverage_pct,
                "notes": "Gold is a model-ranking subset; it is not expected to equal the official all-segment total.",
            }
        )
        if not fenabrave_status:
            issues.append(f"fenabrave_ranked_subset_exceeds_or_lacks_source_total:{period}")
    limitations.append(
        "FENABRAVE fato_emplacamentos contains published model rankings, not the complete universe of registrations."
    )

    source_by_category = {
        str(row.get("category_original")): _quantity(row)
        for row in abve_source_rows
        if row.get("aggregation_level") == "TECHNOLOGY"
        and row.get("included_in_electrified_total") == "True"
    }
    gold_by_category = {
        str(row.get("category_original")): _quantity(row)
        for row in abve_gold_rows
        if row.get("aggregation_level") == "TECHNOLOGY"
        and row.get("included_in_electrified_total") == "True"
    }
    for category, source_value in sorted(source_by_category.items()):
        gold_value = gold_by_category.get(category)
        ok = gold_value == source_value
        comparisons.append(
            {
                "metric": f"abve_2026_08_{category}",
                "source_value": source_value,
                "gold_value": gold_value,
                "delta": None if gold_value is None else gold_value - source_value,
                "status": "PASS" if ok else "FAIL",
                "notes": "ABVE technology category copied from Silver into Gold.",
            }
        )
        if not ok:
            issues.append(f"abve_category_mismatch:{category}")

    abve_total_source_rows = [row for row in abve_source_rows if row.get("category_original") == "TOTAL"]
    gold_total_rows = [row for row in abve_gold_rows if row.get("category_original") == "TOTAL"]
    abve_source_total = _quantity(abve_total_source_rows[0]) if abve_total_source_rows else None
    abve_gold_total = _quantity(gold_total_rows[0]) if gold_total_rows else None
    abve_components_total = sum(source_by_category.values())
    total_ok = (
        abve_source_total is not None
        and abve_gold_total == abve_source_total
        and abve_components_total == abve_source_total
    )
    comparisons.append(
        {
            "metric": "abve_2026_08_electrified_total",
            "source_value": abve_source_total,
            "gold_value": abve_gold_total,
            "delta": None if abve_gold_total is None or abve_source_total is None else abve_gold_total - abve_source_total,
            "status": "PASS" if total_ok else "FAIL",
            "component_sum": abve_components_total,
            "notes": "BEV + PHEV + HEV + HEV Flex must equal the published ABVE total.",
        }
    )
    if not total_ok:
        issues.append("abve_total_mismatch")

    mhev_source_rows = [row for row in abve_source_rows if row.get("category_original") == "MHEV"]
    mhev_subcategories = {
        str(row.get("category_original")): _quantity(row)
        for row in abve_source_rows
        if row.get("aggregation_level") == "SUBCATEGORY"
    }
    mhev_total = _quantity(mhev_source_rows[0]) if mhev_source_rows else None
    mhev_subtotal = sum(mhev_subcategories.values())
    mhev_ok = mhev_total is not None and mhev_total == mhev_subtotal
    comparisons.append(
        {
            "metric": "abve_2026_08_mhev_breakdown",
            "source_value": mhev_total,
            "gold_value": mhev_total,
            "delta": 0 if mhev_ok else None,
            "status": "PASS" if mhev_ok else "FAIL",
            "component_sum": mhev_subtotal,
            "notes": "MHEV is documented separately and excluded from the ABVE electrified total.",
        }
    )
    if not mhev_ok:
        issues.append("abve_mhev_breakdown_mismatch")

    return {
        "status": "PASS" if not issues else "FAIL",
        "issues": issues,
        "comparisons": comparisons,
        "limitations": limitations,
        "sources": {
            "fenabrave": sorted(
                {
                    str(row.get("source_url"))
                    for row in fenabrave_total_rows
                    if row.get("source_url")
                }
            ),
            "abve": "https://abve.org.br/com-57-mil-emplacamentos-em-agosto-eletrificados-abrem-a-corrida-para-o-milhao-em-setembro/",
        },
    }


def validate_metric_root(root: Path = Path("data")) -> dict[str, Any]:
    root = Path(root)
    fenabrave_segment_rows: list[dict[str, str]] = []
    for path in sorted((root / "silver/fenabrave").glob("*/segment_totals.csv")):
        fenabrave_segment_rows.extend(_read_csv(path))
    return validate_metric_records(
        fenabrave_segment_rows=fenabrave_segment_rows,
        fenabrave_registration_rows=_read_csv(root / "gold/fato_emplacamentos.csv"),
        abve_source_rows=_read_csv(root / "silver/abve/2026-08/technology_monthly.csv"),
        abve_gold_rows=_read_csv(root / "gold/fato_eletrificados.csv"),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Gold metrics against published source metrics.")
    parser.add_argument("--root", type=Path, default=Path("data"))
    parser.add_argument("--output", type=Path, default=Path("data/gold/metric_validation_report.json"))
    args = parser.parse_args()
    report = validate_metric_root(args.root)
    output = json.dumps(report, ensure_ascii=False, indent=2)
    print(output)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output + "\n", encoding="utf-8")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
