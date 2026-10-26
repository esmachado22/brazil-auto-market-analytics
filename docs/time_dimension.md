# Dimensão de tempo

O módulo `src/transformations/time_dimension.py` cria `dim_tempo.csv` com uma linha por mês entre o menor e o maior `reference_period` encontrado nos Silver.

Campos principais:

- `date_key`: primeiro dia do mês;
- `reference_period`: `YYYY-MM`;
- `year` e `month`;
- `quarter_number` e `quarter`;
- `year_quarter`;
- `month_name_pt`.

## Execução

```powershell
python -m src.transformations.time_dimension --silver-root data/silver --output data/gold/dim_tempo.csv
```

Com os dados carregados no MVP, o calendário cobre janeiro a agosto de 2026, inclusive os meses intermediários necessários para análises temporais.
