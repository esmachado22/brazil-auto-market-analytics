# Silver FENABRAVE

O módulo `src/transformations/fenabrave.py` transforma o PDF preservado em Bronze em dois arquivos Silver:

- `segment_totals.csv`: resumo mensal por segmento, com quantidades e variações tipadas;
- `model_rankings.csv`: ranking mensal de automóveis e comerciais leves, com marca e modelo separados quando a fonte usa `/`;
- `quality_report.json`: validação de nulos críticos, quantidades negativas e duplicidades.

## Execução

```powershell
foreach ($period in '2026-01','2026-02','2026-03','2026-04','2026-05','2026-06','2026-07','2026-08','2026-09') {
  $pdf = Get-ChildItem "data/bronze/fenabrave/$period/*.pdf" | Select-Object -First 1
  python -m src.transformations.fenabrave --pdf $pdf.FullName
}
```

Os arquivos são gravados em `data/silver/fenabrave/<period>/`.
Os relatórios de fevereiro a setembro publicam os componentes de segmento sem
uma linha explícita de total; o pipeline cria uma linha `TOTAL` derivada da
soma não sobreposta de `A+B`, `C+D`, `Motos`, `Impl. Rod.` e `Outros`.

As linhas mantêm `source_name`, `source_url`, `source_file`, `source_hash`, `source_page` e `reference_period` para rastreabilidade. O PDF original não é alterado e a classificação de tecnologia não é inferida nesta etapa.
