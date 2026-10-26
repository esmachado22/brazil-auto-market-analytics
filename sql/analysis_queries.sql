-- Brazil Auto Market Analytics — consultas principais
-- Tabelas esperadas no Databricks:
-- silver.fenabrave_segment_totals
-- gold.fato_emplacamentos
-- gold.fato_eletrificados

-- [top_10_modelos]
SELECT reference_period, category_standardized, rank, brand_standardized, model_standardized, quantity
FROM gold.fato_emplacamentos
WHERE rank <= 10
ORDER BY reference_period, category_standardized, rank;

-- [top_10_marcas]
SELECT reference_period, category_standardized, brand_standardized,
       SUM(quantity) AS ranked_quantity, COUNT(DISTINCT modelo_key) AS model_count
FROM gold.fato_emplacamentos
GROUP BY reference_period, category_standardized, brand_standardized
QUALIFY ROW_NUMBER() OVER (
  PARTITION BY reference_period, category_standardized
  ORDER BY SUM(quantity) DESC, brand_standardized
) <= 10
ORDER BY reference_period, category_standardized, ranked_quantity DESC;

-- [volume_mensal_oficial]
SELECT reference_period, quantity_month AS total_emplacamentos,
       quantity_previous_month, quantity_same_month_previous_year,
       variation_vs_previous_month_pct, variation_vs_same_month_previous_year_pct
FROM silver.fenabrave_segment_totals
WHERE segment_standardized = 'TOTAL'
ORDER BY reference_period;

-- [market_share_segmentos]
SELECT reference_period, segment_standardized, quantity_month,
       ROUND(100.0 * quantity_month / MAX(CASE WHEN segment_standardized = 'TOTAL' THEN quantity_month END)
         OVER (PARTITION BY reference_period), 2) AS market_share_pct
FROM silver.fenabrave_segment_totals
WHERE segment_standardized NOT IN ('TOTAL', 'SUBTOTAL')
ORDER BY reference_period, market_share_pct DESC;

-- [crescimento_mensal_oficial]
SELECT reference_period, segment_standardized, quantity_month,
       variation_vs_previous_month_pct AS growth_vs_previous_month_pct,
       variation_vs_same_month_previous_year_pct AS growth_vs_same_month_previous_year_pct
FROM silver.fenabrave_segment_totals
WHERE segment_standardized IN ('AUTOMOVEIS', 'COMERCIAIS_LEVES', 'TOTAL')
ORDER BY reference_period, segment_standardized;

-- [combustao_hibrido_eletrico]
-- A FENABRAVE não publicou tecnologia no ranking carregado.
SELECT reference_period, technology_standardized, SUM(quantity) AS quantity,
       SUM(CASE WHEN included_in_electrified_total THEN quantity ELSE 0 END) AS included_quantity
FROM gold.fato_eletrificados
WHERE category_original <> 'TOTAL'
GROUP BY reference_period, technology_standardized
ORDER BY reference_period, technology_standardized;

-- [tecnologias_abve]
SELECT reference_period, category_original, technology_standardized, quantity,
       share_pct, included_in_electrified_total
FROM gold.fato_eletrificados
WHERE category_original IN ('BEV', 'PHEV', 'HEV', 'HEV Flex', 'MHEV')
ORDER BY reference_period, category_original;

-- [evolucao_eletrificados]
SELECT reference_period,
       SUM(CASE WHEN included_in_electrified_total THEN quantity ELSE 0 END) AS total_eletrificados,
       SUM(CASE WHEN category_original = 'MHEV' THEN quantity ELSE 0 END) AS total_mhev,
       MAX(CASE WHEN category_original = 'TOTAL' THEN quantity END) AS published_total
FROM gold.fato_eletrificados
GROUP BY reference_period
ORDER BY reference_period;
