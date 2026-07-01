import streamlit as st
import pandas as pd
from data import databricks_reader


@st.cache_data(ttl=3600)
def load(table_name: str) -> pd.DataFrame:
    return databricks_reader.read_table(table_name)
