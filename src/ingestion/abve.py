"""ABVE Data evidence-page ingestion into Bronze."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .framework import IngestionError, IngestionFramework, IngestionRecord, SourceSpec


ABVE_DATA_URL = "https://abve.org.br/abve-data/eletrificadosmhev/"
ABVE_DEFAULT_REPORT_URL = (
    "https://abve.org.br/com-57-mil-emplacamentos-em-agosto-eletrificados-"
    "abrem-a-corrida-para-o-milhao-em-setembro/"
)
ORIGINAL_CATEGORIES = ("BEV", "PHEV", "HEV", "HEV Flex", "MHEV")


@dataclass(frozen=True)
class AbveReport:
    """Official ABVE evidence page associated with one reference period."""

    reference_period: str
    source_url: str
    source_file: str


def build_report(
    reference_period: str,
    source_url: str = ABVE_DEFAULT_REPORT_URL,
) -> AbveReport:
    """Build a report descriptor without changing the source content."""

    if len(reference_period) != 7 or reference_period[4] != "-":
        raise ValueError("reference_period must use YYYY-MM")
    year, month = reference_period.split("-")
    if not year.isdigit() or not month.isdigit() or not 1 <= int(month) <= 12:
        raise ValueError("reference_period must use a valid YYYY-MM")
    if not source_url.startswith("https://abve.org.br/"):
        raise ValueError("source_url must be an official ABVE HTTPS URL")

    return AbveReport(
        reference_period=reference_period,
        source_url=source_url,
        source_file=f"abve_{year}_{month}.html",
    )


def build_spec(report: AbveReport, *, destination_root: Path) -> SourceSpec:
    """Build the generic ingestion specification for one ABVE report."""

    return SourceSpec(
        source_name="ABVE",
        source_url=report.source_url,
        reference_period=report.reference_period,
        source_file=report.source_file,
        destination_dir=Path(destination_root) / report.reference_period,
    )


def validate_html(record: IngestionRecord) -> None:
    """Validate that the preserved evidence page is non-empty and has ABVE categories."""

    path = Path(record.local_path)
    if record.file_size_bytes <= 0 or not path.is_file():
        raise IngestionError(f"ABVE evidence file is empty or missing: {path}")

    content = path.read_text(encoding="utf-8", errors="replace")
    normalized_content = content.casefold()
    missing_categories = [
        category for category in ORIGINAL_CATEGORIES if category.casefold() not in normalized_content
    ]
    if missing_categories:
        missing = ", ".join(missing_categories)
        raise IngestionError(f"ABVE evidence is missing original categories: {missing}")


def fetch_index(*, timeout_seconds: int = 60) -> str:
    """Fetch the official ABVE Data page for source inspection."""

    request = Request(ABVE_DATA_URL, headers={"User-Agent": "BrazilAutoMarketAnalytics/1.0"})
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            return response.read().decode("utf-8", errors="replace")
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        raise IngestionError(f"Could not read ABVE Data page: {ABVE_DATA_URL}") from exc


def ingest_report(
    report: AbveReport,
    *,
    destination_root: Path = Path("data/bronze/abve"),
    timeout_seconds: int = 60,
) -> IngestionRecord:
    """Download and validate one official ABVE evidence page into Bronze."""

    framework = IngestionFramework()
    record = framework.download(
        build_spec(report, destination_root=destination_root),
        timeout_seconds=timeout_seconds,
    )
    validate_html(record)
    return record


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest one ABVE Data evidence page into Bronze.")
    parser.add_argument("--period", default="2026-08", help="Reference period in YYYY-MM format.")
    parser.add_argument("--url", default=ABVE_DEFAULT_REPORT_URL, help="Official ABVE evidence-page URL.")
    parser.add_argument("--destination-root", type=Path, default=Path("data/bronze/abve"))
    parser.add_argument("--timeout-seconds", type=int, default=60)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    record = ingest_report(
        build_report(args.period, args.url),
        destination_root=args.destination_root,
        timeout_seconds=args.timeout_seconds,
    )
    print(f"INGESTED={record.local_path}")
    print(f"PERIOD={record.reference_period}")
    print(f"BYTES={record.file_size_bytes}")
    print(f"SHA256={record.file_hash}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
