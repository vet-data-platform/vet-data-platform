from databricks import sql
import pandas as pd
import config
from data.bronze_queries import BRONZE_QUERIES


def _connect():
    return sql.connect(
        server_hostname=config.DATABRICKS_HOST,
        http_path=config.DATABRICKS_HTTP_PATH,
        access_token=config.DATABRICKS_TOKEN,
    )


def read_table(table_name: str) -> pd.DataFrame:
    if config.USE_BRONZE:
        query = BRONZE_QUERIES[table_name].format(
            catalog=config.DATABRICKS_BRONZE_CATALOG,
            schema=config.DATABRICKS_BRONZE_SCHEMA,
        )
    else:
        query = (
            f"SELECT * FROM {config.DATABRICKS_CATALOG}"
            f".{config.DATABRICKS_SCHEMA}.{table_name}"
        )

    with _connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall_arrow().to_pandas()
