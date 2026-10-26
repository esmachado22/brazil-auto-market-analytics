"""Build the calendar dimension used by the analytical model."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import date, datetime
from pathlib import Path
from typing import Iterable

from src.ingestion.framework import IngestionError


MONTH_NAMES_PT = (
    "",
    "janeiro",
    "fevereiro",
    "março",
    "abril",
    "maio",
    "junho",
    "julho",
    "agosto",
    "setembro",
    "outubro",
    "novembro",
    "dezembro",
)


def parse_period(reference_period: str) -> tuple[int, int]:
    """Parse and validate a period in YYYY-MM format."""

    try:
        parsed = datetime.strptime(reference_period, "%Y-%m")
    except ValueError as exc:
        raise ValueError(f"Invalid reference period: {reference_period}") from exc
    return parsed.year, parsed.month


def _period_index(year: int, month: int) -> int:
    return year * 12 + month - 1


def _period_from_index(index: int) -> str:
    year, month_zero_based = divmod(index, 12)
    return f"{year:04d}-{month_zero_based + 1:02d}"


def build_time_dimension(start_period: str, end_period: str) -> list[dict[str, object]]:
    """Build one row per calendar month in an inclusive period range."""

    start_year, start_month = parse_period(start_period)
    end_year, end_month = parse_period(end_period)
    start_index = _period_index(start_year, start_month)
    end_index = _period_index(end_year, end_month)
    if start_index > end_index:
        raise ValueError("start_period must not be after end_period")

    rows: list[dict[str, object]] = []
    for index in range(start_index, end_index + 1):
        reference_period = _period_from_index(index)
        year, month = parse_period(reference_period)
        quarter_number = ((month - 1) // 3) + 1
        rows.append(
            {
                "date_key": f"{reference_period}-01",
                "reference_period": reference_period,
                "year": year,
                "month": month,
                "month_name_pt": MONTH_NAMES_PT[month],
                "quarter_number": quarter_number,
                "quarter": f"Q{quarter_number}",
                "year_quarter": f"{year}-Q{quarter_number}",
            }
        )
    return rows


def discover_periods(silver_root: Path) -> list[str]:
    """Read reference periods from all Silver CSVs."""

    periods: set[str] = set()
    for csv_path in Path(silver_root).rglob("*.csv"):
        with csv_path.open(encoding="utf-8", newline="") as file_obj:
            reader = csv.DictReader(file_obj)
            if "reference_period" not in (reader.fieldnames or []):
                continue
            for row in reader:
                period = row.get("reference_period", "").strip()
                if period:
                    parse_period(period)
                    periods.add(period)
    return sorted(periods)


def build_from_silver(silver_root: Path) -> list[dict[str, object]]:
    """Build a continuous calendar covering all periods found in Silver."""

    periods = discover_periods(silver_root)
    if not periods:
        raise IngestionError(f"No valid reference periods found under {silver_root}")
    return build_time_dimension(periods[0], periods[-1])


def write_time_dimension(rows: Iterable[dict[str, object]], output_path: Path) -> None:
    rows = list(rows)
    if not rows:
        raise ValueError("Cannot write an empty time dimension")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the time dimension from Silver periods.")
    parser.add_argument("--silver-root", type=Path, default=Path("data/silver"))
    parser.add_argument("--output", type=Path, default=Path("data/gold/dim_tempo.csv"))
    args = parser.parse_args()

    rows = build_from_silver(args.silver_root)
    write_time_dimension(rows, args.output)
    print(json.dumps({"status": "PASS", "row_count": len(rows), "output": str(args.output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
