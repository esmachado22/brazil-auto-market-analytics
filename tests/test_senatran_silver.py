import csv
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from openpyxl import Workbook

from src.transformations.senatran import build_silver_from_bronze, _split_brand_model


class SenatranSilverTests(unittest.TestCase):
    def test_split_brand_model_preserves_model_when_brand_separator_exists(self) -> None:
        self.assertEqual(_split_brand_model("TOYOTA/COROLLA CROSS"), ("TOYOTA", "COROLLA CROSS"))
        self.assertEqual(_split_brand_model("UNKNOWN"), ("UNKNOWN", "UNKNOWN"))

    def test_build_silver_reads_zip_and_xlsx_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            bronze = root / "bronze" / "senatran" / "2026-09"
            auxiliary = bronze / "auxiliary"
            auxiliary.mkdir(parents=True)
            zip_path = bronze / "frota.zip"
            with ZipFile(zip_path, "w") as archive:
                archive.writestr("frota.txt", "UF;Município;Marca Modelo;Ano Fabricação Veículo;Qtd. Veículos\nSP;SAO PAULO;TOYOTA/COROLLA;2020;2.0\n")
            metadata = {"source_name": "SENATRAN_RENAVAM", "source_url": "https://example.org/frota.zip", "source_file": "frota.zip", "file_hash": "hash"}
            (zip_path.with_name(zip_path.name + ".metadata.json")).write_text(json.dumps(metadata), encoding="utf-8")
            for name, header, rows in (
                ("D_Frota_por_UF_Municipio_COMBUSTIVEL_Setembro_2026.xlsx", ("UF", "Município", "Combustível Veículo", "Qtd. Veículos"), [("SP", "SAO PAULO", "GASOLINA", 2)]),
                ("E_Frota_por_UF_Municipio_POTENCIA_Setembro_2026.xlsx", ("UF", "Município", "Potência Veículo", "Qtd. Veículos"), [("SP", "SAO PAULO", 120, 2)]),
            ):
                workbook = Workbook()
                sheet = workbook.active
                sheet.append(header)
                for row in rows:
                    sheet.append(row)
                path = auxiliary / name
                workbook.save(path)
                metadata["source_file"] = name
                (path.with_name(path.name + ".metadata.json")).write_text(json.dumps(metadata), encoding="utf-8")

            report = build_silver_from_bronze("2026-09", bronze_root=root / "bronze" / "senatran", silver_root=root / "silver" / "senatran")

            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["outputs"]["fleet_brand_model"]["rows"], 1)
            with (root / "silver/senatran/2026-09/fleet_fuel.csv").open(encoding="utf-8", newline="") as file_obj:
                self.assertEqual(next(csv.DictReader(file_obj))["fuel_original"], "GASOLINA")


if __name__ == "__main__":
    unittest.main()
