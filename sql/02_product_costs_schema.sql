DROP TABLE IF EXISTS product_costs CASCADE;

CREATE TABLE product_costs (
    product_id   VARCHAR(64) PRIMARY KEY REFERENCES products(product_id),
    cogs_ratio   NUMERIC(4,3) NOT NULL CHECK (cogs_ratio > 0 AND cogs_ratio < 1)
);
