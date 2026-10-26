# Dimensão de marca

O módulo `src/transformations/brand_dimension.py` cria `dim_marca.csv` a partir do ranking de modelos FENABRAVE.

Campos principais:

- `marca_key`: chave determinística derivada do nome padronizado;
- `brand_original`: primeiro nome original preservado;
- `brand_originals`: todos os nomes originais observados para a marca;
- `brand_standardized`: nome usado nas análises;
- origem, períodos e arquivos associados.

As únicas abreviações normalizadas nesta etapa são `VW` → `VOLKSWAGEN` e `M.BENZ` → `MERCEDES-BENZ`. Outras marcas permanecem com o nome publicado pela FENABRAVE para evitar inferências indevidas.

## Execução

```powershell
python -m src.transformations.brand_dimension
```

O resultado é gravado em `data/gold/dim_marca.csv`.
