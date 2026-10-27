# Análise volume x preço

As consultas estão em `sql/price_analysis.sql` e usam somente tabelas Gold.
O preço usado é o ponto central da faixa FIPE (`price_central_brl`), calculado
como a média simples entre o menor e o maior valor das versões capturadas para
o mesmo modelo/ano. Ele deve ser lido como indicador de posicionamento, não
como preço efetivo de venda ou média oficial ponderada.

As quatro consultas entregues são:

- `preco_medio_por_tecnologia`: calcula a média apenas quando existe uma
  classificação de tecnologia explícita no Gold; não infere tecnologia a partir
  do nome do modelo.
- `preco_por_marca`: ponto central, mínimo, máximo e quantidade de modelos precificados.
- `preco_por_modelo`: preço por período, marca, modelo e ano-modelo.
- `volume_x_preco`: cruza o volume do ranking FENABRAVE com o preço FIPE,
  preservando linhas sem preço através de `LEFT JOIN`.

## Limitações

O ranking FENABRAVE disponível é um recorte dos modelos publicados. A FIPE não
oferece API ou download integral da base para este projeto; portanto, a Gold só
recebe snapshots manuais validados, com cobertura parcial. O join volume x preço
é nulo quando não existe snapshot para o mesmo período, marca e modelo.

Execução típica no Databricks SQL:

```sql
-- executar cada bloco identificado por [nome_da_consulta]
```
