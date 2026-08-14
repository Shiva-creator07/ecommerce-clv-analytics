-- ============================================================
-- Customer Lifetime Value
-- Historical CLV: actual gross profit generated to date
-- Predictive CLV: avg_order_profit * purchase_frequency_per_year
--                 * estimated_lifespan_years
--
-- Frequency extrapolation guardrail: annualizing "orders / observed
-- days" is only meaningful when there's enough signal to trust it.
-- A customer with 2 orders placed hours apart gives almost no
-- information about their real annual cadence — extrapolating from
-- that (even with a cap) produces inflated predictions. So:
--   - Customers need >= 3 orders AND >= 60 observed days before we
--     attempt real frequency extrapolation
--   - Everyone else (one-time buyers, or repeat buyers with too
--     short/thin a history) falls back to a conservative 1x/year
--     default, same treatment as genuine one-time buyers
--   - A 24/year sanity cap remains as a final backstop
-- ============================================================

DROP VIEW IF EXISTS vw_customer_clv CASCADE;

CREATE VIEW vw_customer_clv AS
WITH customer_orders AS (
    SELECT
        c.customer_unique_id,
        o.order_id,
        o.order_purchase_timestamp,
        op.total_revenue,
        op.total_gross_profit
    FROM orders o
    JOIN customers c              ON o.customer_id = c.customer_id
    JOIN vw_order_profitability op ON o.order_id = op.order_id
    WHERE o.order_status NOT IN ('canceled', 'unavailable')
),
customer_agg AS (
    SELECT
        customer_unique_id,
        COUNT(DISTINCT order_id)                          AS total_orders,
        SUM(total_revenue)                                 AS historical_revenue,
        SUM(total_gross_profit)                            AS historical_profit,
        MIN(order_purchase_timestamp)                      AS first_order_date,
        MAX(order_purchase_timestamp)                       AS last_order_date,
        EXTRACT(EPOCH FROM (MAX(order_purchase_timestamp) - MIN(order_purchase_timestamp))) / 86400.0
                                                              AS customer_lifespan_days_observed
    FROM customer_orders
    GROUP BY customer_unique_id
),
customer_clv AS (
    SELECT
        customer_unique_id,
        total_orders,
        historical_revenue,
        historical_profit,
        first_order_date,
        last_order_date,
        ROUND(historical_profit / total_orders, 2)         AS avg_order_profit,
        ROUND(
            CASE
                -- enough repeat behavior AND enough observed time
                -- to trust an extrapolated annual frequency
                WHEN total_orders >= 3 AND customer_lifespan_days_observed >= 60 THEN
                    LEAST(
                        total_orders / (customer_lifespan_days_observed / 365.0),
                        24.0
                    )
                -- everyone else: not enough signal to extrapolate,
                -- fall back to a conservative default
                ELSE 1.0
            END,
            3
        )                                                    AS purchase_frequency_per_year
    FROM customer_agg
)
SELECT
    customer_unique_id,
    total_orders,
    historical_revenue,
    historical_profit,
    first_order_date,
    last_order_date,
    avg_order_profit,
    purchase_frequency_per_year,
    ROUND(
        avg_order_profit * purchase_frequency_per_year * 2.0,
        2
    )                                                        AS predicted_clv_2yr
FROM customer_clv;
