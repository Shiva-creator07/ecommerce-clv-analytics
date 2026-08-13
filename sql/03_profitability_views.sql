-- ============================================================
-- Order-item level profitability (foundation view)
-- ============================================================

DROP VIEW IF EXISTS vw_order_item_profitability CASCADE;

CREATE VIEW vw_order_item_profitability AS
SELECT
    oi.order_id,
    oi.order_item_id,
    oi.product_id,
    oi.seller_id,
    o.customer_id,
    o.order_purchase_timestamp,
    o.order_status,
    oi.price                                    AS revenue,
    oi.freight_value                            AS freight_cost,
    ROUND(oi.price * pc.cogs_ratio, 2)          AS estimated_cogs,
    ROUND(oi.price - (oi.price * pc.cogs_ratio), 2)
                                                 AS gross_profit,
    ROUND(
        ((oi.price - (oi.price * pc.cogs_ratio)) / NULLIF(oi.price, 0)) * 100,
        2
    )                                            AS gross_margin_pct,
    p.product_category_name,
    t.product_category_name_english
FROM order_items oi
JOIN orders o            ON oi.order_id = o.order_id
JOIN product_costs pc     ON oi.product_id = pc.product_id
JOIN products p           ON oi.product_id = p.product_id
LEFT JOIN product_category_translation t
       ON p.product_category_name = t.product_category_name;


-- ============================================================
-- Order-level profitability (rolls up items to one row per order)
-- ============================================================

DROP VIEW IF EXISTS vw_order_profitability CASCADE;

CREATE VIEW vw_order_profitability AS
SELECT
    order_id,
    customer_id,
    order_purchase_timestamp,
    order_status,
    COUNT(*)                       AS item_count,
    SUM(revenue)                   AS total_revenue,
    SUM(freight_cost)              AS total_freight,
    SUM(estimated_cogs)            AS total_cogs,
    SUM(gross_profit)              AS total_gross_profit,
    ROUND(
        (SUM(gross_profit) / NULLIF(SUM(revenue), 0)) * 100,
        2
    )                               AS gross_margin_pct
FROM vw_order_item_profitability
GROUP BY order_id, customer_id, order_purchase_timestamp, order_status;
