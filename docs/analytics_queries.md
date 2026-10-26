# Consultas analíticas

As consultas principais estão em `sql/analysis_queries.sql` e cobrem top 10 modelos, top 10 marcas, volume mensal oficial, participação por segmento, crescimento mensal, tecnologias ABVE e evolução dos eletrificados.

As consultas usam `silver.fenabrave_segment_totals` para totais oficiais e `gold.fato_emplacamentos` para rankings publicados. O ranking FENABRAVE carregado é um recorte dos modelos publicados e não deve ser apresentado como o universo completo de vendas por marca/modelo.

Como a FENABRAVE não informou tecnologia no arquivo usado, a comparação completa combustão × híbrido × elétrico depende da integração ABVE e de uma fonte de tecnologia para os demais veículos. A consulta correspondente deixa essa limitação explícita.
