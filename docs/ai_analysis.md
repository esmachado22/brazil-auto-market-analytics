# Camada de análise executiva

As tasks T32–T34 são implementadas em
`src/analysis/executive_analysis.py`. A primeira versão é determinística e
auditável: recebe métricas já calculadas a partir do Gold e gera JSON
estruturado. Não chama um modelo externo, não consulta a internet e não cria
valores ausentes.

## Entradas permitidas

Cada registro precisa conter `periodo`, `metrica`, `nome`, `valor` e `fonte`.
As métricas permitidas são `volume`, `market_share`, `growth_pct`,
`electrified_volume`, `price_reference` e `fleet_stock`. Todos os registros de
uma execução devem pertencer ao mesmo período `YYYY-MM`.

## Saída

```json
{
  "periodo": "2026-08",
  "resumo": "Foram observadas 2 métricas no período 2026-08.",
  "principais_movimentos": [],
  "dados_observados": [],
  "alertas": []
}
```

Movimentos só são calculados para registros `growth_pct`; o sentido é derivado
do sinal do valor. Alertas lembram as diferenças entre preço FIPE e venda e
entre estoque SENATRAN e emplacamento. Registros inválidos falham antes da
saída.

## Execução

```powershell
python -m src.analysis.executive_analysis `
  --input examples/executive_metrics.json `
  --output data/gold/executive_analysis.json
```
