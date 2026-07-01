import os

try:
    import streamlit as st
    def _get(key, default=None):
        return st.secrets.get(key, os.getenv(key, default))
except Exception:
    def _get(key, default=None):
        return os.getenv(key, default)

# Gold — live production tables (used when USE_BRONZE = false)
DATABRICKS_HOST      = _get("DATABRICKS_HOST")
DATABRICKS_TOKEN     = _get("DATABRICKS_TOKEN")
DATABRICKS_HTTP_PATH = _get("DATABRICKS_HTTP_PATH")
DATABRICKS_CATALOG   = _get("DATABRICKS_CATALOG", "vet_platform")
DATABRICKS_SCHEMA    = _get("DATABRICKS_SCHEMA", "gold")

# Bronze — for UI testing before gold layer is ready (used when USE_BRONZE = true)
DATABRICKS_BRONZE_CATALOG = _get("DATABRICKS_BRONZE_CATALOG", "vet_platform")
DATABRICKS_BRONZE_SCHEMA  = _get("DATABRICKS_BRONZE_SCHEMA", "bronze")
USE_BRONZE                = _get("USE_BRONZE", "false").lower() == "true"
