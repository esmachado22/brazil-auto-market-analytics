-- Brazil Auto Market Analytics — análises de preço de referência FIPE
--
-- A tabela gold.fato_precos contém a faixa FIPE e o ponto central derivado, não
-- preço efetivo de transação. A cobertura depende dos snapshots manuais.

-- [preco_medio_por_tecnologia]
-- Só classifica tecnologia quando houver mapeamento explícito no Gold.
WITH prices AS (
    SELECT brand_standardized, model_standardized,
           AVG(price_central_brl) AS central_reference_price_brl
    FROM gold.fato_precos
    WHERE price_type = 'REFERENCE_RANGE_CENTRAL'
    GROUP BY brand_standardized, model_standardized
), technologies AS (
    SELECT brand_standardized, model_standardized,
           MAX(NULLIF(technology_standardized, 'NAO_INFORMADO')) AS technology_standardized
    FROM gold.fato_emplacamentos
    GROUP BY brand_standardized, model_standardized
)
SELECT t.technology_standardized,
       ROUND(AVG(p.central_reference_price_brl), 2) AS central_reference_price_brl,
       COUNT(*) AS priced_model_count
FROM prices p
JOIN technologies t
  ON p.brand_standardized = t.brand_standardized
 AND p.model_standardized = t.model_standardized
WHERE t.technology_standardized IS NOT NULL
GROUP BY t.technology_standardized
ORDER BY central_reference_price_brl DESC;

-- [preco_por_marca]
SELECT brand_original,
       ROUND(AVG(price_central_brl), 2) AS central_reference_price_brl,
       MIN(price_min_brl) AS min_reference_price_brl,
       MAX(price_max_brl) AS max_reference_price_brl,
       COUNT(*) AS priced_model_count
FROM gold.fato_precos
WHERE price_type = 'REFERENCE_RANGE_CENTRAL'
GROUP BY brand_original
ORDER BY central_reference_price_brl DESC;

-- [preco_por_modelo]
SELECT reference_period, brand_original, model_original, model_year,
       ROUND(price_min_brl, 2) AS reference_price_min_brl,
       ROUND(price_max_brl, 2) AS reference_price_max_brl,
       ROUND(price_central_brl, 2) AS reference_price_central_brl,
       variant_count
FROM gold.fato_precos
WHERE price_type = 'REFERENCE_RANGE_CENTRAL'
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
    SELECT reference_period, brand_standardized, model_standardized,
           price_min_brl, price_max_brl, price_central_brl
    FROM gold.fato_precos
    WHERE price_type = 'REFERENCE_RANGE_CENTRAL'
)
SELECT m.reference_period, m.brand_standardized, m.model_standardized,
       m.ranked_volume,
       ROUND(p.price_min_brl, 2) AS reference_price_min_brl,
       ROUND(p.price_max_brl, 2) AS reference_price_max_brl,
       ROUND(p.price_central_brl, 2) AS reference_price_central_brl,
       ROUND(m.ranked_volume * p.price_central_brl, 2) AS ranked_volume_x_reference_price
FROM market m
LEFT JOIN prices p
  ON m.reference_period = p.reference_period
 AND m.brand_standardized = p.brand_standardized
 AND m.model_standardized = p.model_standardized
ORDER BY m.reference_period, ranked_volume DESC;
