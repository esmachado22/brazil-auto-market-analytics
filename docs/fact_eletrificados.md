# Fato de eletrificados

O módulo `src/transformations/fact_eletrificados.py` cria `fato_eletrificados.csv` a partir do Silver ABVE.

O fato preserva categorias originais e inclui uma coluna explícita `included_in_electrified_total`. Assim, `BEV`, `PHEV`, `HEV` e `HEV Flex` podem compor o total ABVE, enquanto `MHEV`, `MHEV 12V` e `MHEV 48V` permanecem disponíveis, mas fora desse total.

## Execução

```powershell
python -m src.transformations.fact_eletrificados
```

O resultado é gravado em `data/gold/fato_eletrificados.csv`.
