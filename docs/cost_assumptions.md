# Synthetic Cost Data — Methodology & Assumptions

## Why this exists

The Olist Brazilian E-Commerce dataset includes sale price and freight value
per order item, but does not include product cost (COGS). Without cost data,
"profitability" analysis is not possible — only revenue analysis is.

Rather than fabricate cost as a single flat percentage (unrealistic) or skip
profitability entirely (weaker project), this project generates a synthetic,
clearly-documented cost layer: each product is assigned a COGS ratio
(cost as a fraction of sale price) drawn from a realistic range for its
product category, with per-product variation to reflect that margins differ
even within the same category.

This is a **documented assumption**, not real financial data. Every query and
chart built on top of it should be understood as illustrative of the
*methodology* (profitability analysis, RFM, CLV), not as a factual claim
about Olist sellers' actual margins.

## Category to COGS ratio ranges

COGS ratio = cost / sale price. A ratio of 0.70 means the product costs the
seller 70% of what it sells for (30% gross margin).

| Category group                          | COGS ratio range | Rationale |
|------------------------------------------|-------------------|-----------|
| Electronics / computers / telephony      | 0.70 - 0.80       | Commodity hardware, thin margins, price competition |
| Fashion / beauty / accessories           | 0.35 - 0.50       | Brand & style premium, higher markup |
| Home, furniture & decor                  | 0.45 - 0.60       | Moderate margin, higher logistics/bulk cost |
| Books, media, stationery                 | 0.55 - 0.65       | Low but stable margin, price-sensitive category |
| Toys, games, baby & sports                | 0.40 - 0.55       | Moderate-to-high markup, seasonal demand |
| Everything else (default)                 | 0.50 - 0.65       | Reasonable general-retail middle ground |

Each product draws a ratio uniformly at random from its category's range,
seeded for reproducibility (numpy seed = 42).

## Where this lives

Costs are stored as a ratio per product (product_costs.cogs_ratio), computed
at query time as:

estimated_cost = order_items.price * product_costs.cogs_ratio
gross_profit   = order_items.price - estimated_cost

## Limitations

- Real COGS varies by supplier, bulk discounts, currency fluctuation, and
  seller-specific sourcing, none of which this dataset captures.
- Category-level ranges are informed estimates, not sourced from Olist or
  Brazilian market data.
- Freight cost is tracked separately and treated as a distinct cost line.
