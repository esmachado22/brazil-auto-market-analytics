# Dicionário de dados Gold

## Dimensões

| Tabela | Chave | Campos principais |
| --- | --- | --- |
| `dim_tempo` | `date_key` | `reference_period`, `year`, `month`, `quarter` |
| `dim_marca` | `marca_key` | `brand_standardized`, `brand_originals`, `source_names` |
| `dim_modelo` | `modelo_key` | `marca_key`, `model_standardized`, `categories` |

## Fatos

| Tabela | Grain | Medida e campos de contexto |
| --- | --- | --- |
| `fato_emplacamentos` | período, categoria, marca, modelo, rank | `quantity`; FENABRAVE |
| `fato_eletrificados` | período, categoria/tecnologia | `quantity`, `share_pct`; ABVE |
| `fato_precos` | período, código FIPE, modelo, ano-modelo | `price_brl`, `price_type=REFERENCE` |
| `fato_frota` | período, UF, município, marca, modelo, combustível, potência | `quantity`, `measure_type=ESTOQUE` |

## Convenções

- chaves sintéticas têm prefixo (`EMPLACAMENTO_`, `ELETRIFICADO_`, `PRECO_`);
- `reference_period` usa `YYYY-MM`;
- `quantity` é inteiro não negativo;
- `price_brl` está em reais e é preço médio de referência, não transação;
- `technology_standardized` usa a taxonomia documentada em
  `docs/technology_classification.md`;
- valores `NAO_INFORMADO` permanecem explícitos e não são inferidos.

Os campos de proveniência são parte do contrato Gold e devem ser preservados em
qualquer carga no Databricks ou no Power BI.
