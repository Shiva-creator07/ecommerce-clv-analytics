-- ============================================================
-- RFM Segmentation
-- Recency: days since last order (lower = better, scored via NTILE)
-- Frequency: number of distinct orders — scored via explicit bands,
--   NOT NTILE, because ~97% of customers ordered exactly once.
--   NTILE would force that single tied group into 5 arbitrarily
--   different buckets, artificially inflating "frequent buyer" counts.
-- Monetary: total revenue (scored via NTILE)
-- ============================================================

DROP VIEW IF EXISTS vw_customer_rfm CASCADE;

CREATE VIEW vw_customer_rfm AS
WITH customer_orders AS (
    SELECT
        c.customer_unique_id,
        o.order_id,
        o.order_purchase_timestamp,
        op.total_revenue
    FROM orders o
    JOIN customers c              ON o.customer_id = c.customer_id
    JOIN vw_order_profitability op ON o.order_id = op.order_id
    WHERE o.order_status NOT IN ('canceled', 'unavailable')
),
rfm_base AS (
    SELECT
        customer_unique_id,
        MAX(order_purchase_timestamp)                                  AS last_order_date,
        (SELECT MAX(order_purchase_timestamp) FROM customer_orders)
            - MAX(order_purchase_timestamp)                            AS recency_interval,
        COUNT(DISTINCT order_id)                                       AS frequency,
        SUM(total_revenue)                                             AS monetary
    FROM customer_orders
    GROUP BY customer_unique_id
),
rfm_scored AS (
    SELECT
        customer_unique_id,
        last_order_date,
        EXTRACT(DAY FROM recency_interval)::INT AS recency_days,
        frequency,
        monetary,
        NTILE(5) OVER (ORDER BY recency_interval DESC) AS recency_score,
        CASE
            WHEN frequency = 1 THEN 1
            WHEN frequency = 2 THEN 2
            WHEN frequency = 3 THEN 3
            WHEN frequency = 4 THEN 4
            ELSE 5
        END                                              AS frequency_score,
        NTILE(5) OVER (ORDER BY monetary ASC)           AS monetary_score
    FROM rfm_base
)
SELECT
    customer_unique_id,
    last_order_date,
    recency_days,
    frequency,
    monetary,
    recency_score,
    frequency_score,
    monetary_score,
    (recency_score + frequency_score + monetary_score) AS rfm_total_score,
    CASE
        WHEN recency_score >= 4 AND frequency_score >= 4 AND monetary_score >= 4
            THEN 'Champions'
        WHEN recency_score >= 3 AND frequency_score >= 2
            THEN 'Loyal Customers'
        WHEN recency_score >= 4 AND frequency_score = 1
            THEN 'New / Promising'
        WHEN recency_score <= 2 AND frequency_score >= 2
            THEN 'At Risk'
        WHEN recency_score <= 2 AND frequency_score = 1 AND monetary_score <= 2
            THEN 'Lost'
        ELSE 'Needs Attention'
    END AS rfm_segment
FROM rfm_scored;
