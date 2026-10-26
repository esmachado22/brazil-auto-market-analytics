-- Brazil Auto Market Analytics — análises de preço de referência FIPE
--
-- A tabela gold.fato_precos contém preço médio de referência FIPE, não preço
-- efetivo de transação. A cobertura depende dos snapshots manuais capturados.

-- [preco_medio_por_tecnologia]
-- Só classifica tecnologia quando houver mapeamento explícito no Gold.
WITH prices AS (
    SELECT brand_original, model_original, AVG(price_brl) AS avg_reference_price_brl
    FROM gold.fato_precos
    WHERE price_type = 'REFERENCE'
    GROUP BY brand_original, model_original
), technologies AS (
    SELECT brand_standardized, model_standardized,
           MAX(NULLIF(technology_standardized, 'NAO_INFORMADO')) AS technology_standardized
    FROM gold.fato_emplacamentos
    GROUP BY brand_standardized, model_standardized
)
SELECT t.technology_standardized,
       ROUND(AVG(p.avg_reference_price_brl), 2) AS avg_reference_price_brl,
       COUNT(*) AS priced_model_count
FROM prices p
JOIN technologies t
  ON UPPER(TRIM(p.brand_original)) = t.brand_standardized
 AND UPPER(TRIM(p.model_original)) = t.model_standardized
WHERE t.technology_standardized IS NOT NULL
GROUP BY t.technology_standardized
ORDER BY avg_reference_price_brl DESC;

-- [preco_por_marca]
SELECT brand_original,
       ROUND(AVG(price_brl), 2) AS avg_reference_price_brl,
       MIN(price_brl) AS min_reference_price_brl,
       MAX(price_brl) AS max_reference_price_brl,
       COUNT(*) AS priced_model_count
FROM gold.fato_precos
WHERE price_type = 'REFERENCE'
GROUP BY brand_original
ORDER BY avg_reference_price_brl DESC;

-- [preco_por_modelo]
SELECT reference_period, brand_original, model_original, model_year,
       ROUND(price_brl, 2) AS reference_price_brl
FROM gold.fato_precos
WHERE price_type = 'REFERENCE'
ORDER BY reference_period, brand_original, model_original, model_year;

-- [volume_x_preco]
-- Agrega os rankings publicados por período/modelo antes do join para não
-- multiplicar volume quando o mesmo modelo aparece em mais de uma categoria.
WITH market AS (
    SELECT reference_period, brand_standardized, model_standardized,
           SUM(quantity) AS ranked_volume
    FROM gold.fato_emplacamentos
    GROUP BY reference_period, brand_standardized, model_standardized
), prices AS (
    SELECT reference_period, brand_original, model_original,
           AVG(price_brl) AS avg_reference_price_brl
    FROM gold.fato_precos
    WHERE price_type = 'REFERENCE'
    GROUP BY reference_period, brand_original, model_original
)
SELECT m.reference_period, m.brand_standardized, m.model_standardized,
       m.ranked_volume, ROUND(p.avg_reference_price_brl, 2) AS avg_reference_price_brl,
       ROUND(m.ranked_volume * p.avg_reference_price_brl, 2) AS ranked_volume_x_reference_price
FROM market m
LEFT JOIN prices p
  ON m.reference_period = p.reference_period
 AND m.brand_standardized = UPPER(TRIM(p.brand_original))
 AND m.model_standardized = UPPER(TRIM(p.model_original))
ORDER BY m.reference_period, ranked_volume DESC;
