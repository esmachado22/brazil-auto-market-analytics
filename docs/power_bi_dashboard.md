# Dashboard executivo

Especificação do dashboard para montagem no Power BI. O conjunto de dados
deve ser carregado apenas a partir das tabelas Gold validadas descritas em
`docs/power_bi_model.md`.

## Páginas

1. **Mercado geral** — cartões de volume publicado, modelos publicados e
   evolução mensal; linha de volume por período; ranking dos dez modelos.
2. **Combustão x eletrificados** — série ABVE de volume eletrificado, cartões
   BEV/PHEV/HEV e nota de que a fonte FENABRAVE não classifica todo o ranking
   por tecnologia.
3. **Eletrificados** — barras por tecnologia, participação publicada e evolução
   mensal com filtros de período.
4. **Marcas e modelos** — ranking por marca/modelo, participação de segmento e
   tooltip de preço FIPE quando houver snapshot correspondente.
5. **Geografia** — mapa/tabela de frota SENATRAN por UF e município, com
   filtros de marca, modelo e período; separar visualmente estoque de vendas.

## Regras de publicação

- usar `status = PASS` dos relatórios de validação Gold como pré-requisito;
- exibir período e fonte em cada página;
- mostrar “preço de referência FIPE” e nunca “preço de venda”;
- não misturar `fato_frota` com emplacamentos no mesmo KPI;
- exibir mensagem de cobertura quando não houver preço FIPE para o modelo;
- não inferir tecnologia faltante.

Esta especificação é o artefato reproduzível do dashboard. A publicação em um
workspace Power BI foi definida como fora do escopo deste projeto; o entregável
é o relatório local e sua especificação versionada.

Foi criado localmente um relatório Power BI com as tabelas Gold de
emplacamentos e eletrificados, cinco páginas e visuais iniciais. O arquivo
`Brazil Auto Market Analytics.pbix` fica no diretório do projeto, mas permanece
fora do Git por ser um artefato binário local.
