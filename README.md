# E-commerce Profitability & CLV Analytics

An end-to-end analytics project on the Olist Brazilian E-Commerce dataset — going beyond a standard sales dashboard into **profitability, RFM customer segmentation, and Customer Lifetime Value (CLV) prediction**, backed by advanced SQL (window functions, CTEs, layered views) and a live interactive dashboard.

**Live demo:** https://ecommerce-clv-analytics-u3tuajbf4u6heykqooep3p.streamlit.app

## Why this project is different

Most portfolio e-commerce projects stop at revenue dashboards. This one asks: is the business actually profitable, and which customers are worth investing in?

- **Profitability, not just revenue** - order and category-level gross margin, using a documented synthetic cost layer (see docs/cost_assumptions.md), since the source dataset has no cost data.
- **RFM segmentation** built with window functions (NTILE, RANK) - and a real bug caught and fixed along the way (see below).
- **Customer Lifetime Value** prediction, with guardrails against the kind of naive-extrapolation errors that break CLV models on sparse real-world data.

## Key findings

- **Champions vs. Lost:** the top customer segment (34 customers, "Champions") has an average predicted 2-year CLV of Rs 878 - roughly 24x the "Lost" segment's Rs 36.
- **Revenue leaders aren't always profit leaders:** computers_accessories ranks #5 in revenue but drops to #11 in gross profit - the largest revenue-vs-profit rank mismatch of any category.
- **~97% of customers are one-time buyers.** Olist's retention funnel drops from 92,096 one-time buyers to just 48 customers with 4+ orders.

## Engineering notes: bugs caught and fixed

1. **RFM frequency scoring:** NTILE(5) forced the ~97% of one-order customers into 5 arbitrary buckets. Fixed with explicit bands instead of quantiles.
2. **CLV frequency extrapolation:** annualizing orders/days_observed blew up when two orders landed close together in time. Fixed by requiring a minimum order count and observation window before extrapolating.

Full writeups in docs/cost_assumptions.md.

## Tech stack

- Database: PostgreSQL (local Docker; production: Neon serverless Postgres)
- Data processing: Python, pandas, SQLAlchemy
- Dashboard: Streamlit, Plotly
- Data source: Olist Brazilian E-Commerce dataset (Kaggle)

## Project structure
ecommerce-clv-analytics/
+-- dashboard/app.py
+-- data/raw/
+-- docs/cost_assumptions.md
+-- scripts/
+-- sql/
+-- docker-compose.yml
+-- requirements.txt
## Running locally

1. Clone repo, create venv, `pip install -r requirements.txt`
2. `docker compose up -d`
3. Download Olist dataset from Kaggle into `data/raw`
4. Create `.env` with local Postgres credentials
5. Run SQL files in `sql/`, then `python scripts/load_data.py` and `python scripts/generate_costs.py`
6. `streamlit run dashboard/app.py`

## Author

Built by Shivansh Mishra (github.com/Shiva-creator07).
