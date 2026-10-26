"""Standardize the FENABRAVE PDF Bronze artifact into Silver CSV files."""

from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from src.ingestion.framework import IngestionError, sha256_file


SEGMENT_LABELS = {
    "A) AUTOS": "AUTOMOVEIS",
    "B) COM. LEVES": "COMERCIAIS_LEVES",
    "A + B": "AUTOMOVEIS_E_COMERCIAIS_LEVES",
    "C) CAMINHOES": "CAMINHOES",
    "D) ONIBUS": "ONIBUS",
    "C + D": "CAMINHOES_E_ONIBUS",
    "SUBTOTAL": "SUBTOTAL",
    "E) MOTOS": "MOTOS",
    "F) IMPL. ROD.": "IMPLEMENTOS_RODOVIARIOS",
    "OUTROS": "OUTROS",
    "TOTAL": "TOTAL",
}

SUMMARY_FIELDS = (
    "quantity_month",
    "quantity_previous_month",
    "quantity_accumulated",
    "quantity_same_month_previous_year",
    "quantity_accumulated_previous_year",
    "variation_vs_previous_month_pct",
    "variation_vs_same_month_previous_year_pct",
    "variation_accumulated_vs_previous_year_pct",
)

DERIVED_TOTAL_COMPONENTS = (
    "AUTOMOVEIS_E_COMERCIAIS_LEVES",
    "CAMINHOES_E_ONIBUS",
    "MOTOS",
    "IMPLEMENTOS_RODOVIARIOS",
    "OUTROS",
)


@dataclass(frozen=True)
class SourceMetadata:
    source_name: str
    source_url: str
    reference_period: str
    source_file: str
    file_hash: str


def normalize_text(value: str) -> str:
    """Remove accents and normalize whitespace for matching source labels."""

    without_accents = "".join(
        char for char in unicodedata.normalize("NFKD", value) if not unicodedata.combining(char)
    )
    return " ".join(without_accents.upper().split())


def parse_integer(value: str) -> int:
    """Parse FENABRAVE's dot-separated thousands format."""

    cleaned = value.strip().replace(".", "")
    if not re.fullmatch(r"-?\d+", cleaned):
        raise ValueError(f"Invalid integer value: {value}")
    return int(cleaned)


def parse_decimal(value: str) -> float:
    """Parse FENABRAVE's comma decimal format."""

    cleaned = value.strip().replace(".", "").replace(",", ".")
    return float(cleaned)


def parse_summary_lines(
    text: str,
    *,
    metadata: SourceMetadata,
    source_page: int = 1,
) -> list[dict[str, Any]]:
    """Parse the monthly segment summary from the first report page."""

    records: list[dict[str, Any]] = []
    labels_by_length = sorted(SEGMENT_LABELS, key=len, reverse=True)
    for raw_line in text.splitlines():
        normalized_line = normalize_text(raw_line)
        matched_label = next(
            (
                label
                for label in labels_by_length
                if normalized_line == label or normalized_line.startswith(label + " ")
            ),
            None,
        )
        if matched_label is None:
            continue

        tokens = normalized_line[len(matched_label) :].strip().split()
        if len(tokens) < len(SUMMARY_FIELDS):
            continue
        quantities = [parse_integer(token) for token in tokens[:5]]
        variations = [parse_decimal(token) for token in tokens[5:8]]
        values = quantities + variations
        raw_label = raw_line.strip()[: raw_line.find(tokens[0])].strip()
        record = {
            "reference_period": metadata.reference_period,
            "source_name": metadata.source_name,
            "source_url": metadata.source_url,
            "source_file": metadata.source_file,
            "source_hash": metadata.file_hash,
            "source_page": source_page,
            "segment_original": raw_label or matched_label,
            "segment_standardized": SEGMENT_LABELS[matched_label],
        }
        record.update(dict(zip(SUMMARY_FIELDS, values)))
        records.append(record)

    if not any(record["segment_standardized"] == "TOTAL" for record in records):
        by_segment = {record["segment_standardized"]: record for record in records}
        if all(segment in by_segment for segment in DERIVED_TOTAL_COMPONENTS):
            total_record = {
                "reference_period": metadata.reference_period,
                "source_name": metadata.source_name,
                "source_url": metadata.source_url,
                "source_file": metadata.source_file,
                "source_hash": metadata.file_hash,
                "source_page": source_page,
                "segment_original": "TOTAL (DERIVADO DOS SEGMENTOS PUBLICADOS)",
                "segment_standardized": "TOTAL",
            }
            for field in SUMMARY_FIELDS[:5]:
                total_record[field] = sum(
                    int(by_segment[segment][field]) for segment in DERIVED_TOTAL_COMPONENTS
                )
            for field in SUMMARY_FIELDS[5:]:
                total_record[field] = None
            records.append(total_record)

    return records


def _group_words_by_line(words: Iterable[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    lines: list[tuple[float, list[dict[str, Any]]]] = []
    for word in sorted(words, key=lambda item: (float(item["top"]), float(item["x0"]))):
        top = float(word["top"])
        line = next((line for line in lines if abs(line[0] - top) <= 1.5), None)
        if line is None:
            lines.append((top, [word]))
        else:
            line[1].append(word)
    return [sorted(line_words, key=lambda item: float(item["x0"])) for _, line_words in lines]


def _parse_rank(words: list[dict[str, Any]], *, minimum_x: float, maximum_x: float) -> int | None:
    candidates = [
        word["text"]
        for word in words
        if minimum_x <= float(word["x0"]) < maximum_x and re.match(r"^\d+", word["text"])
    ]
    if not candidates:
        return None
    return int(re.match(r"^(\d+)", candidates[0]).group(1))


def _parse_quantity_word(words: list[dict[str, Any]], *, minimum_x: float, maximum_x: float) -> int | None:
    for word in words:
        if minimum_x <= float(word["x0"]) < maximum_x and re.fullmatch(r"\d[\d.]*", word["text"]):
            return parse_integer(word["text"])
    return None


def _parse_model(words: list[dict[str, Any]], *, minimum_x: float, maximum_x: float) -> str:
    return " ".join(
        word["text"]
        for word in words
        if minimum_x <= float(word["x0"]) < maximum_x
    ).strip()


def _model_parts(model: str) -> tuple[str | None, str]:
    if "/" not in model:
        return None, model
    brand, model_name = model.split("/", 1)
    return brand.strip() or None, model_name.strip()


def parse_ranking_words(
    words: Iterable[dict[str, Any]],
    *,
    metadata: SourceMetadata,
    source_page: int,
    category_left: str = "AUTOMOVEIS",
    category_right: str = "COMERCIAIS_LEVES",
) -> list[dict[str, Any]]:
    """Parse the two-column model ranking using the PDF word coordinates."""

    records: list[dict[str, Any]] = []
    for line_words in _group_words_by_line(words):
        candidates = (
            ("left", _parse_rank(line_words, minimum_x=0, maximum_x=110), _parse_model(line_words, minimum_x=100, maximum_x=240), _parse_quantity_word(line_words, minimum_x=235, maximum_x=300), category_left),
            ("right", _parse_rank(line_words, minimum_x=300, maximum_x=370), _parse_model(line_words, minimum_x=350, maximum_x=490), _parse_quantity_word(line_words, minimum_x=490, maximum_x=560), category_right),
        )
        for _, rank, model, quantity, category in candidates:
            if rank is None or not model or quantity is None:
                continue
            brand, model_name = _model_parts(model)
            records.append(
                {
                    "reference_period": metadata.reference_period,
                    "source_name": metadata.source_name,
                    "source_url": metadata.source_url,
                    "source_file": metadata.source_file,
                    "source_hash": metadata.file_hash,
                    "source_page": source_page,
                    "category_standardized": category,
                    "rank": rank,
                    "brand_original": brand,
                    "model_original": model_name,
                    "brand_model_original": model,
                    "quantity": quantity,
                }
            )
    return records


def validate_silver(records: list[dict[str, Any]], *, key_fields: tuple[str, ...]) -> dict[str, Any]:
    """Validate nulls, quantities and duplicate keys in a Silver dataset."""

    duplicate_keys: list[tuple[Any, ...]] = []
    seen: set[tuple[Any, ...]] = set()
    null_critical_count = 0
    negative_quantity_count = 0
    for record in records:
        key = tuple(record.get(field) for field in key_fields)
        if key in seen:
            duplicate_keys.append(key)
        seen.add(key)
        if any(record.get(field) in (None, "") for field in key_fields):
            null_critical_count += 1
        quantity = record.get("quantity", record.get("quantity_month"))
        if quantity is None or quantity < 0:
            negative_quantity_count += 1

    return {
        "status": "PASS"
        if not duplicate_keys and null_critical_count == 0 and negative_quantity_count == 0
        else "FAIL",
        "row_count": len(records),
        "duplicate_count": len(duplicate_keys),
        "null_critical_count": null_critical_count,
        "negative_quantity_count": negative_quantity_count,
        "duplicate_keys": [list(key) for key in duplicate_keys],
    }


def _load_metadata(pdf_path: Path) -> SourceMetadata:
    metadata_path = pdf_path.with_name(pdf_path.name + ".metadata.json")
    if not metadata_path.is_file():
        raise IngestionError(f"Bronze metadata not found: {metadata_path}")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    return SourceMetadata(
        source_name=metadata["source_name"],
        source_url=metadata["source_url"],
        reference_period=metadata["reference_period"],
        source_file=metadata["source_file"],
        file_hash=metadata.get("file_hash") or sha256_file(pdf_path),
    )


def _write_csv(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not records:
        raise IngestionError(f"No Silver records to write: {path}")
    with path.open("w", encoding="utf-8", newline="") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def standardize_report(pdf_path: Path, *, output_root: Path = Path("data/silver/fenabrave")) -> dict[str, Any]:
    """Extract and validate FENABRAVE summary and model ranking into Silver."""

    try:
        import pdfplumber
    except ImportError as exc:
        raise IngestionError("pdfplumber is required to standardize FENABRAVE PDFs") from exc

    pdf_path = Path(pdf_path)
    if not pdf_path.is_file():
        raise IngestionError(f"Bronze PDF not found: {pdf_path}")
    metadata = _load_metadata(pdf_path)
    with pdfplumber.open(pdf_path) as pdf:
        summary_records = parse_summary_lines(
            pdf.pages[0].extract_text() or "",
            metadata=metadata,
        )
        ranking_page_index = next(
            (
                index
                for index, page in enumerate(pdf.pages)
                if "RANKING DOS EMPLACAMENTOS EM" in normalize_text(page.extract_text() or "")
            ),
            None,
        )
        if ranking_page_index is None:
            raise IngestionError("FENABRAVE model ranking page was not found")
        ranking_records = parse_ranking_words(
            pdf.pages[ranking_page_index].extract_words(),
            metadata=metadata,
            source_page=ranking_page_index + 1,
        )

    if not summary_records:
        raise IngestionError("FENABRAVE segment summary produced no records")
    if not ranking_records:
        raise IngestionError("FENABRAVE model ranking produced no records")

    period_root = Path(output_root) / metadata.reference_period
    summary_quality = validate_silver(
        summary_records,
        key_fields=("reference_period", "segment_standardized", "source_file"),
    )
    ranking_quality = validate_silver(
        ranking_records,
        key_fields=("reference_period", "category_standardized", "rank", "source_file"),
    )
    if summary_quality["status"] != "PASS" or ranking_quality["status"] != "PASS":
        raise IngestionError("FENABRAVE Silver quality validation failed")

    _write_csv(period_root / "segment_totals.csv", summary_records)
    _write_csv(period_root / "model_rankings.csv", ranking_records)
    quality = {
        "status": "PASS",
        "reference_period": metadata.reference_period,
        "source_file": metadata.source_file,
        "source_hash": metadata.file_hash,
        "segment_totals": summary_quality,
        "model_rankings": ranking_quality,
    }
    (period_root / "quality_report.json").write_text(
        json.dumps(quality, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return quality


def main() -> int:
    parser = argparse.ArgumentParser(description="Standardize a FENABRAVE Bronze PDF into Silver.")
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, default=Path("data/silver/fenabrave"))
    args = parser.parse_args()
    quality = standardize_report(args.pdf, output_root=args.output_root)
    print(json.dumps(quality, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
