import dlt

from common.config_loader import get_source
from common.bronze_loader import load_bronze


@dlt.table(
    name="bronze_hospital_a",
    comment="Bronze layer for Hospital A",
    table_properties={"quality": "bronze"}
)
def bronze_hospital_a():
    return load_bronze(get_source("hospital_a"))


@dlt.table(
    name="bronze_hospital_b",
    comment="Bronze layer for Hospital B",
    table_properties={"quality": "bronze"}
)
def bronze_hospital_b():
    return load_bronze(get_source("hospital_b"))


@dlt.table(
    name="bronze_hospital_c",
    comment="Bronze layer for Hospital C",
    table_properties={"quality": "bronze"}
)
def bronze_hospital_c():
    return load_bronze(get_source("hospital_c"))