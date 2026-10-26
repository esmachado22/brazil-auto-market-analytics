"""SENATRAN/RENAVAM resource discovery and Bronze ingestion."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen
from zipfile import BadZipFile, ZipFile, is_zipfile

from .framework import IngestionError, IngestionFramework, IngestionRecord, SourceSpec


SENATRAN_CKAN_API_URL = (
    "https://dados.transportes.gov.br/api/3/action/package_show"
    "?id=registro-nacional-de-veiculos-automotores-renavam"
)
SENATRAN_DATASET_URL = "https://dados.transportes.gov.br/dataset/registro-nacional-de-veiculos-automotores-renavam"
MONTHS_PT = {
    1: "janeiro",
    2: "fevereiro",
    3: "marco",
    4: "abril",
    5: "maio",
    6: "junho",
    7: "julho",
    8: "agosto",
    9: "setembro",
    10: "outubro",
    11: "novembro",
    12: "dezembro",
}
PERIOD_PATTERN = re.compile(r"^(?P<year>20\d{2})-(?P<month>0[1-9]|1[0-2])$")


@dataclass(frozen=True)
class SenatranResource:
    """Official RENAVAM resource for one monthly inventory snapshot."""

    reference_period: str
    description: str
    source_url: str
    source_file: str
    size_bytes: int | None
    resource_id: str


def _period_description(period: str) -> str:
    match = PERIOD_PATTERN.fullmatch(period)
    if not match:
        raise ValueError("period must use YYYY-MM format")
    month_name = MONTHS_PT[int(match.group("month"))]
    return f"{month_name} de {match.group('year')}"


def parse_resources(payload: dict) -> list[SenatranResource]:
    """Parse the CKAN package response into monthly marca/modelo resources."""

    resources: list[SenatranResource] = []
    for item in payload.get("result", {}).get("resources", []):
        description = str(item.get("description", ""))
        source_url = str(item.get("url", ""))
        if "uf, município e tipo de veículo" not in description.lower():
            continue
        if "marca_e_modelo" not in source_url.lower():
            continue
        match = re.search(r"(janeiro|fevereiro|marco|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)_(20\d{2})", source_url.lower())
        if not match:
            continue
        month = next(number for number, name in MONTHS_PT.items() if name == match.group(1))
        reference_period = f"{match.group(2)}-{month:02d}"
        resources.append(
            SenatranResource(
                reference_period=reference_period,
                description=description,
                source_url=source_url,
                source_file=unquote(Path(urlparse(source_url).path).name),
                size_bytes=int(item["size"]) if item.get("size") is not None else None,
                resource_id=str(item.get("id", "")),
            )
        )
    return sorted(resources, key=lambda resource: resource.reference_period)


def discover_resources(api_url: str = SENATRAN_CKAN_API_URL, *, timeout_seconds: int = 60) -> list[SenatranResource]:
    """Read the official CKAN catalog and discover real monthly resources."""

    request = Request(api_url, headers={"User-Agent": "BrazilAutoMarketAnalytics/1.0"})
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise IngestionError(f"Could not read SENATRAN catalog: {api_url}") from exc
    resources = parse_resources(payload)
    if not resources:
        raise IngestionError("SENATRAN catalog returned no marca/modelo resources")
    return resources


def build_spec(resource: SenatranResource, *, destination_root: Path) -> SourceSpec:
    """Build the generic ingestion specification for one SENATRAN resource."""

    return SourceSpec(
        source_name="SENATRAN_RENAVAM",
        source_url=resource.source_url,
        reference_period=resource.reference_period,
        source_file=resource.source_file,
        destination_dir=Path(destination_root) / resource.reference_period,
    )


def validate_archive(record: IngestionRecord) -> None:
    """Validate that a Bronze resource is a readable, non-empty ZIP archive."""

    path = Path(record.local_path)
    if record.file_size_bytes <= 0 or not path.is_file() or path.suffix.lower() != ".zip":
        raise IngestionError(f"SENATRAN file is empty, missing or not ZIP: {path}")
    if not is_zipfile(path):
        raise IngestionError(f"SENATRAN file is not a valid ZIP archive: {path}")
    try:
        with ZipFile(path) as archive:
            if not archive.namelist():
                raise IngestionError(f"SENATRAN archive has no members: {path}")
    except BadZipFile as exc:
        raise IngestionError(f"SENATRAN archive cannot be read: {path}") from exc


def ingest_period(
    period: str,
    *,
    destination_root: Path = Path("data/bronze/senatran"),
    api_url: str = SENATRAN_CKAN_API_URL,
    timeout_seconds: int = 60,
) -> IngestionRecord:
    """Discover and ingest one real SENATRAN monthly archive into Bronze."""

    resources = {resource.reference_period: resource for resource in discover_resources(api_url, timeout_seconds=timeout_seconds)}
    if period not in resources:
        available = ", ".join(sorted(resources)) or "none"
        raise IngestionError(f"SENATRAN period not found: {period}. Available: {available}")

    framework = IngestionFramework()
    record = framework.download(build_spec(resources[period], destination_root=destination_root), timeout_seconds=timeout_seconds)
    validate_archive(record)
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest one SENATRAN RENAVAM monthly archive into Bronze.")
    parser.add_argument("--period", required=True, help="Reference period in YYYY-MM format, for example 2026-09.")
    parser.add_argument("--destination-root", type=Path, default=Path("data/bronze/senatran"))
    parser.add_argument("--api-url", default=SENATRAN_CKAN_API_URL)
    parser.add_argument("--timeout-seconds", type=int, default=120)
    args = parser.parse_args()
    record = ingest_period(
        args.period,
        destination_root=args.destination_root,
        api_url=args.api_url,
        timeout_seconds=args.timeout_seconds,
    )
    print(f"INGESTED={record.local_path}")
    print(f"PERIOD={record.reference_period}")
    print(f"BYTES={record.file_size_bytes}")
    print(f"SHA256={record.file_hash}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
