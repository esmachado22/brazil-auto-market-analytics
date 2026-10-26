# Classificação de tecnologia

A classificação canônica é aplicada pela função `classify_technology` em `src/transformations/technology.py`.

| Categoria original | Classe canônica | Observação |
|---|---|---|
| `BEV`, `EV`, elétrico | `ELETRICO` | Veículo 100% elétrico |
| `PHEV`, `HEV`, `HEV Flex`, `MHEV` | `HIBRIDO` | Mantém a categoria original em campo separado |
| `Flex`, gasolina, diesel, etanol, GNV | `COMBUSTAO` | Combustão interna |
| vazio ou nulo | `NAO_INFORMADO` | Ausência de informação |
| `TOTAL`, `ELETRIFICADOS` ou valor desconhecido | `OUTRO` | Agregado ou categoria não mapeada |

Para a regra específica da ABVE, somente `BEV + PHEV + HEV + HEV Flex` compõem o total de eletrificados. `MHEV` continua classificado como `HIBRIDO`, mas fica fora desse total.

A categoria original nunca é sobrescrita; a classe canônica é uma coluna adicional para análise.
