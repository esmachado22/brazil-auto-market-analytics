# Brazil Auto Market Analytics

Pipeline reproduzível de Data Engineering e Analytics para o mercado automotivo
brasileiro, com foco em emplacamentos, eletrificados, frota e preço de
referência.

## O que está pronto

- Bronze/Silver/Gold para FENABRAVE (janeiro a setembro de 2026), ABVE e SENATRAN;
- dimensões de tempo, marca e modelo;
- fatos de emplacamentos, eletrificados, frota e preço FIPE de referência;
- validações de dados, métricas, chaves, reconciliações e proveniência;
- consultas SQL de mercado e volume x preço;
- modelo semântico e especificação de dashboard Power BI;
- análise executiva estruturada, determinística e sem invenção de dados.

O inventário dos dados locais, seus períodos e caminhos está em
`docs/data_inventory.md`.

## Estrutura

```text
src/ingestion/          ingestão Bronze e proveniência
src/transformations/    Silver/Gold por fonte
src/quality/             validações e relatórios
src/analysis/            saída executiva estruturada
sql/                    consultas analíticas
docs/                   arquitetura, método, qualidade e BI
examples/               entradas reproduzíveis
data/                   dados locais; arquivos grandes não são versionados
```

## Execução local

Use o Python do ambiente configurado e execute:

```powershell
python -m unittest discover -s tests -v
python -m src.analysis.executive_analysis `
  --input examples/executive_metrics.json `
  --output data/gold/executive_analysis.json
```

As consultas em `sql/analysis_queries.sql` e `sql/price_analysis.sql` foram
escritas para tabelas Gold/Silver com os nomes documentados. O guia de
Databricks está em `docs/databricks_setup.md`.

## Fontes e limitações

As fontes são FENABRAVE, ABVE, SENATRAN e FIPE; a matriz e URLs estão em
`docs/data_sources.md`. O ranking FENABRAVE é um recorte publicado. Frota é
estoque, não vendas. A FIPE fornece referência média, não preço de transação,
e exige snapshots manuais validados por não haver API ou base integral usada
por este projeto. Tecnologia não é inferida quando a fonte não a informa.

O dashboard está especificado em `docs/power_bi_dashboard.md` e foi entregue
também como relatório local `Brazil Auto Market Analytics.pbix`. A publicação
em workspace Power BI está fora do escopo deste projeto.
