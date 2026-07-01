import streamlit as st
import plotly.express as px
from data.loader import load

st.set_page_config(page_title="Hospitals & Doctors", page_icon="🏥", layout="wide")
st.title("🏥 Hospitals & Doctors")

# Source: vet_platform.gold.daily_revenue_summary
df = load("daily_revenue_summary")

# ── Hospital filter ───────────────────────────────────────────────────────────
hospitals = sorted(df["hospital_name"].dropna().unique())
selected = st.multiselect("Filter by hospital", hospitals, default=hospitals)
filtered = df[df["hospital_name"].isin(selected)]

st.divider()

col_l, col_r = st.columns(2)

# ── Visits per hospital ───────────────────────────────────────────────────────
with col_l:
    st.subheader("Visits per Hospital")
    visits = (
        filtered.groupby("hospital_name")["visit_count"]
        .sum()
        .reset_index()
        .sort_values("visit_count", ascending=False)
    )
    fig1 = px.bar(visits, x="hospital_name", y="visit_count",
                  color="hospital_name",
                  labels={"hospital_name": "Hospital", "visit_count": "Visits"})
    fig1.update_layout(showlegend=False)
    st.plotly_chart(fig1, use_container_width=True)

# ── Revenue per hospital ──────────────────────────────────────────────────────
with col_r:
    st.subheader("Net Revenue per Hospital")
    rev = (
        filtered.groupby("hospital_name")[["total_revenue", "net_revenue"]]
        .sum()
        .reset_index()
        .sort_values("net_revenue", ascending=False)
    )
    fig2 = px.bar(rev, x="hospital_name", y="net_revenue",
                  color="hospital_name",
                  labels={"hospital_name": "Hospital", "net_revenue": "Net Revenue (₹)"})
    fig2.update_layout(showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ── Top doctors by revenue ────────────────────────────────────────────────────
st.subheader("Top Doctors by Revenue")
top_doctors = (
    filtered.groupby("doctor_name")[["total_revenue", "visit_count", "invoice_count"]]
    .sum()
    .reset_index()
    .sort_values("total_revenue", ascending=False)
    .head(15)
)
fig3 = px.bar(
    top_doctors, x="total_revenue", y="doctor_name", orientation="h",
    labels={"doctor_name": "Doctor", "total_revenue": "Revenue (₹)"},
    color="total_revenue", color_continuous_scale="Blues",
)
fig3.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
st.plotly_chart(fig3, use_container_width=True)

st.divider()

# ── Hospital summary table ────────────────────────────────────────────────────
st.subheader("Hospital Summary Table")
table = (
    filtered.groupby("hospital_name")
    .agg(
        total_revenue=("total_revenue", "sum"),
        net_revenue=("net_revenue", "sum"),
        total_tax=("total_tax", "sum"),
        total_discount=("total_discount", "sum"),
        total_visits=("visit_count", "sum"),
        total_invoices=("invoice_count", "sum"),
    )
    .reset_index()
    .sort_values("total_revenue", ascending=False)
)
table.columns = ["Hospital", "Total Revenue (₹)", "Net Revenue (₹)",
                 "Tax (₹)", "Discounts (₹)", "Total Visits", "Total Invoices"]
st.dataframe(table, use_container_width=True, hide_index=True)
