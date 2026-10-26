# Modelo analítico Gold

O MVP Gold é composto por:

- `dim_tempo.csv`;
- `dim_marca.csv`;
- `dim_modelo.csv`;
- `fato_emplacamentos.csv`;
- `fato_eletrificados.csv`.

O modelo mantém as relações `modelo → marca`, `fato_emplacamentos → modelo/marca` e `fatos → dim_tempo`. A validação não trata o ranking FENABRAVE como o total do mercado: o ranking é uma amostra ordenada publicada pela fonte, enquanto o total mensal vem do resumo de segmentos.

## Validação

```powershell
python -m src.quality.gold_model --root data --output data/gold/model_validation_report.json
```

O relatório valida chaves únicas, relacionamentos, cobertura temporal, reconciliação ABVE (`BEV + PHEV + HEV + HEV Flex = TOTAL`) e presença do total FENABRAVE.
