import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from src.ingestion.framework import IngestionError, IngestionRecord
from src.ingestion.senatran import (
    SenatranResource,
    build_auxiliary_specs,
    build_spec,
    parse_resources,
    validate_archive,
)


class SenatranIngestionTests(unittest.TestCase):
    def test_parse_resources_keeps_marca_modelo_period_and_size(self) -> None:
        payload = {
            "result": {
                "resources": [
                    {
                        "id": "resource-1",
                        "description": "Quantidade de veículos registrados por uf, município e tipo de veículo no mês de Setembro de 2026",
                        "url": "https://dados.transportes.gov.br/download/i_frota_por_uf_municipio_marca_e_modelo_ano_setembro_2026.zip",
                        "size": 136926215,
                    },
                    {
                        "id": "ignored",
                        "description": "Quantidade de veículos registrados por uf, município e tipo de veículo no mês de Setembro de 2026",
                        "url": "https://dados.transportes.gov.br/download/i_frota_por_uf_municipio_combustivel_setembro_2026.zip",
                        "size": 10,
                    },
                ]
            }
        }

        resources = parse_resources(payload)

        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0].reference_period, "2026-09")
        self.assertEqual(resources[0].size_bytes, 136926215)

    def test_build_spec_partitions_by_period(self) -> None:
        resource = SenatranResource(
            reference_period="2026-09",
            description="resource",
            source_url="https://example.org/frota.zip",
            source_file="frota.zip",
            size_bytes=10,
            resource_id="r1",
        )

        spec = build_spec(resource, destination_root=Path("data/bronze/senatran"))

        self.assertEqual(spec.source_name, "SENATRAN_RENAVAM")
        self.assertEqual(spec.destination_dir, Path("data/bronze/senatran/2026-09"))

    def test_build_auxiliary_specs_uses_official_fuel_and_power_files(self) -> None:
        specs = build_auxiliary_specs("2026-09", destination_root=Path("data/bronze/senatran"))

        self.assertEqual(len(specs), 2)
        self.assertIn("COMBUSTIVEL", specs[0].source_file)
        self.assertIn("POTENCIA", specs[1].source_file)
        self.assertTrue(all(spec.destination_dir.name == "auxiliary" for spec in specs))

    def test_validate_archive_accepts_zip(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "frota.zip"
            with ZipFile(path, "w") as archive:
                archive.writestr("frota.csv", "UF;MUNICIPIO;QUANTIDADE\nSP;São Paulo;1\n")
            record = IngestionRecord(
                source_name="SENATRAN_RENAVAM",
                source_url="https://example.org/frota.zip",
                reference_period="2026-09",
                source_file="frota.zip",
                local_path=str(path),
                metadata_path=str(path) + ".metadata.json",
                file_hash="unused",
                file_size_bytes=path.stat().st_size,
                ingestion_timestamp="2026-10-26T00:00:00+00:00",
            )

            validate_archive(record)

    def test_validate_archive_rejects_non_zip(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "frota.zip"
            path.write_bytes(b"not a zip")
            record = IngestionRecord(
                source_name="SENATRAN_RENAVAM",
                source_url="https://example.org/frota.zip",
                reference_period="2026-09",
                source_file="frota.zip",
                local_path=str(path),
                metadata_path=str(path) + ".metadata.json",
                file_hash="unused",
                file_size_bytes=path.stat().st_size,
                ingestion_timestamp="2026-10-26T00:00:00+00:00",
            )

            with self.assertRaises(IngestionError):
                validate_archive(record)


if __name__ == "__main__":
    unittest.main()
