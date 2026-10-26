# Fato de emplacamentos

O módulo `src/transformations/fact_emplacamentos.py` cria `fato_emplacamentos.csv` a partir do ranking FENABRAVE Silver.

Campos principais:

- `reference_period`;
- `marca_key` e `modelo_key`;
- `category_standardized`;
- `rank` e `quantity`;
- `technology_standardized`;
- origem, página e hash.

A tecnologia fica `NAO_INFORMADO` quando a FENABRAVE não publica essa informação no ranking. O fato não infere tecnologia pelo nome do modelo.

## Execução

```powershell
python -m src.transformations.brand_dimension --silver-root data/silver/fenabrave
python -m src.transformations.model_dimension --silver-root data/silver/fenabrave
python -m src.transformations.fact_emplacamentos --silver-root data/silver/fenabrave
```

O resultado é gravado em `data/gold/fato_emplacamentos.csv` e combina todos os
rankings mensais disponíveis no Silver.
