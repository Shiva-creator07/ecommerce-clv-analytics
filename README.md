# E-commerce Profitability & CLV Analytics

An end-to-end analytics project on the Olist Brazilian E-Commerce dataset — going beyond a standard sales dashboard into **profitability, RFM customer segmentation, and Customer Lifetime Value (CLV) prediction**, backed by advanced SQL (window functions, CTEs, layered views) and a live interactive dashboard.

**Live demo:** https://ecommerce-clv-analytics-u3tuajbf4u6heykqooep3p.streamlit.app

## Why this project is different

Most portfolio e-commerce projects stop at revenue dashboards. This one asks: *is the business actually profitable, and which customers are worth investing in?*

- **Profitability, not just revenue** — order and category-level gross margin, using a documented synthetic cost layer (see [`docs/cost_assumptions.md`](docs/cost_assumptions.md)), since the source dataset has no cost data.
- **RFM segmentation** built with window functions (`NTILE`, `RANK`) — and a real bug caught and fixed along the way (see below).
- **Customer Lifetime Value** prediction, with guardrails against the kind of naive-extrapolation errors that break CLV models on sparse real-world data.

## Key findings

- **Champions vs. Lost:** the top customer segment (34 customers, "Champions") has an average predicted 2-year CLV of ₹878 — roughly **24x** the "Lost" segment's ₹36. A small group of repeat buyers accounts for a disproportionate share of predicted future value.
- **Revenue leaders aren't always profit leaders:** `computers_accessories` ranks #5 in revenue but drops to **#11 in gross profit** — the largest revenue-vs-profit rank mismatch of any category, consistent with electronics' inherently thinner margins.
- **~97% of customers are one-time buyers.** Olist's retention funnel drops from 92,096 one-time buyers to just 48 customers with 4+ orders. This shapes every downstream metric and is treated as a known dataset characteristic, not a data quality issue.

## Engineering notes: bugs caught and fixed

Two real bugs surfaced during development, both from a common root cause — **naive statistical methods breaking on skewed, sparse real-world data.** Both are documented in full in [`docs/cost_assumptions.md`](docs/cost_assumptions.md).

1. **RFM frequency scoring:** `NTILE(5)` on `frequency` forced the ~97% of customers tied at "1 order" into 5 arbitrary buckets, inflating "frequent buyer" segments. Fixed by scoring frequency with explicit bands instead of quantiles.
2. **CLV frequency extrapolation:** annualizing `orders / days_observed` blew up to absurd values when two orders happened to land close together in time (in one case, 1 second apart) — producing a predicted CLV in the millions from ~₹3,000 of actual profit. Fixed by requiring a minimum order count and observation window before extrapolating, with a sane fallback otherwise.

## Tech stack

- **Database:** PostgreSQL (local: Docker; production: [Neon](https://neon.tech) serverless Postgres)
- **Data processing:** Python, pandas, SQLAlchemy
- **Dashboard:** Streamlit, Plotly
- **Data source:** [Olist Brazilian E-Commerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) (Kaggle)

## Project structure
cat > README.md << 'EOF'
# E-commerce Profitability & CLV Analytics

An end-to-end analytics project on the Olist Brazilian E-Commerce dataset — going beyond a standard sales dashboard into **profitability, RFM customer segmentation, and Customer Lifetime Value (CLV) prediction**, backed by advanced SQL (window functions, CTEs, layered views) and a live interactive dashboard.

**Live demo:** https://ecommerce-clv-analytics-u3tuajbf4u6heykqooep3p.streamlit.app

## Why this project is different

Most portfolio e-commerce projects stop at revenue dashboards. This one asks: *is the business actually profitable, and which customers are worth investing in?*

- **Profitability, not just revenue** — order and category-level gross margin, using a documented synthetic cost layer (see [`docs/cost_assumptions.md`](docs/cost_assumptions.md)), since the source dataset has no cost data.
- **RFM segmentation** built with window functions (`NTILE`, `RANK`) — and a real bug caught and fixed along the way (see below).
- **Customer Lifetime Value** prediction, with guardrails against the kind of naive-extrapolation errors that break CLV models on sparse real-world data.

## Key findings

- **Champions vs. Lost:** the top customer segment (34 customers, "Champions") has an average predicted 2-year CLV of ₹878 — roughly **24x** the "Lost" segment's ₹36. A small group of repeat buyers accounts for a disproportionate share of predicted future value.
- **Revenue leaders aren't always profit leaders:** `computers_accessories` ranks #5 in revenue but drops to **#11 in gross profit** — the largest revenue-vs-profit rank mismatch of any category, consistent with electronics' inherently thinner margins.
- **~97% of customers are one-time buyers.** Olist's retention funnel drops from 92,096 one-time buyers to just 48 customers with 4+ orders. This shapes every downstream metric and is treated as a known dataset characteristic, not a data quality issue.

## Engineering notes: bugs caught and fixed

Two real bugs surfaced during development, both from a common root cause — **naive statistical methods breaking on skewed, sparse real-world data.** Both are documented in full in [`docs/cost_assumptions.md`](docs/cost_assumptions.md).

1. **RFM frequency scoring:** `NTILE(5)` on `frequency` forced the ~97% of customers tied at "1 order" into 5 arbitrary buckets, inflating "frequent buyer" segments. Fixed by scoring frequency with explicit bands instead of quantiles.
2. **CLV frequency extrapolation:** annualizing `orders / days_observed` blew up to absurd values when two orders happened to land close together in time (in one case, 1 second apart) — producing a predicted CLV in the millions from ~₹3,000 of actual profit. Fixed by requiring a minimum order count and observation window before extrapolating, with a sane fallback otherwise.

## Tech stack

- **Database:** PostgreSQL (local: Docker; production: [Neon](https://neon.tech) serverless Postgres)
- **Data processing:** Python, pandas, SQLAlchemy
- **Dashboard:** Streamlit, Plotly
- **Data source:** [Olist Brazilian E-Commerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) (Kaggle)

## Project structur## Running locally

**1. Clone and set up Python environment**

```bash
git clone https://github.com/Shiva-creator07/ecommerce-clv-analytics.git
cd ecommerce-clv-analytics
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**2. Start Postgres**

```bash
docker compose up -d
```

**3. Download the data**

This project uses the [Olist Brazilian E-Commerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) from Kaggle. Raw CSVs are not committed to this repo.

```bash
pip install kaggle
# place your kaggle.json API token in ~/.kaggle/kaggle.json
kaggle datasets download -d olistbr/brazilian-ecommerce -p data/raw --unzip
```

**4. Create a `.env` file**
DB_HOST=localhost
DB_PORT=5433
DB_NAME=ecommerce_clv
DB_USER=clv_user
DB_PASSWORD=clv_password
**5. Build the database**

```bash
for f in sql/*.sql; do
  docker exec -i ecommerce-clv-postgres psql -U clv_user -d ecommerce_clv < "$f"
done
python scripts/load_data.py
python scripts/generate_costs.py
```

**6. Run the dashboard**

```bash
streamlit run dashboard/app.py
```

## Author

Built by [Shivansh Mishra](https://github.com/Shiva-creator07) as a portfolio project demonstrating SQL analytics, data engineering, and full-stack deployment (local Docker → cloud Postgres → live dashboard).
