"""Standardize ABVE Data HTML evidence into Silver."""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from src.ingestion.framework import IngestionError, sha256_file
from src.transformations.technology import classify_technology, is_abve_electrified_component


COMPONENT_CATEGORIES = ("BEV", "PHEV", "HEV", "HEV Flex")
CATEGORY_PATTERN = re.compile(
    r"\b(?P<category>HEV Flex|PHEV|BEV|HEV|TOTAL)\s*:\s*"
    r"(?P<quantity>\d[\d.]*)"
    r"(?:\s*\((?P<share>[\d,]+)%\))?",
    flags=re.IGNORECASE,
)
MHEV_TOTAL_PATTERN = re.compile(r"MHEV\)\s*venderam\s*(?P<quantity>\d[\d.]*)\s*unidades", re.IGNORECASE)
MHEV_48V_PATTERN = re.compile(r"MHEV\s+48V.*?com\s+(?P<quantity>\d[\d.]*)\s+unidades", re.IGNORECASE)
MHEV_12V_PATTERN = re.compile(r"MHEV\s+12V.*?somaram\s+(?P<quantity>\d[\d.]*)\s+unidades", re.IGNORECASE)


@dataclass(frozen=True)
class SourceMetadata:
    source_name: str
    source_url: str
    reference_period: str
    source_file: str
    file_hash: str


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in {"script", "style", "noscript"}:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style", "noscript"} and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self._skip_depth:
            self.parts.append(data)


def extract_text(document: str) -> str:
    """Extract visible HTML text while excluding scripts and styles."""

    parser = _TextExtractor()
    parser.feed(document)
    return " ".join(html.unescape(" ".join(parser.parts)).split())


def parse_integer(value: str) -> int:
    cleaned = value.replace(".", "")
    if not re.fullmatch(r"\d+", cleaned):
        raise ValueError(f"Invalid ABVE integer: {value}")
    return int(cleaned)


def parse_decimal(value: str) -> float:
    return float(value.replace(",", "."))


def _record(
    *,
    metadata: SourceMetadata,
    category_original: str,
    quantity: int,
    share_pct: float | None,
    aggregation_level: str,
    is_component: bool,
    source_locator: str,
) -> dict[str, Any]:
    return {
        "reference_period": metadata.reference_period,
        "source_name": metadata.source_name,
        "source_url": metadata.source_url,
        "source_file": metadata.source_file,
        "source_hash": metadata.file_hash,
        "source_locator": source_locator,
        "category_original": category_original,
        "technology_standardized": classify_technology(category_original),
        "aggregation_level": aggregation_level,
        "is_component": is_component,
        "included_in_electrified_total": is_abve_electrified_component(category_original),
        "quantity": quantity,
        "share_pct": share_pct,
    }


def parse_abve_text(text: str, *, metadata: SourceMetadata) -> list[dict[str, Any]]:
    """Extract original ABVE technology categories and published quantities."""

    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    for match in CATEGORY_PATTERN.finditer(text):
        category = match.group("category")
        category = "HEV Flex" if category.casefold() == "hev flex" else category.upper()
        if category in seen:
            continue
        seen.add(category)
        records.append(
            _record(
                metadata=metadata,
                category_original=category,
                quantity=parse_integer(match.group("quantity")),
                share_pct=parse_decimal(match.group("share")) if match.group("share") else None,
                aggregation_level="TOTAL" if category == "TOTAL" else "TECHNOLOGY",
                is_component=category in COMPONENT_CATEGORIES,
                source_locator="article_body:technology_summary",
            )
        )

    extra_patterns = (
        ("MHEV", MHEV_TOTAL_PATTERN, "TECHNOLOGY"),
        ("MHEV 48V", MHEV_48V_PATTERN, "SUBCATEGORY"),
        ("MHEV 12V", MHEV_12V_PATTERN, "SUBCATEGORY"),
    )
    for category, pattern, aggregation_level in extra_patterns:
        match = pattern.search(text)
        if match and category not in seen:
            seen.add(category)
            records.append(
                _record(
                    metadata=metadata,
                    category_original=category,
                    quantity=parse_integer(match.group("quantity")),
                    share_pct=None,
                    aggregation_level=aggregation_level,
                    is_component=False,
                    source_locator="article_body:mhev_summary",
                )
            )
    return records


def validate_silver(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Validate ABVE Silver records and reconcile published totals."""

    required = {"reference_period", "category_original", "technology_standardized", "quantity"}
    null_critical_count = sum(
        1 for record in records if any(record.get(field) in (None, "") for field in required)
    )
    negative_quantity_count = sum(1 for record in records if record["quantity"] < 0)
    keys = [(record["reference_period"], record["category_original"]) for record in records]
    duplicate_count = len(keys) - len(set(keys))
    by_category = {record["category_original"]: record["quantity"] for record in records}
    component_total = sum(by_category.get(category, 0) for category in COMPONENT_CATEGORIES)
    published_total = by_category.get("TOTAL")
    total_reconciles = published_total is not None and component_total == published_total
    mhev_reconciles = (
        by_category.get("MHEV") is None
        or by_category["MHEV"] == by_category.get("MHEV 48V", 0) + by_category.get("MHEV 12V", 0)
    )
    status = (
        "PASS"
        if records
        and null_critical_count == 0
        and negative_quantity_count == 0
        and duplicate_count == 0
        and total_reconciles
        and mhev_reconciles
        else "FAIL"
    )
    return {
        "status": status,
        "row_count": len(records),
        "duplicate_count": duplicate_count,
        "null_critical_count": null_critical_count,
        "negative_quantity_count": negative_quantity_count,
        "component_total": component_total,
        "published_total": published_total,
        "total_reconciles": total_reconciles,
        "mhev_reconciles": mhev_reconciles,
    }


def _load_metadata(html_path: Path) -> SourceMetadata:
    metadata_path = html_path.with_name(html_path.name + ".metadata.json")
    if not metadata_path.is_file():
        raise IngestionError(f"ABVE Bronze metadata not found: {metadata_path}")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    return SourceMetadata(
        source_name=metadata["source_name"],
        source_url=metadata["source_url"],
        reference_period=metadata["reference_period"],
        source_file=metadata["source_file"],
        file_hash=metadata.get("file_hash") or sha256_file(html_path),
    )


def _write_csv(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def standardize_report(html_path: Path, *, output_root: Path = Path("data/silver/abve")) -> dict[str, Any]:
    """Transform an ABVE Bronze HTML evidence page into Silver."""

    html_path = Path(html_path)
    if not html_path.is_file():
        raise IngestionError(f"ABVE Bronze HTML not found: {html_path}")
    metadata = _load_metadata(html_path)
    text = extract_text(html_path.read_text(encoding="utf-8", errors="replace"))
    records = parse_abve_text(text, metadata=metadata)
    quality = validate_silver(records)
    if quality["status"] != "PASS":
        raise IngestionError(f"ABVE Silver quality validation failed: {quality}")

    period_root = Path(output_root) / metadata.reference_period
    _write_csv(period_root / "technology_monthly.csv", records)
    quality_report = {
        **quality,
        "reference_period": metadata.reference_period,
        "source_file": metadata.source_file,
        "source_hash": metadata.file_hash,
    }
    (period_root / "quality_report.json").write_text(
        json.dumps(quality_report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return quality_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Standardize an ABVE Bronze HTML page into Silver.")
    parser.add_argument("--html", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, default=Path("data/silver/abve"))
    args = parser.parse_args()
    print(json.dumps(standardize_report(args.html, output_root=args.output_root), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
