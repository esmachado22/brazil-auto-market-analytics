# Preço de referência FIPE

A fonte validada é a [Tabela FIPE](https://www.fipe.org.br/pt-br/indices/veiculos), com consulta pública em `veiculos.fipe.org.br`. A FIPE informa que o valor é um preço médio de referência em reais, não o preço efetivo de uma transação. Também informa que não oferece API nem download da base completa ou parcial.

Por essa limitação, a integração implementada é deliberadamente baseada em snapshots manuais de consultas oficiais. O arquivo de exemplo está em `examples/fipe_reference_snapshot.csv.example`; uma linha real deve conter a URL oficial da consulta, código FIPE, marca, modelo, ano-modelo, valor e timestamp da consulta.

Fluxo:

1. Capturar uma consulta individual no site oficial e preencher o CSV com a linha publicada.
2. Executar `src.ingestion.fipe` para gravar Bronze e metadados.
3. Executar `src.transformations.fipe` para criar `data/silver/fipe/<period>/reference_prices.csv` e `data/gold/fato_precos.csv`.

Todos os registros recebem `price_type=REFERENCE`. O valor não deve ser descrito como preço de venda, preço de anúncio ou preço transacionado. A cobertura depende das consultas manuais capturadas; o pipeline não tenta produzir uma falsa base completa.
