import streamlit as st
import plotly.express as px
from data.loader import load

st.set_page_config(page_title="Patients", page_icon="🐾", layout="wide")
st.title("🐾 Patient Insights")

# Sources: vet_platform.gold.repeat_visit_summary + active_pet_summary
repeat_df = load("repeat_visit_summary")
active_df  = load("active_pet_summary")

# ── Retention KPIs ────────────────────────────────────────────────────────────
repeat_count = int(repeat_df["is_repeat_visitor"].sum())
total_pets   = len(repeat_df)
active_count = int(active_df["is_active"].sum())

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Patients",      f"{total_pets:,}")
c2.metric("Repeat Visitors",     f"{repeat_count:,}")
c3.metric("Retention Rate",      f"{repeat_count / total_pets * 100:.1f}%" if total_pets else "N/A")
c4.metric("Currently Active",    f"{active_count:,}")

st.divider()

col_l, col_r = st.columns(2)

# ── Active vs inactive breakdown ──────────────────────────────────────────────
with col_l:
    st.subheader("Active vs Inactive Patients")
    active_counts = active_df["is_active"].value_counts().reset_index()
    active_counts.columns = ["status", "count"]
    active_counts["status"] = active_counts["status"].map({True: "Active", False: "Inactive"})
    fig1 = px.pie(active_counts, names="status", values="count", hole=0.4,
                  color="status",
                  color_discrete_map={"Active": "#2ecc71", "Inactive": "#e74c3c"})
    st.plotly_chart(fig1, use_container_width=True)

# ── Species breakdown ─────────────────────────────────────────────────────────
with col_r:
    st.subheader("Patients by Species")
    species = active_df["species"].value_counts().reset_index()
    species.columns = ["species", "count"]
    fig2 = px.bar(species, x="species", y="count",
                  labels={"species": "Species", "count": "Patients"},
                  color="species")
    fig2.update_layout(showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ── Repeat visit distribution ─────────────────────────────────────────────────
st.subheader("Visit Frequency Distribution")
fig3 = px.histogram(
    repeat_df, x="total_visit_count", nbins=20,
    labels={"total_visit_count": "Number of Visits", "count": "Patients"},
    color_discrete_sequence=["#0066CC"],
)
st.plotly_chart(fig3, use_container_width=True)

st.divider()

# ── Patients overdue for a visit ──────────────────────────────────────────────
st.subheader("Patients Overdue (Inactive — Days Since Last Visit)")
overdue = (
    active_df[active_df["is_active"] == False]
    [["pet_name", "species", "owner_name", "hospital_name", "last_visit_date", "days_since_last_visit"]]
    .sort_values("days_since_last_visit", ascending=False)
    .head(20)
)
overdue.columns = ["Pet", "Species", "Owner", "Hospital", "Last Visit", "Days Overdue"]
st.dataframe(overdue, use_container_width=True, hide_index=True)
