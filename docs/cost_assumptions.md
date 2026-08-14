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

---

# RFM Segmentation — Methodology Note

## Frequency scoring: why NTILE was replaced with explicit bands

Olist is dominated by one-time buyers: ~97% of customers (92,102 of ~94,990)
placed exactly one order. Using `NTILE(5)` to score frequency — as is
standard in most RFM tutorials — forces that single tied group to be split
arbitrarily across all 5 score buckets, since NTILE must fill each bucket
evenly regardless of ties. This artificially inflated "frequent buyer"
segments (Champions: 14,764, Loyal Customers: 19,871) despite most of those
customers having ordered only once.

**Fix:** frequency is instead scored using explicit, business-meaningful
bands (1 order = score 1, 2 orders = score 2, ... 5+ orders = score 5).
Recency and Monetary remain NTILE-scored since they are continuous values
without this tie-clustering problem.

**Result after fix:** Champions dropped to 34 customers (avg spend ₹712,
~3x the next segment) — a small, high-value group consistent with the
dataset's known low repeat-purchase rate, rather than an artifact of
tie-breaking.

---

# CLV Prediction — Methodology Note

## Frequency extrapolation guardrails

An early version of predicted CLV annualized purchase frequency as
`total_orders / (days_between_first_and_last_order / 365)`. This broke
badly for customers whose 2 orders happened to be placed close together in
time (in one case, 1 second apart): the tiny denominator inflated annualized
frequency into the hundreds, producing a predicted 2-year CLV over ₹2.1
million from a customer with ~₹2,930 in actual historical profit.

A simple frequency cap (24/year) reduced the worst outliers but didn't fix
the root problem: with only 2 data points close together in time, there
isn't enough signal to trust any extrapolated annual rate at all.

**Fix:** frequency extrapolation is now only attempted when a customer has
**3+ orders AND at least 60 observed days** between first and last order.
Customers who don't meet this bar (including all one-time buyers) fall back
to a conservative 1 purchase/year default. The 24/year cap remains as a
final backstop for edge cases.

This is a good example of why sparse, real-world transaction data needs
guardrails before naive extrapolation formulas — a lesson that also came up
in the RFM frequency scoring (see above).
