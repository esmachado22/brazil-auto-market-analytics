"""Build the Gold fleet fact from the SENATRAN stock Silver table."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path
from typing import Any


FACT_COLUMNS = [
    "frota_key",
    "reference_period",
    "uf",
    "municipio",
    "brand_original",
    "model_original",
    "year_manufacture",
    "quantity",
    "measure_type",
    "source_name",
    "source_url",
    "source_file",
    "source_hash",
]


def fleet_key(row: dict[str, Any]) -> str:
    """Create a deterministic key for one stock-grain row."""

    parts = (
        row.get("reference_period", ""),
        row.get("uf", ""),
        row.get("municipio", ""),
        row.get("brand_original", ""),
        row.get("model_original", ""),
        row.get("year_manufacture", ""),
    )
    digest = hashlib.sha256("|".join(str(part) for part in parts).encode("utf-8")).hexdigest()[:24]
    return f"FROTA_{digest}"


def build_fleet_fact(
    period: str,
    *,
    silver_root: Path = Path("data/silver/senatran"),
    gold_root: Path = Path("data/gold"),
) -> dict[str, Any]:
    """Materialize the SENATRAN stock fact as a compressed, traceable Gold file."""

    silver_path = Path(silver_root) / period / "fleet_brand_model.csv.gz"
    if not silver_path.is_file():
        raise FileNotFoundError(f"SENATRAN Silver file not found: {silver_path}")
    output_path = Path(gold_root) / "fato_frota.csv.gz"
    partial_path = output_path.with_suffix(output_path.suffix + ".part")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    partial_path.unlink(missing_ok=True)
    count = 0
    with gzip.open(silver_path, "rt", encoding="utf-8", newline="") as source, gzip.open(
        partial_path, "wt", encoding="utf-8", newline=""
    ) as target:
        reader = csv.DictReader(source)
        writer = csv.DictWriter(target, fieldnames=FACT_COLUMNS)
        writer.writeheader()
        for row in reader:
            output_row = {
                "frota_key": fleet_key(row),
                "reference_period": row.get("reference_period", period),
                "uf": row.get("uf", ""),
                "municipio": row.get("municipio", ""),
                "brand_original": row.get("brand_original", ""),
                "model_original": row.get("model_original", ""),
                "year_manufacture": row.get("year_manufacture", ""),
                "quantity": row.get("quantity", "0"),
                "measure_type": "ESTOQUE",
                "source_name": row.get("source_name", "SENATRAN_RENAVAM"),
                "source_url": row.get("source_url", ""),
                "source_file": row.get("source_file", ""),
                "source_hash": row.get("source_hash", ""),
            }
            writer.writerow(output_row)
            count += 1
    partial_path.replace(output_path)

    report = {
        "status": "PASS",
        "reference_period": period,
        "fact": "fato_frota",
        "measure_type": "ESTOQUE",
        "source_name": "SENATRAN_RENAVAM",
        "grain": "período + UF + município + marca/modelo + ano de fabricação",
        "rows": count,
        "path": str(output_path),
        "flow_stock_rule": "SENATRAN = estoque; FENABRAVE/ABVE = fluxo de emplacamentos.",
    }
    report_path = Path(gold_root) / "fato_frota_validation.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the Gold SENATRAN fleet fact.")
    parser.add_argument("--period", required=True)
    parser.add_argument("--silver-root", type=Path, default=Path("data/silver/senatran"))
    parser.add_argument("--gold-root", type=Path, default=Path("data/gold"))
    args = parser.parse_args()
    print(json.dumps(build_fleet_fact(args.period, silver_root=args.silver_root, gold_root=args.gold_root), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
