# Brazil Auto Market Analytics

## 1. Objetivo

Construir um projeto de portfólio de Data Engineering + Analytics para analisar a evolução do mercado automotivo brasileiro, com foco em:

- veículos a combustão;
- veículos híbridos;
- veículos elétricos;
- marcas e modelos;
- emplacamentos;
- participação de mercado;
- evolução mensal;
- características dos veículos;
- análise geográfica;
- preço de referência, quando disponível.

O projeto deve utilizar dados públicos e reproduzíveis e demonstrar boas práticas de engenharia de dados, qualidade, modelagem, documentação e análise.

O objetivo não é criar apenas um dashboard. O foco principal é demonstrar um pipeline completo utilizando Databricks Free Edition.

## 2. Pergunta de negócio

> Como o mercado automotivo brasileiro está evoluindo entre veículos a combustão, híbridos e elétricos?

Perguntas secundárias:

- Quais são os veículos mais emplacados?
- Quais marcas possuem maior participação?
- Como a participação de híbridos e elétricos evolui ao longo do tempo?
- Quais modelos eletrificados apresentam maior crescimento?
- Como as tecnologias se distribuem?
- Quais categorias estão crescendo?
- Como a distribuição geográfica se comporta?
- Qual é a relação entre volume de emplacamentos e preço de referência?
- Quais mudanças relevantes podem ser identificadas?

## 3. Fontes de dados

### 3.1 FENABRAVE

Fonte principal para emplacamentos e rankings.

Dados esperados:

- período;
- marca;
- modelo;
- categoria;
- quantidade;
- ranking, quando disponível.

Preferir fontes oficiais. Preservar o arquivo original sempre que possível.

Registrar:

- URL/origem;
- data de coleta;
- nome do arquivo;
- período;
- hash do arquivo, quando aplicável.

### 3.2 ABVE

Fonte complementar para eletrificados.

Categorias esperadas, conforme disponibilidade:

- BEV;
- PHEV;
- HEV;
- HEV Flex;
- MHEV;
- total de eletrificados;
- participação.

Preservar a classificação original e documentar qualquer padronização.

### 3.3 SENATRAN

Fonte complementar para frota.

Quando disponíveis:

- marca;
- modelo;
- combustível;
- ano de fabricação;
- ano/modelo;
- UF;
- município;
- potência;
- quantidade.

Frota é estoque de veículos registrados. Não tratar frota como venda/emplacamento.

### 3.4 Preço

Preço é uma camada opcional de enriquecimento.

Quando houver fonte pública e permitida:

- preço de referência;
- marca;
- modelo;
- ano/modelo;
- versão;
- combustível.

Usar nomes como `preco_referencia` ou `preco_fipe_referencia`. Não chamar de preço efetivamente vendido.

Não utilizar scraping/API quando os termos de uso não permitirem.

Se não houver fonte adequada, o MVP deve continuar sem preço.

## 4. Arquitetura

```text
                 FONTES PÚBLICAS
                       |
        +--------------+--------------+
        |              |              |
    FENABRAVE         ABVE        SENATRAN
        |              |              |
        +--------------+--------------+
                       |
                       v
                INGESTÃO PYTHON
                       |
                       v
             DATABRICKS FREE
                       |
                    BRONZE
                       |
                       v
                    SILVER
                       |
                       v
                     GOLD
                       |
          +------------+------------+
          |            |            |
          v            v            v
      Databricks    Power BI       IA
        SQL
```

## 5. Tecnologias

Priorizar:

- Databricks Free Edition;
- Python;
- PySpark;
- SQL;
- Delta Lake;
- notebooks Databricks;
- Git/GitHub;
- Power BI;
- Markdown.

Não utilizar AWS/Redshift no MVP, evitando custos desnecessários.

## 6. Camadas

### Bronze

Preservar os dados próximos ao formato original.

Adicionar metadados como:

```text
source_name
source_url
ingestion_timestamp
reference_period
source_file
file_hash
```

Não sobrescrever histórico.

### Silver

Responsável por:

- padronização;
- tipos;
- nulos;
- duplicidades;
- marca/modelo;
- períodos;
- combustível;
- categorias;
- qualidade.

Não alterar silenciosamente os dados de origem.

### Gold

Criar modelo analítico.

Dimensões sugeridas:

```text
dim_tempo
dim_marca
dim_modelo
dim_categoria
dim_tecnologia
dim_localidade
```

Fatos sugeridos:

```text
fato_emplacamentos
fato_eletrificados
fato_frota
fato_precos
```

O modelo pode ser alterado se a estrutura real dos dados indicar uma solução melhor.

## 7. Classificação de tecnologia

Criar classificação padronizada:

```text
COMBUSTAO
HIBRIDO
ELETRICO
OUTRO
NAO_INFORMADO
```

Quando houver granularidade suficiente, preservar também a classificação original:

```text
BEV
PHEV
HEV
HEV_FLEX
MHEV
FLEX
GASOLINA
DIESEL
ELETRICO
HIBRIDO
```

## 8. Métricas

Calcular quando os dados permitirem:

- total de emplacamentos;
- emplacamentos por mês;
- marca;
- modelo;
- categoria;
- tecnologia;
- market share;
- crescimento mensal;
- crescimento acumulado;
- participação dos eletrificados;
- frota por tecnologia;
- frota por combustível;
- frota por UF/município;
- preço médio de referência;
- volume x preço.

Market share:

```text
market_share = vendas_categoria / vendas_total
```

## 9. Qualidade

Criar validações automáticas para:

- período;
- marca;
- modelo;
- quantidade;
- valores negativos;
- preços negativos;
- períodos inválidos;
- duplicidades;
- chaves;
- integridade entre dimensões e fatos.

Falhas devem ser registradas com quantidade de registros afetados. Não excluir silenciosamente.

## 10. Histórico e idempotência

O pipeline deve ser incremental e não duplicar dados ao ser executado novamente para o mesmo período.

Uma chave de controle deve considerar, conforme a fonte:

```text
source
reference_period
file/version
```

ou equivalente.

## 11. Dashboard

Após validação da Gold:

### Visão geral

- emplacamentos;
- top marcas;
- top modelos;
- market share;
- evolução mensal.

### Combustão x eletrificados

- volume;
- participação;
- evolução;
- marcas;
- modelos.

### Eletrificados

- BEV;
- PHEV;
- HEV;
- HEV Flex;
- MHEV.

### Marcas e modelos

- ranking;
- crescimento;
- participação;
- preço de referência, quando disponível.

### Geografia

- UF;
- município;
- tecnologia;
- frota.

## 12. IA

Adicionar somente depois do pipeline funcionar.

A IA deve analisar dados estruturados da camada Gold e responder perguntas como:

- Quais foram as principais mudanças do mês?
- Quais marcas cresceram mais?
- Como os eletrificados evoluíram?
- Quais modelos elétricos cresceram mais?

Distinguir:

- dado observado;
- cálculo;
- interpretação;
- hipótese.

Não inventar valores ausentes.

## 13. Reprodutibilidade

Outra pessoa deve conseguir:

1. clonar o GitHub;
2. entender as fontes;
3. configurar o ambiente;
4. executar ingestão;
5. executar transformações;
6. consultar Gold;
7. reproduzir métricas.

## 14. Estrutura sugerida

```text
brazil-auto-market-analytics/
├── README.md
├── PROJECT.md
├── TASKS.md
├── LICENSE
├── .gitignore
├── docs/
│   ├── architecture.md
│   ├── data_sources.md
│   ├── data_dictionary.md
│   ├── data_quality.md
│   └── methodology.md
├── notebooks/
│   ├── 01_ingestion/
│   ├── 02_bronze/
│   ├── 03_silver/
│   ├── 04_gold/
│   ├── 05_quality/
│   └── 06_analysis/
├── src/
│   ├── ingestion/
│   ├── transformations/
│   ├── quality/
│   └── utils/
├── tests/
├── config/
└── data/
    └── README.md
```

Não versionar grandes arquivos de dados no GitHub.

## 15. Regras para o Codex

1. Não inventar dados.
2. Não inventar URLs.
3. Não assumir estrutura sem verificar.
4. Não criar dados fictícios para mascarar ausência de fonte.
5. Não utilizar APIs pagas sem autorização.
6. Não adicionar AWS sem necessidade.
7. Priorizar Databricks Free.
8. Manter o MVP simples.
9. Explicar mudanças importantes.
10. Criar código modular.
11. Criar testes.
12. Preservar histórico.
13. Implementar idempotência.
14. Registrar origem.
15. Documentar limitações.
16. Separar dado de interpretação.
17. Não excluir inválidos silenciosamente.
18. Nunca colocar credenciais no GitHub.

## 16. Regra de fontes

Antes de implementar um coletor:

1. verificar se a fonte é oficial;
2. verificar se os dados são públicos;
3. verificar formato;
4. verificar periodicidade;
5. verificar termos de utilização;
6. verificar mecanismo de download;
7. preferir arquivos oficiais ou APIs autorizadas;
8. documentar a fonte.

Se não houver automação adequada, usar ingestão manual documentada em vez de scraping agressivo.

## 17. Critério de sucesso do MVP

O MVP está concluído quando for possível:

- obter dados reais da FENABRAVE;
- obter dados reais da ABVE;
- armazenar Bronze;
- transformar Silver;
- criar Gold;
- calcular volume por tecnologia;
- calcular market share;
- comparar combustão, híbridos e elétricos;
- analisar marcas e modelos;
- consultar por SQL;
- reproduzir o processo;
- documentar as fontes;
- executar no Databricks Free.

Depois avançar para SENATRAN, preço, Power BI e IA.

## 18. Objetivo profissional

Demonstrar conhecimentos práticos em:

- Data Engineering;
- Databricks;
- PySpark;
- SQL;
- Lakehouse;
- Delta Lake;
- ETL/ELT;
- Data Quality;
- Data Modeling;
- Analytics;
- Power BI;
- Python;
- IA aplicada a dados.

Priorizar qualidade, clareza e reprodutibilidade em vez de complexidade artificial.
