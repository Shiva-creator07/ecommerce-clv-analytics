-- ============================================================
-- Combined RFM segment × CLV summary
-- The core "business impact" view: what is each customer
-- segment actually worth?
-- ============================================================

DROP VIEW IF EXISTS vw_rfm_clv_summary CASCADE;

CREATE VIEW vw_rfm_clv_summary AS
SELECT
    r.rfm_segment,
    COUNT(*)                                    AS num_customers,
    ROUND(AVG(c.historical_profit), 2)          AS avg_historical_profit,
    ROUND(AVG(c.predicted_clv_2yr), 2)          AS avg_predicted_clv_2yr,
    ROUND(SUM(c.predicted_clv_2yr), 2)          AS total_predicted_clv_2yr
FROM vw_customer_rfm r
JOIN vw_customer_clv c ON r.customer_unique_id = c.customer_unique_id
GROUP BY r.rfm_segment
ORDER BY avg_predicted_clv_2yr DESC;
