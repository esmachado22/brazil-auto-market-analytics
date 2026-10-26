# Silver ABVE

O módulo `src/transformations/abve.py` transforma o comunicado HTML preservado em Bronze em `technology_monthly.csv` e `quality_report.json`.

## Regras

- `BEV` → `ELETRICO`;
- `PHEV`, `HEV`, `HEV Flex` e `MHEV` → `HIBRIDO`;
- `TOTAL` é mantido como agregado e recebe `OUTRO` na classificação canônica;
- `BEV + PHEV + HEV + HEV Flex` deve reconciliar com `TOTAL`;
- `MHEV` permanece como categoria original e fica fora do total de eletrificados;
- `MHEV 48V + MHEV 12V` deve reconciliar com `MHEV` quando os três valores forem publicados.

## Execução

```powershell
python -m src.transformations.abve --html data/bronze/abve/2026-08/abve_2026_08.html
```

Os arquivos são gravados em `data/silver/abve/2026-08/`. A saída preserva origem, período, hash e o local lógico da informação no HTML.
