# Arquitetura

O projeto implementa um fluxo de dados público e reproduzível para o mercado
automotivo brasileiro:

```text
fontes oficiais
    ↓
Bronze (arquivo original + metadata)
    ↓
Silver (tipos, normalização e checks)
    ↓
Gold (dimensões, fatos e relatórios de validação)
    ↓
SQL analítico / Power BI / análise executiva estruturada
```

## Camadas

- **Bronze** preserva o arquivo recebido, hash SHA-256, URL, período e data de
  ingestão. O framework compartilhado está em `src/ingestion/framework.py`.
- **Silver** aplica parsing específico da fonte, normaliza nomes e mantém
  proveniência. As transformações ficam em `src/transformations/`.
- **Gold** expõe `dim_tempo`, `dim_marca`, `dim_modelo`,
  `fato_emplacamentos`, `fato_eletrificados`, `fato_precos` e `fato_frota`.
- **Quality** executa validações de estrutura, chaves, reconciliações,
  métricas e fatos de frota. Os relatórios ficam em `data/gold/` quando gerados.

## Fontes e escopo

- FENABRAVE: rankings e totais publicados de emplacamentos;
- ABVE: volumes mensais de eletrificados por tecnologia;
- SENATRAN: estoque de frota por localização, marca e modelo;
- FIPE: snapshots manuais de preço médio de referência.

Cada fato conserva `source_name`, `source_url`, `source_file` e `source_hash`.
Vendas/emplacamentos e estoque de frota são fatos distintos e não são somados.

## Reprodutibilidade

Os dados brutos e arquivos grandes são ignorados pelo Git. Scripts e exemplos
permitem reexecutar ingestão e transformação localmente; no Databricks, os
mesmos contratos podem ser materializados como tabelas Bronze/Silver/Gold e
consultados pelos SQL em `sql/`.
