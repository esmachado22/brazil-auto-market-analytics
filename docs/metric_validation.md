# Validação de métricas

O módulo `src/quality/metric_validation.py` compara os valores publicados nas camadas Silver com os fatos Gold e grava o relatório em `data/gold/metric_validation_report.json`.

## Resultado do MVP

- FENABRAVE janeiro a setembro de 2026: os totais oficiais publicados são
  validados por período. O fato Gold soma apenas os modelos do ranking de cada
  mês; portanto, cada soma é tratada como subconjunto e a cobertura é reportada
  no JSON, sem expectativa de igualdade com o total oficial.
- ABVE agosto de 2026: BEV, PHEV, HEV e HEV Flex no Gold reproduzem as categorias Silver e somam **57.386**, igual ao total publicado.
- ABVE MHEV: **6.669 = 4.017 + 2.652**. Esse grupo é mantido separado porque não está incluído no total de eletrificados usado pela fonte.

## Execução

```powershell
$py = 'C:\Users\Desktop\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -m src.quality.metric_validation --root data --output data/gold/metric_validation_report.json
```

As fontes e limitações ficam registradas no próprio relatório para manter a validação auditável.
