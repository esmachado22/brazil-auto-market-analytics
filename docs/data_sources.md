# Fontes de dados

## FENABRAVE

### Identificação

- **Fonte:** Federação Nacional da Distribuição de Veículos Automotores (FENABRAVE).
- **Papel no projeto:** fonte principal para emplacamentos de veículos novos, rankings e participação de mercado.
- **Status da validação:** fonte oficial validada em 26/10/2026.

### URLs oficiais

| Recurso | URL | Uso |
|---|---|---|
| Índices e números / Emplacamentos | <https://www.fenabrave.org.br/Portal/conteudo/emplacamentos> | Índice público dos relatórios mensais |
| Relatório mensal de exemplo | <https://www.fenabrave.org.br/portal/files/2026_01_02.pdf> | PDF oficial de janeiro de 2026 |
| Imprensa | <https://www.fenabrave.org.br/portalv2/home/imprensa> | Comunicados e números consolidados |
| Dados de Mercado Personalizados (DMP) | <https://www.fenabrave.org.br/Dados/index2.html> | Consulta detalhada por período, região e município |

### Cobertura observada

Na consulta realizada em 26/10/2026, a página pública listava relatórios mensais de janeiro a setembro de 2026 e de janeiro a dezembro de 2025. A página também oferece um seletor para consultar outros anos, mas a cobertura efetiva deve ser verificada por ano durante a ingestão.

O DMP informa possibilidade de consulta de dados de veículos novos por período, marca e segmento, com histórico desde 2003. O acesso a modelos mais vendidos, dados regionais e dados municipais passou a exigir cadastro na área de imprensa.

### Formato e conteúdo

O índice público é HTML e os relatórios mensais são PDFs oficiais. O relatório de janeiro de 2026 analisado possui 52 páginas e apresenta, entre outros itens:

- período de referência;
- emplacamentos por segmento, incluindo automóveis, comerciais leves, caminhões, ônibus, motocicletas e implementos rodoviários;
- volume do mês, mês anterior, acumulado e comparações com o ano anterior;
- participação de mercado por marca;
- distribuição regional;
- ranking de modelos e respectivas quantidades;
- categorias separadas, como automóveis e comerciais leves.

Não foi identificado um arquivo público estruturado em CSV ou XLS no índice de emplacamentos consultado. Para o MVP, a ingestão deverá preservar o PDF original e aplicar extração documentada, com validação dos totais publicados.

### Limitações

- PDF é um formato orientado à apresentação, não uma tabela analítica; a extração pode exigir tratamento de layout, separadores de milhar e casas decimais.
- Os rankings publicados são recortes por categoria e podem não representar o universo completo de modelos.
- Dados regionais e municipais detalhados dependem de cadastro/acesso ao DMP.
- A disponibilidade histórica e o formato podem variar por ano; não assumir que todos os anos possuem os mesmos relatórios.
- O relatório usa expressões como “venda” em alguns títulos, mas a camada do projeto deve nomear o fato como `fato_emplacamentos`, mantendo a definição da fonte.
- A classificação de tecnologia, combustível e tipo de eletrificação não está garantida nos relatórios mensais da FENABRAVE; essa camada será complementada e validada com a ABVE e outras fontes.

### Estratégia definida para o MVP

1. Usar os PDFs mensais oficiais disponíveis no índice público.
2. Registrar URL, data de coleta, nome do arquivo, período e hash.
3. Preservar o PDF original na camada Bronze.
4. Extrair primeiro os totais por segmento e os rankings necessários para a análise.
5. Comparar os totais extraídos com o resumo do próprio relatório.
6. Documentar qualquer falha de extração ou ausência de período; não preencher lacunas com dados inventados.

## ABVE

### Identificação

- **Fonte:** Associação Brasileira do Veículo Elétrico (ABVE), por meio do ABVE Data.
- **Papel no projeto:** fonte complementar para emplacamentos de veículos leves eletrificados e suas tecnologias.
- **Status da validação:** fonte oficial validada em 26/10/2026.

### URLs oficiais

| Recurso | URL | Uso |
|---|---|---|
| ABVE Data — visão geral | <https://abve.org.br/bi-geral/> | Dashboard principal do mercado de eletrificados |
| ABVE Data — Eletrificados+MHEV | <https://abve.org.br/abve-data/eletrificadosmhev/> | Evolução por tecnologia e comparação com MHEV |
| Arquivo de notícias ABVE Data | <https://abve.org.br/category/abvedata/> | Comunicados mensais e evidências publicadas |

### Cobertura e categorias

A série histórica publicada pela ABVE Data acompanha os veículos leves eletrificados desde janeiro de 2012. A classificação vigente separa:

- **BEV:** veículo 100% elétrico;
- **PHEV:** híbrido com recarga externa;
- **HEV:** híbrido sem recarga externa, com tração elétrica;
- **HEV Flex:** híbrido flex sem recarga externa, com tração elétrica;
- **MHEV:** micro-híbrido, acompanhado separadamente.

Desde janeiro de 2025, a ABVE não inclui MHEV no total de veículos eletrificados, pois a tecnologia não possui tração elétrica autônoma. O total de eletrificados usado no projeto deve seguir a definição da ABVE: `BEV + PHEV + HEV + HEV_FLEX`. MHEV deve permanecer disponível como categoria original, mas fora desse total.

Na consulta realizada em 26/10/2026, a ABVE publicou dados mensais até setembro de 2026, incluindo volumes, participação no mercado de veículos leves, comparações mensais e anuais e recortes geográficos em alguns comunicados.

### Formato e conteúdo

O ABVE Data é disponibilizado principalmente como dashboard web interativo e como comunicados HTML mensais. Os comunicados apresentam tabelas ou listas com:

- período de referência;
- total mensal de eletrificados leves;
- BEV, PHEV, HEV e HEV Flex;
- MHEV, incluindo 12V e 48V quando informado;
- participação de cada tecnologia;
- participação dos eletrificados no mercado de veículos leves;
- comparações com mês anterior e mesmo mês do ano anterior;
- alguns recortes por estado, município e região.

Não foi identificado um arquivo público estruturado em CSV ou XLS na página do ABVE Data consultada. A ingestão deve preservar a página ou evidência original, registrar o período e documentar a extração feita do dashboard ou do comunicado.

### Limitações

- O dashboard pode depender de elementos interativos que não aparecem no HTML estático.
- Os comunicados mensais podem apresentar apenas recortes e não necessariamente a série completa por marca e modelo.
- A ABVE Data e a FENABRAVE podem usar universos diferentes; a comparação deve respeitar a definição de veículos leves e o período de cada fonte.
- A ABVE publica números de mercado e classificação tecnológica, mas a disponibilidade de marca/modelo detalhados deve ser verificada antes de modelar essa dimensão.
- Não misturar o total `eletrificados` com `eletrificados + MHEV`.

### Estratégia definida para o MVP

1. Usar os comunicados e o ABVE Data como fonte oficial complementar.
2. Preservar a classificação original e criar a classificação padronizada do projeto.
3. Armazenar BEV, PHEV, HEV, HEV Flex e MHEV em registros separados quando houver granularidade.
4. Calcular o total de eletrificados sem MHEV, seguindo o critério vigente da ABVE.
5. Validar os totais mensais e o market share contra os valores publicados pela ABVE.

## SENATRAN

### Identificação

- **Fonte:** Secretaria Nacional de Trânsito (SENATRAN), base RENAVAM.
- **Papel no projeto:** fonte complementar para frota registrada, tratada como estoque e não como venda ou emplacamento.
- **Status da validação:** fonte oficial validada em 26/10/2026.

### URLs oficiais

| Recurso | URL | Uso |
|---|---|---|
| Estatísticas de frota | <https://www.gov.br/transportes/pt-br/assuntos/transito/conteudo-Senatran/estatisticas-frota-de-veiculos-senatran> | Navegação por ano de referência |
| Frota de Veículos — 2026 | <https://www.gov.br/transportes/pt-br/assuntos/transito/conteudo-Senatran/frota-de-veiculos-2026> | Arquivos mensais oficiais |
| Dataset RENAVAM | <https://dados.transportes.gov.br/dataset/registro-nacional-de-veiculos-automotores-renavam> | Catálogo e recursos ZIP |

### Cobertura, campos e formatos

A página de estatísticas disponibiliza anos de referência desde 2000 e anteriores. A página de 2026 consultada listava arquivos mensais de janeiro a setembro de 2026. Os arquivos oficiais são planilhas Excel (`.xlsx`) separadas por assunto:

- frota por UF e tipo de veículo;
- frota por município e tipo de veículo;
- UF, município, ano de fabricação e modelo;
- UF, município e CEP;
- UF, município e combustível;
- UF, município e cor;
- UF, município e potência;
- UF, município e tipo de restrição;
- UF, município, marca e modelo;
- UF, município, tipo, espécie e eixos.

Tamanhos observados por cabeçalho HTTP nos arquivos de setembro de 2026:

| Arquivo | Tamanho observado |
|---|---:|
| Frota por UF e tipo | 30 KB |
| Frota por município e tipo | 720 KB |
| Ano de fabricação e modelo | 16,7 MB |
| Combustível | 1,3 MB |
| Potência | 23,1 MB |
| Tipo, espécie e eixos | 7,6 MB |

O catálogo RENAVAM também apresenta recursos ZIP mensais, incluindo arquivos de UF, município, marca, modelo e ano. O portal informa formato CSV/TXT/ZIP para o conjunto, enquanto a página mensal da SENATRAN disponibiliza os recortes em Excel.

### Limitações

- SENATRAN representa estoque de veículos registrados; não deve ser usado diretamente como fluxo de vendas ou emplacamentos.
- As dimensões são distribuídas em arquivos diferentes. Não combinar arquivos de combustível, marca/modelo e potência sem validar a chave e o nível de agregação.
- Os arquivos detalhados podem ser grandes e não devem ser versionados no Git.
- A disponibilidade mensal e os nomes dos arquivos podem mudar; o coletor deverá consultar a página oficial e registrar a versão baixada.
- O catálogo de dados apresenta periodicidade anual em seus metadados, embora mantenha recursos mensais; a periodicidade deve ser verificada pelos arquivos efetivamente publicados.

### Decisão para o MVP

SENATRAN fica fora da primeira ingestão do MVP principal. A fonte está validada para a Fase 6, depois de FENABRAVE, ABVE, Bronze, Silver, Gold e métricas principais funcionarem.

## Preço de referência

### Fonte avaliada: FIPE

- **Fonte:** Fundação Instituto de Pesquisas Econômicas (FIPE).
- **URL oficial:** <https://www.fipe.org.br/pt-br/indices/veiculos>.
- **Definição:** preço médio de referência de veículos no mercado nacional, expresso em reais no mês/ano de referência.

A FIPE informa que a consulta oficial é feita modelo a modelo, que não disponibiliza download da base completa ou parcial e que não oferece serviço de API. Também ressalta que o valor é apenas um parâmetro de negociação/avaliação e não representa necessariamente o preço efetivamente praticado.

### Decisão

Preço de referência não entra no MVP. A integração fica para a Fase 7 e somente será feita se houver uma forma autorizada e reproduzível de obter os dados. O projeto continuará usando nomes como `preco_referencia` ou `preco_fipe_referencia`, nunca “preço efetivamente vendido”.

Consulte a [matriz de fontes](source_matrix.md) para o resumo comparativo das decisões.

