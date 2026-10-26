# Metodologia

## Fontes

O pipeline usa publicações oficiais da FENABRAVE, ABVE, SENATRAN e FIPE. URLs,
arquivos, períodos e hashes são registrados no Bronze e propagados aos fatos.
Detalhes por fonte estão em `docs/data_sources.md` e na matriz em
`docs/source_matrix.md`.

## Métricas

- **Volume de emplacamentos:** `quantity` publicado no ranking ou total
  FENABRAVE; o ranking de modelos é identificado como recorte publicado.
- **Market share:** volume do segmento dividido pelo total do mesmo período,
  usando o total oficial da Silver.
- **Eletrificados:** componentes BEV, PHEV, HEV e HEV Flex são reconciliados
  com o total ABVE; MHEV fica separado quando a fonte o publica fora do total.
- **Fluxo x estoque:** emplacamentos são fluxo do período; SENATRAN é estoque
  registrado no período. Não existe soma entre os dois.
- **Preço de referência:** valor médio FIPE por modelo/ano, identificado como
  `REFERENCE`; não é preço efetivo de venda.

## Normalização

Nomes são convertidos para chaves estáveis e formas padronizadas nas dimensões.
Tecnologia só é preenchida quando a fonte fornece a classificação ou quando há
regra documentada. Ausência é preservada como `NAO_INFORMADO`.

## Limitações

O escopo depende da cobertura publicada em cada mês. FIPE não fornece API ou
download integral utilizado neste projeto, portanto preço exige snapshot manual
validado. O ranking FENABRAVE não é tratado como universo completo de todos os
modelos vendidos. A análise de tecnologia por modelo requer uma fonte de
mapeamento adicional.
