import streamlit as st
import plotly.express as px
from data.loader import load

st.set_page_config(page_title="Treatments", page_icon="💊", layout="wide")
st.title("💊 Treatments & Medications")

# Source: vet_platform.gold.top_treatment_summary
df = load("top_treatment_summary")

# ── KPIs ─────────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
c1.metric("Total Treatment Types", f"{df['treatment_name'].nunique():,}")
c2.metric("Total Usages",          f"{int(df['usage_count'].sum()):,}")
c3.metric("Unique Pets Treated",   f"{int(df['unique_pets_treated'].sum()):,}")

st.divider()

col_l, col_r = st.columns(2)

# ── Top treatments by usage ───────────────────────────────────────────────────
with col_l:
    st.subheader("Top Treatments by Usage")
    top = df.nsmallest(15, "usage_rank")[["treatment_name", "usage_count"]].sort_values("usage_count")
    fig1 = px.bar(
        top, x="usage_count", y="treatment_name", orientation="h",
        labels={"treatment_name": "Treatment", "usage_count": "Usages"},
        color="usage_count", color_continuous_scale="Blues",
    )
    fig1.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig1, use_container_width=True)

# ── Treatments by category ────────────────────────────────────────────────────
with col_r:
    st.subheader("Usage by Treatment Category")
    by_cat = (
        df.groupby("treatment_category")["usage_count"]
        .sum()
        .reset_index()
        .sort_values("usage_count", ascending=False)
    )
    fig2 = px.pie(by_cat, names="treatment_category", values="usage_count", hole=0.4)
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ── Most used medications per treatment ───────────────────────────────────────
st.subheader("Most Used Medication per Treatment")
med_table = (
    df[["treatment_name", "treatment_category", "usage_count",
        "unique_pets_treated", "most_used_medication", "usage_rank"]]
    .sort_values("usage_rank")
    .head(20)
)
med_table.columns = ["Treatment", "Category", "Usages", "Unique Pets", "Top Medication", "Rank"]
st.dataframe(med_table, use_container_width=True, hide_index=True)
