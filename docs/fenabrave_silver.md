# Silver FENABRAVE

O módulo `src/transformations/fenabrave.py` transforma o PDF preservado em Bronze em dois arquivos Silver:

- `segment_totals.csv`: resumo mensal por segmento, com quantidades e variações tipadas;
- `model_rankings.csv`: ranking mensal de automóveis e comerciais leves, com marca e modelo separados quando a fonte usa `/`;
- `quality_report.json`: validação de nulos críticos, quantidades negativas e duplicidades.

## Execução

```powershell
python -m src.transformations.fenabrave --pdf data/bronze/fenabrave/2026-01/2026_01_02.pdf
```

Os arquivos são gravados em `data/silver/fenabrave/2026-01/`.

As linhas mantêm `source_name`, `source_url`, `source_file`, `source_hash`, `source_page` e `reference_period` para rastreabilidade. O PDF original não é alterado e a classificação de tecnologia não é inferida nesta etapa.
