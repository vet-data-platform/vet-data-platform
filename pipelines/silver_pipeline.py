import dlt
from pyspark.sql.functions import col

from common.silver_loader import (
    owner_source,
    doctor_source,
    pet_source,
    hospital_master,
    medication_master,
    visit_fact,
    treatment_fact,
    invoice_fact,
)


# ============================================================
# SCD TYPE 2 SOURCE VIEWS
# ============================================================

@dlt.view(
    name="owner_source",
    comment="Prepared owner records for SCD Type 2 processing"
)
def owner_source_view():
    return owner_source()


@dlt.view(
    name="doctor_source",
    comment="Prepared doctor records for SCD Type 2 processing"
)
def doctor_source_view():
    return doctor_source()


@dlt.view(
    name="pet_source",
    comment="Prepared pet records for SCD Type 2 processing"
)
def pet_source_view():
    return pet_source()


# ============================================================
# DIMENSION TABLES
# ============================================================

#
# Hospital (SCD Type 1)
#
@dlt.table(
    name="silver_hospital_master",
    comment="Silver Hospital Dimension",
    table_properties={"quality": "silver"}
)
def silver_hospital_master():
    return hospital_master()


#
# Owner (SCD Type 2)
#
dlt.create_streaming_table(
    name="silver_owner_master",
    comment="Owner Dimension with SCD Type 2",
    table_properties={"quality": "silver"}
)

dlt.apply_changes(
    target="silver_owner_master",
    source="owner_source",
    keys=["owner_id"],
    sequence_by=col("ingest_timestamp"),
    stored_as_scd_type=2
)


#
# Doctor (SCD Type 2)
#
dlt.create_streaming_table(
    name="silver_doctor_master",
    comment="Doctor Dimension with SCD Type 2",
    table_properties={"quality": "silver"}
)

dlt.apply_changes(
    target="silver_doctor_master",
    source="doctor_source",
    keys=["doctor_id"],
    sequence_by=col("ingest_timestamp"),
    stored_as_scd_type=2
)


#
# Pet (SCD Type 2)
#
dlt.create_streaming_table(
    name="silver_pet_master",
    comment="Pet Dimension with SCD Type 2",
    table_properties={"quality": "silver"}
)

dlt.apply_changes(
    target="silver_pet_master",
    source="pet_source",
    keys=["pet_id"],
    sequence_by=col("ingest_timestamp"),
    stored_as_scd_type=2
)


#
# Medication (SCD Type 1)
#
@dlt.table(
    name="silver_medication_master",
    comment="Medication Dimension",
    table_properties={"quality": "silver"}
)
def silver_medication_master():
    return medication_master()


# ============================================================
# FACT TABLES
# ============================================================

@dlt.table(
    name="silver_visit_fact",
    comment="Visit Fact",
    table_properties={"quality": "silver"}
)
def silver_visit_fact():
    return visit_fact()


@dlt.table(
    name="silver_treatment_fact",
    comment="Treatment Fact",
    table_properties={"quality": "silver"}
)
def silver_treatment_fact():
    return treatment_fact()


@dlt.table(
    name="silver_invoice_fact",
    comment="Invoice Fact",
    table_properties={"quality": "silver"}
)
def silver_invoice_fact():
    return invoice_fact()