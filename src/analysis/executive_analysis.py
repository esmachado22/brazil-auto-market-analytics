"""Build a validated executive analysis from supplied Gold metrics.

This module deliberately does not call an LLM or external service. It produces
an auditable structured result from the values supplied by the pipeline.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any, Iterable, Mapping


ALLOWED_METRICS = {
    "volume",
    "market_share",
    "growth_pct",
    "electrified_volume",
    "price_reference",
    "fleet_stock",
}
PERIOD_PATTERN = re.compile(r"^\d{4}-\d{2}$")
REQUIRED_FIELDS = {"periodo", "metrica", "nome", "valor", "fonte"}


class AnalysisInputError(ValueError):
    """Raised when an executive metric is not safe to analyze."""


def _validate_record(record: Mapping[str, Any]) -> dict[str, Any]:
    missing = sorted(REQUIRED_FIELDS - set(record))
    if missing:
        raise AnalysisInputError(f"metric is missing fields: {', '.join(missing)}")
    period = str(record["periodo"])
    metric = str(record["metrica"])
    if not PERIOD_PATTERN.fullmatch(period):
        raise AnalysisInputError(f"invalid period: {period}")
    if metric not in ALLOWED_METRICS:
        raise AnalysisInputError(f"metric is not allowed: {metric}")
    if not str(record["nome"]).strip() or not str(record["fonte"]).strip():
        raise AnalysisInputError("metric name and source cannot be empty")
    try:
        value = float(record["valor"])
    except (TypeError, ValueError) as exc:
        raise AnalysisInputError("metric value must be numeric") from exc
    if not math.isfinite(value):
        raise AnalysisInputError("metric value must be finite")
    normalized = dict(record)
    normalized["periodo"] = period
    normalized["metrica"] = metric
    normalized["nome"] = str(record["nome"])
    normalized["fonte"] = str(record["fonte"])
    normalized["valor"] = value
    return normalized


def build_executive_analysis(records: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Return the stable structured output used by reports and downstream BI."""

    validated = [_validate_record(record) for record in records]
    periods = sorted({record["periodo"] for record in validated})
    if len(periods) > 1:
        raise AnalysisInputError("all metrics in one analysis must use the same period")
    period = periods[0] if periods else None
    movements: list[dict[str, Any]] = []
    for record in validated:
        if record["metrica"] != "growth_pct":
            continue
        direction = "crescimento" if record["valor"] > 0 else "queda" if record["valor"] < 0 else "estabilidade"
        movements.append(
            {
                "nome": record["nome"],
                "direcao": direction,
                "variacao_pct": record["valor"],
                "fonte": record["fonte"],
            }
        )
    alerts: list[str] = []
    if not validated:
        alerts.append("Nenhuma métrica foi fornecida; não há conclusão executiva.")
    if any(record["metrica"] == "price_reference" for record in validated):
        alerts.append("Preços são referências FIPE e não representam transações efetivas.")
    if any(record["metrica"] == "fleet_stock" for record in validated):
        alerts.append("Estoque de frota não deve ser interpretado como volume de vendas.")
    if not movements and validated:
        alerts.append("Nenhuma métrica de crescimento foi fornecida para calcular movimentos.")
    summary = (
        f"Foram observadas {len(validated)} métricas no período {period}."
        if period
        else "Não há métricas observadas."
    )
    return {
        "periodo": period,
        "resumo": summary,
        "principais_movimentos": movements,
        "dados_observados": validated,
        "alertas": alerts,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a structured executive analysis from metric JSON.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise AnalysisInputError("input JSON must be a list of metrics")
    result = build_executive_analysis(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
