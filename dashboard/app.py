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
st.plotly_chart(fig_trend, use_container_width=True)
