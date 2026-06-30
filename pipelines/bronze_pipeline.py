import dlt
from common.bronze_loader import get_entity_df


@dlt.table(
    name="bronze_hospital",
    comment="Bronze layer for hospital master data",
    table_properties={"quality": "bronze"}
)
def bronze_hospital():
    return get_entity_df("hospital")


@dlt.table(
    name="bronze_user",
    comment="Bronze layer for all users (owners and doctors)",
    table_properties={"quality": "bronze"}
)
def bronze_user():
    return get_entity_df("user")


@dlt.table(
    name="bronze_pet",
    comment="Bronze layer for pet master data",
    table_properties={"quality": "bronze"}
)
def bronze_pet():
    return get_entity_df("pet")


@dlt.table(
    name="bronze_visit",
    comment="Bronze layer for pet visit and appointment details",
    table_properties={"quality": "bronze"}
)
def bronze_visit():
    return get_entity_df("visit")


@dlt.table(
    name="bronze_invoice",
    comment="Bronze layer for invoice and billing details",
    table_properties={"quality": "bronze"}
)
def bronze_invoice():
    return get_entity_df("invoice")