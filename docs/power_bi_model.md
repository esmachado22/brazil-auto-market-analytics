# Modelo semântico Power BI

O modelo abaixo é a especificação do dataset analítico. Todas as tabelas
consumidas pelo BI são saídas Gold validadas; Silver e Bronze não são fontes de
visuais.

## Tabelas

| Tabela | Tipo | Uso |
| --- | --- | --- |
| `dim_tempo` | dimensão | período, mês, trimestre e ano |
| `dim_marca` | dimensão | marca padronizada |
| `dim_modelo` | dimensão | modelo e categoria |
| `fato_emplacamentos` | fato | ranking e volume publicado pela FENABRAVE |
| `fato_eletrificados` | fato | volumes mensais ABVE por tecnologia |
| `fato_precos` | fato | faixa FIPE por modelo/ano e ponto central da faixa |
| `fato_frota` | fato | estoque SENATRAN por município, marca e modelo |

## Relacionamentos

- `dim_tempo[reference_period]` 1:* `fato_emplacamentos[reference_period]`;
- `dim_tempo[reference_period]` 1:* `fato_eletrificados[reference_period]`;
- `dim_tempo[reference_period]` 1:* `fato_precos[reference_period]`;
- `dim_tempo[reference_period]` 1:* `fato_frota[reference_period]`;
- `dim_marca[marca_key]` 1:* `fato_emplacamentos[marca_key]`;
- `dim_modelo[modelo_key]` 1:* `fato_emplacamentos[modelo_key]`.

As tabelas ABVE e FIPE permanecem fatos independentes quando não há chave
confiável de modelo. O relacionamento por texto só deve ser usado nas consultas
de cobertura documentadas em `docs/price_analysis.md`, nunca como dimensão
silenciosamente inferida no modelo.

## Medidas DAX

```DAX
Volume publicado = SUM(fato_emplacamentos[quantity])
Modelos publicados = DISTINCTCOUNT(fato_emplacamentos[modelo_key])
Preço referência central = AVERAGE(fato_precos[price_central_brl])
Volume eletrificados =
    CALCULATE(
        SUM(fato_eletrificados[quantity]),
        fato_eletrificados[included_in_electrified_total] = TRUE()
    )
Estoque frota =
    CALCULATE(
        SUM(fato_frota[quantity]),
        fato_frota[measure_type] = "ESTOQUE"
    )
Participação segmento % =
    DIVIDE(
        [Volume publicado],
        CALCULATE([Volume publicado], ALL(fato_emplacamentos[category_standardized]))
    )
```

Antes de publicar, configurar `dim_tempo`, `dim_marca` e `dim_modelo` como
dimensões e verificar o relatório Gold correspondente em
`data/gold/*_validation.json`.
