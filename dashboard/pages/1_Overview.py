import streamlit as st
import plotly.express as px
from data.loader import load

st.set_page_config(page_title="Overview", page_icon="📊", layout="wide")
st.title("📊 Overview")

# Source: vet_platform.gold.daily_revenue_summary
df = load("daily_revenue_summary")

# ── Headline KPIs ─────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Revenue",    f"₹{df['total_revenue'].sum():,.0f}")
c2.metric("Net Revenue",      f"₹{df['net_revenue'].sum():,.0f}")
c3.metric("Total Visits",     f"{int(df['visit_count'].sum()):,}")
c4.metric("Total Invoices",   f"{int(df['invoice_count'].sum()):,}")

st.divider()

col_l, col_r = st.columns(2)

# ── Revenue trend over time ───────────────────────────────────────────────────
with col_l:
    st.subheader("Revenue Trend")
    daily = (
        df.groupby("revenue_date")[["total_revenue", "net_revenue"]]
        .sum()
        .reset_index()
        .sort_values("revenue_date")
    )
    fig = px.line(
        daily, x="revenue_date",
        y=["total_revenue", "net_revenue"],
        labels={"value": "Amount (₹)", "revenue_date": "Date", "variable": ""},
        color_discrete_map={"total_revenue": "#0066CC", "net_revenue": "#2ecc71"},
    )
    st.plotly_chart(fig, use_container_width=True)

# ── Revenue by hospital ───────────────────────────────────────────────────────
with col_r:
    st.subheader("Revenue by Hospital")
    by_hosp = (
        df.groupby("hospital_name")[["total_revenue", "net_revenue"]]
        .sum()
        .reset_index()
        .sort_values("total_revenue", ascending=False)
    )
    fig2 = px.bar(
        by_hosp, x="hospital_name", y="total_revenue",
        labels={"hospital_name": "Hospital", "total_revenue": "Revenue (₹)"},
        color="hospital_name",
    )
    fig2.update_layout(showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ── Tax & discount summary ────────────────────────────────────────────────────
st.subheader("Revenue Breakdown Summary")
summary_cols = st.columns(3)
summary_cols[0].metric("Total Tax Collected",    f"₹{df['total_tax'].sum():,.0f}")
summary_cols[1].metric("Total Discounts Given",  f"₹{df['total_discount'].sum():,.0f}")
summary_cols[2].metric("Avg Revenue / Visit",
    f"₹{(df['total_revenue'].sum() / df['visit_count'].sum()):,.0f}"
    if df['visit_count'].sum() > 0 else "N/A"
)
