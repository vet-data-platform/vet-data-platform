import streamlit as st

st.set_page_config(
    page_title="Vet Data Platform",
    page_icon="🐾",
    layout="wide",
)

st.title("🐾 Vet Data Platform — KPI Dashboard")
st.markdown("Business intelligence dashboard for the veterinary hospital network.")

st.divider()

col1, col2 = st.columns([3, 1])
with col1:
    st.info("Use the **sidebar** to navigate: Overview, Hospitals, Patients, Treatments.")
with col2:
    st.caption("Data source: **🟢 Databricks (live)**")
    st.caption("Cache refreshes every hour.")
