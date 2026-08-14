import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="E-commerce Profitability & CLV Analytics",
    page_icon="📊",
    layout="wide",
)

@st.cache_resource
def get_engine():
    return create_engine(
        f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )

@st.cache_data(ttl=600)
def run_query(query: str) -> pd.DataFrame:
    engine = get_engine()
    return pd.read_sql(query, engine)


st.title("📊 E-commerce Profitability & CLV Analytics")
st.caption("Olist Brazilian E-Commerce dataset — profitability, RFM segmentation, and customer lifetime value")

# Sanity check: confirm DB connection works
try:
    test_df = run_query("SELECT COUNT(*) AS total_orders FROM orders;")
    st.success(f"Connected to database. Total orders: {test_df['total_orders'].iloc[0]:,}")
except Exception as e:
    st.error(f"Database connection failed: {e}")

st.divider()

# ============================================================
# KPI Row
# ============================================================
kpi_query = """
SELECT
    SUM(total_revenue)      AS total_revenue,
    SUM(total_gross_profit) AS total_profit,
    ROUND(
        (SUM(total_gross_profit) / NULLIF(SUM(total_revenue), 0)) * 100, 2
    )                        AS overall_margin_pct,
    COUNT(DISTINCT customer_id) AS total_customers
FROM vw_order_profitability;
"""
kpi_df = run_query(kpi_query)
kpi = kpi_df.iloc[0]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"₹{kpi['total_revenue']:,.0f}")
col2.metric("Total Gross Profit", f"₹{kpi['total_profit']:,.0f}")
col3.metric("Overall Margin", f"{kpi['overall_margin_pct']:.1f}%")
col4.metric("Total Customers", f"{int(kpi['total_customers']):,}")

st.divider()

# ============================================================
# Revenue & Profit Trend
# ============================================================
st.subheader("Revenue & Profit Trend")

trend_query = """
SELECT
    DATE_TRUNC('month', order_purchase_timestamp)::DATE AS month,
    SUM(total_revenue)      AS revenue,
    SUM(total_gross_profit) AS gross_profit
FROM vw_order_profitability
WHERE order_status NOT IN ('canceled', 'unavailable')
GROUP BY month
ORDER BY month;
"""
trend_df = run_query(trend_query)

import plotly.graph_objects as go

fig_trend = go.Figure()
fig_trend.add_trace(go.Scatter(
    x=trend_df["month"], y=trend_df["revenue"],
    mode="lines", name="Revenue", line=dict(width=3),
))
fig_trend.add_trace(go.Scatter(
    x=trend_df["month"], y=trend_df["gross_profit"],
    mode="lines", name="Gross Profit", line=dict(width=3),
))
fig_trend.update_layout(
    xaxis_title="Month",
    yaxis_title="Amount (₹)",
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(t=10, b=10),
)
st.plotly_chart(fig_trend, width="stretch")

st.divider()

# ============================================================
# RFM Segment Breakdown
# ============================================================
st.subheader("Customer Segments (RFM) & Lifetime Value")

rfm_query = "SELECT * FROM vw_rfm_clv_summary ORDER BY avg_predicted_clv_2yr DESC;"
rfm_df = run_query(rfm_query)

col_left, col_right = st.columns(2)

with col_left:
    fig_count = go.Figure(go.Bar(
        x=rfm_df["rfm_segment"], y=rfm_df["num_customers"],
        marker_color="#4C78A8",
    ))
    fig_count.update_layout(
        title="Customers per Segment",
        xaxis_title="Segment", yaxis_title="Customers",
        margin=dict(t=40, b=10),
    )
    st.plotly_chart(fig_count, width="stretch")

with col_right:
    fig_clv = go.Figure(go.Bar(
        x=rfm_df["rfm_segment"], y=rfm_df["avg_predicted_clv_2yr"],
        marker_color="#72B7B2",
    ))
    fig_clv.update_layout(
        title="Avg Predicted 2yr CLV per Segment",
        xaxis_title="Segment", yaxis_title="Avg CLV (₹)",
        margin=dict(t=40, b=10),
    )
    st.plotly_chart(fig_clv, width="stretch")

st.dataframe(rfm_df, width="stretch", hide_index=True)

st.divider()

# ============================================================
# CLV Distribution
# ============================================================
st.subheader("Predicted CLV Distribution")

clv_dist_query = "SELECT predicted_clv_2yr FROM vw_customer_clv WHERE predicted_clv_2yr > 0;"
clv_dist_df = run_query(clv_dist_query)

clv_cap = clv_dist_df["predicted_clv_2yr"].quantile(0.99)
clv_dist_filtered = clv_dist_df[clv_dist_df["predicted_clv_2yr"] <= clv_cap]

fig_hist = go.Figure(go.Histogram(
    x=clv_dist_filtered["predicted_clv_2yr"],
    nbinsx=50,
    marker_color="#E45756",
))
fig_hist.update_layout(
    xaxis_title="Predicted 2yr CLV (₹)",
    yaxis_title="Number of Customers",
    margin=dict(t=10, b=10),
)
st.plotly_chart(fig_hist, width="stretch")
st.caption("Top 1% of customers by predicted CLV excluded from this view for readability.")

st.divider()

# ============================================================
# Category Profitability
# ============================================================
st.subheader("Category Profitability")

cat_query = """
SELECT category, total_revenue, total_gross_profit, avg_gross_margin_pct,
       revenue_rank, profit_rank, (revenue_rank - profit_rank) AS rank_gap
FROM vw_category_profitability
ORDER BY total_gross_profit DESC
LIMIT 15;
"""
cat_df = run_query(cat_query)

fig_cat = go.Figure(go.Bar(
    x=cat_df["total_gross_profit"], y=cat_df["category"],
    orientation="h", marker_color="#54A24B",
))
fig_cat.update_layout(
    title="Top 15 Categories by Gross Profit",
    xaxis_title="Gross Profit (₹)", yaxis_title="",
    yaxis=dict(autorange="reversed"),
    margin=dict(t=40, b=10),
    height=500,
)
st.plotly_chart(fig_cat, width="stretch")

st.markdown("**Revenue vs. Profit Rank Mismatch** — categories where high revenue doesn't mean high profit")
mismatch_df = cat_df.reindex(
    cat_df["rank_gap"].abs().sort_values(ascending=False).index
)[["category", "total_revenue", "total_gross_profit", "avg_gross_margin_pct", "revenue_rank", "profit_rank", "rank_gap"]]
st.dataframe(mismatch_df, width="stretch", hide_index=True)

st.divider()

# ============================================================
# Retention Funnel
# ============================================================
st.subheader("Customer Retention Funnel")

funnel_query = """
SELECT
    CASE
        WHEN frequency = 1 THEN '1. One-time buyers'
        WHEN frequency IN (2, 3) THEN '2. Repeat (2-3 orders)'
        ELSE '3. Loyal (4+ orders)'
    END AS retention_stage,
    COUNT(*) AS customers
FROM vw_customer_rfm
GROUP BY retention_stage
ORDER BY retention_stage;
"""
funnel_df = run_query(funnel_query)

fig_funnel = go.Figure(go.Funnel(
    y=funnel_df["retention_stage"],
    x=funnel_df["customers"],
    marker=dict(color=["#4C78A8", "#72B7B2", "#54A24B"]),
))
fig_funnel.update_layout(margin=dict(t=10, b=10))
st.plotly_chart(fig_funnel, width="stretch")

st.caption(
    "Consistent with the RFM analysis: ~97% of Olist customers are one-time buyers. "
    "This is a known characteristic of the dataset, not a data quality issue."
)

st.divider()
st.caption("Built by Shivansh Mishra · Data: Olist Brazilian E-Commerce (Kaggle) · Cost data is synthetic — see docs/cost_assumptions.md")
