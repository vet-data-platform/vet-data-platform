from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    DateType,
    TimestampType,
    LongType,
    DecimalType,
)


SCD_FIELDS = [
    StructField("__START_AT", TimestampType(), True),
    StructField("__END_AT", TimestampType(), True),
]


SILVER_SCHEMAS = {

    "hospital_master": StructType([
        StructField("hospital_key", LongType(), False),
        StructField("hospital_id", StringType(), False),
        StructField("hospital_name", StringType(), True),
        StructField("hospital_address", StringType(), True),
        StructField("hospital_phone", StringType(), True),
        StructField("hospital_email", StringType(), True),
        StructField("source_system", StringType(), True),
        StructField("ingest_timestamp", TimestampType(), True),
    ]),

    "owner_master": StructType([
        StructField("owner_key", LongType(), False),
        StructField("owner_id", StringType(), False),
        StructField("first_name", StringType(), True),
        StructField("last_name", StringType(), True),
        StructField("gender", StringType(), True),
        StructField("dob", DateType(), True),
        StructField("phone", StringType(), True),
        StructField("email", StringType(), True),
        StructField("address", StringType(), True),
        StructField("city", StringType(), True),
        StructField("state", StringType(), True),
        StructField("source_system", StringType(), True),
        StructField("ingest_timestamp", TimestampType(), True),
        *SCD_FIELDS
    ]),

    "pet_master": StructType([
        StructField("pet_key", LongType(), False),
        StructField("pet_id", StringType(), False),
        StructField("pet_name", StringType(), True),
        StructField("species", StringType(), True),
        StructField("breed", StringType(), True),
        StructField("gender", StringType(), True),
        StructField("birth_date", DateType(), True),
        StructField("weight_kg", DecimalType(10, 2), True),
        StructField("microchip_number", StringType(), True),
        StructField("owner_key", LongType(), True),
        StructField("hospital_key", LongType(), True),
        StructField("source_system", StringType(), True),
        StructField("ingest_timestamp", TimestampType(), True),
        *SCD_FIELDS
    ]),

    "doctor_master": StructType([
        StructField("doctor_key", LongType(), False),
        StructField("doctor_id", StringType(), False),
        StructField("doctor_name", StringType(), True),
        StructField("gender", StringType(), True),
        StructField("dob", DateType(), True),
        StructField("phone", StringType(), True),
        StructField("email", StringType(), True),
        StructField("address", StringType(), True),
        StructField("city", StringType(), True),
        StructField("state", StringType(), True),
        StructField("specialization", StringType(), True),
        StructField("hospital_key", LongType(), True),
        StructField("source_system", StringType(), True),
        StructField("ingest_timestamp", TimestampType(), True),
        *SCD_FIELDS
    ]),

    "medication_master": StructType([
        StructField("medication_key", LongType(), False),
        StructField("medication_id", StringType(), False),
        StructField("medication_name", StringType(), True),
        StructField("dosage", StringType(), True),
        StructField("source_system", StringType(), True),
        StructField("ingest_timestamp", TimestampType(), True),
    ]),

    "visit_fact": StructType([
        StructField("visit_key", LongType(), False),
        StructField("visit_id", StringType(), False),
        StructField("visit_date", DateType(), True),
        StructField("pet_key", LongType(), True),
        StructField("doctor_key", LongType(), True),
        StructField("hospital_key", LongType(), True),
        StructField("appointment_type", StringType(), True),
        StructField("diagnosis_code", StringType(), True),
        StructField("diagnosis_description", StringType(), True),
        StructField("source_system", StringType(), True),
        StructField("ingest_timestamp", TimestampType(), True),
    ]),

    "treatment_fact": StructType([
        StructField("treatment_key", LongType(), False),
        StructField("treatment_id", StringType(), False),
        StructField("visit_key", LongType(), True),
        StructField("medication_key", LongType(), True),
        StructField("treatment_name", StringType(), True),
        StructField("treatment_category", StringType(), True),
        StructField("source_system", StringType(), True),
        StructField("ingest_timestamp", TimestampType(), True),
    ]),

    "invoice_fact": StructType([
        StructField("invoice_key", LongType(), False),
        StructField("invoice_id", StringType(), False),
        StructField("visit_key", LongType(), True),
        StructField("hospital_key", LongType(), True),
        StructField("invoice_amount", DecimalType(18, 2), True),
        StructField("tax_amount", DecimalType(18, 2), True),
        StructField("discount_amount", DecimalType(18, 2), True),
        StructField("net_amount", DecimalType(18, 2), True),
        StructField("payment_method", StringType(), True),
        StructField("payment_status", StringType(), True),
        StructField("insurance_provider", StringType(), True),
        StructField("source_system", StringType(), True),
        StructField("ingest_timestamp", TimestampType(), True),
    ]),
}