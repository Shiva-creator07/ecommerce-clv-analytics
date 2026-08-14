-- ============================================================
-- Product & category-level profitability
-- ============================================================

DROP VIEW IF EXISTS vw_product_profitability CASCADE;

CREATE VIEW vw_product_profitability AS
SELECT
    product_id,
    product_category_name_english,
    COUNT(*)                              AS units_sold,
    SUM(revenue)                          AS total_revenue,
    SUM(estimated_cogs)                   AS total_cogs,
    SUM(gross_profit)                     AS total_gross_profit,
    ROUND(AVG(gross_margin_pct), 2)       AS avg_gross_margin_pct
FROM vw_order_item_profitability
GROUP BY product_id, product_category_name_english;


DROP VIEW IF EXISTS vw_category_profitability CASCADE;

CREATE VIEW vw_category_profitability AS
SELECT
    COALESCE(product_category_name_english, 'unknown') AS category,
    COUNT(*)                              AS units_sold,
    SUM(revenue)                          AS total_revenue,
    SUM(estimated_cogs)                   AS total_cogs,
    SUM(gross_profit)                     AS total_gross_profit,
    ROUND(AVG(gross_margin_pct), 2)       AS avg_gross_margin_pct,
    -- rank by revenue and by profit separately, to spot mismatches
    RANK() OVER (ORDER BY SUM(revenue) DESC)      AS revenue_rank,
    RANK() OVER (ORDER BY SUM(gross_profit) DESC) AS profit_rank
FROM vw_order_item_profitability
GROUP BY product_category_name_english;
