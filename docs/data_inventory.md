# Inventário dos dados locais

Os arquivos físicos ficam em `data/` dentro do projeto:

```text
D:\Brazil Auto Market Analytics\data
```

A pasta `data/` é ignorada pelo Git porque contém PDFs, CSVs e arquivos muito
grandes. Este inventário é versionado para registrar o que foi materializado.

## FENABRAVE — emplacamentos

Arquivos principais:

- Silver mensal: `data/silver/fenabrave/<period>/segment_totals.csv`;
- ranking Silver: `data/silver/fenabrave/<period>/model_rankings.csv`;
- fato Gold: `data/gold/fato_emplacamentos.csv`;
- validação: `data/gold/metric_validation_report.json`.

Períodos disponíveis: janeiro a setembro de 2026. O ranking Gold possui 900
linhas, 100 por mês. Os totais oficiais publicados por mês são:

| Período | Total oficial publicado |
|---|---:|
| 2026-01 | 366.713 |
| 2026-02 | 374.931 |
| 2026-03 | 513.099 |
| 2026-04 | 479.662 |
| 2026-05 | 492.426 |
| 2026-06 | 488.420 |
| 2026-07 | 504.574 |
| 2026-08 | 503.768 |
| 2026-09 | 509.686 |

O ranking é um recorte publicado pela FENABRAVE; a soma dos 100 modelos não
representa todo o total oficial do mês.

## ABVE — eletrificados

- Silver: `data/silver/abve/2026-08/`;
- fato Gold: `data/gold/fato_eletrificados.csv`;
- período atualmente materializado: agosto de 2026;
- total de eletrificados validado: 57.386, sem incluir MHEV.

## SENATRAN — frota

- Silver: `data/silver/senatran/2026-09/`;
- fato Gold: `data/gold/fato_frota.csv.gz`;
- período: setembro de 2026;
- linhas: 22.849.046;
- medida: `ESTOQUE`, não vendas mensais.

## FIPE — preço de referência

Não existe `data/gold/fato_precos.csv` materializado. O projeto possui o
adaptador e o fluxo para snapshots manuais, mas não inventa preços nem baixa
uma base completa que a FIPE não disponibiliza publicamente.
