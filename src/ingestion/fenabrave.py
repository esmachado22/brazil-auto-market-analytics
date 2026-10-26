"""FENABRAVE report discovery and Bronze ingestion."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse
from urllib.request import Request, urlopen

from .framework import IngestionError, IngestionFramework, IngestionRecord, SourceSpec


FENABRAVE_INDEX_URL = "https://www.fenabrave.org.br/Portal/conteudo/emplacamentos"
PERIOD_PATTERN = re.compile(r"(?P<year>20\d{2})[_-](?P<month>0[1-9]|1[0-2])")


@dataclass(frozen=True)
class FenabraveReport:
    """Official report discovered in the FENABRAVE index."""

    reference_period: str
    source_url: str
    source_file: str


class _LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        href = dict(attrs).get("href")
        if href:
            self.links.append(href)


def discover_reports(html: str, *, index_url: str = FENABRAVE_INDEX_URL) -> list[FenabraveReport]:
    """Extract unique monthly PDF reports from an official index page."""

    parser = _LinkParser()
    parser.feed(html)
    reports: dict[str, FenabraveReport] = {}

    for href in parser.links:
        source_url = _normalize_source_url(urljoin(index_url, href))
        parsed_url = urlparse(source_url)
        source_file = unquote(Path(parsed_url.path).name)
        if parsed_url.scheme not in {"http", "https"} or not source_file.lower().endswith(".pdf"):
            continue

        match = PERIOD_PATTERN.search(source_file)
        if not match:
            continue
        reference_period = f"{match.group('year')}-{match.group('month')}"
        reports[reference_period] = FenabraveReport(
            reference_period=reference_period,
            source_url=source_url,
            source_file=source_file,
        )

    return sorted(reports.values(), key=lambda report: report.reference_period)


def _normalize_source_url(source_url: str) -> str:
    """Use HTTPS when the official FENABRAVE index publishes HTTP links."""

    parsed_url = urlparse(source_url)
    if parsed_url.scheme == "http" and parsed_url.hostname == "www.fenabrave.org.br":
        return source_url.replace("http://", "https://", 1)
    return source_url


def fetch_reports(index_url: str = FENABRAVE_INDEX_URL, *, timeout_seconds: int = 60) -> list[FenabraveReport]:
    """Read the official index page and discover its report links."""

    request = Request(index_url, headers={"User-Agent": "BrazilAutoMarketAnalytics/1.0"})
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            html = response.read().decode("utf-8", errors="replace")
    except OSError as exc:
        raise IngestionError(f"Could not read FENABRAVE index: {index_url}") from exc
    return discover_reports(html, index_url=index_url)


def build_spec(report: FenabraveReport, *, destination_root: Path) -> SourceSpec:
    """Build the generic ingestion specification for one FENABRAVE report."""

    return SourceSpec(
        source_name="FENABRAVE",
        source_url=report.source_url,
        reference_period=report.reference_period,
        source_file=report.source_file,
        destination_dir=Path(destination_root) / report.reference_period,
    )


def validate_pdf(record: IngestionRecord) -> None:
    """Validate that an ingested report is a non-empty PDF file."""

    path = Path(record.local_path)
    if record.file_size_bytes <= 0 or not path.is_file():
        raise IngestionError(f"FENABRAVE file is empty or missing: {path}")
    with path.open("rb") as file_obj:
        signature = file_obj.read(5)
    if signature != b"%PDF-":
        raise IngestionError(f"FENABRAVE file is not a PDF: {path}")


def ingest_period(
    period: str,
    *,
    destination_root: Path = Path("data/bronze/fenabrave"),
    index_url: str = FENABRAVE_INDEX_URL,
    timeout_seconds: int = 60,
) -> IngestionRecord:
    """Discover and ingest one real FENABRAVE report into Bronze."""

    reports = {report.reference_period: report for report in fetch_reports(index_url, timeout_seconds=timeout_seconds)}
    if period not in reports:
        available = ", ".join(sorted(reports)) or "none"
        raise IngestionError(f"FENABRAVE period not found: {period}. Available: {available}")

    framework = IngestionFramework()
    record = framework.download(
        build_spec(reports[period], destination_root=destination_root),
        timeout_seconds=timeout_seconds,
    )
    validate_pdf(record)
    return record


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest one FENABRAVE monthly report into Bronze.")
    parser.add_argument("--period", required=True, help="Reference period in YYYY-MM format, for example 2026-01.")
    parser.add_argument("--destination-root", type=Path, default=Path("data/bronze/fenabrave"))
    parser.add_argument("--index-url", default=FENABRAVE_INDEX_URL)
    parser.add_argument("--timeout-seconds", type=int, default=60)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    record = ingest_period(
        args.period,
        destination_root=args.destination_root,
        index_url=args.index_url,
        timeout_seconds=args.timeout_seconds,
    )
    print(f"INGESTED={record.local_path}")
    print(f"PERIOD={record.reference_period}")
    print(f"BYTES={record.file_size_bytes}")
    print(f"SHA256={record.file_hash}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
