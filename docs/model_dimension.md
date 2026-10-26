# Dimensão de modelo

O módulo `src/transformations/model_dimension.py` cria `dim_modelo.csv` a partir do ranking Silver da FENABRAVE.

Cada modelo recebe uma `modelo_key` determinística e uma `marca_key`, mantendo o relacionamento modelo → marca. O texto original é preservado em `model_originals`; `model_standardized` é usado para agrupamento analítico.

## Execução

```powershell
python -m src.transformations.model_dimension
```

O resultado é gravado em `data/gold/dim_modelo.csv`. A dimensão usa apenas os modelos realmente publicados no ranking carregado; não cria modelos ausentes.
