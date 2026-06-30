from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    DateType,
    TimestampType,
    DoubleType,
    DecimalType
)

METADATA_FIELDS = [
    StructField("source_system", StringType(), True),
    StructField("ingest_date", DateType(), True),
    StructField("ingest_timestamp", TimestampType(), True),
    StructField("file_name", StringType(), True),
    StructField("record_hash", StringType(), True),
]

ENTITY_SCHEMAS = {

    "hospital": StructType([
        StructField("hospital_id", StringType(), True),
        StructField("hospital_name", StringType(), True),
        StructField("hospital_type", StringType(), True),
        StructField("address", StringType(), True),
        StructField("city", StringType(), True),
        StructField("state", StringType(), True),
        StructField("country", StringType(), True),
        StructField("postal_code", StringType(), True),
        StructField("phone", StringType(), True),
        StructField("email", StringType(), True),
        *METADATA_FIELDS
    ]),

    "user": StructType([
        StructField("user_id", StringType(), True),
        StructField("user_type", StringType(), True),
        StructField("first_name", StringType(), True),
        StructField("last_name", StringType(), True),
        StructField("gender", StringType(), True),
        StructField("dob", DateType(), True),
        StructField("email", StringType(), True),
        StructField("phone", StringType(), True),
        StructField("address", StringType(), True),
        StructField("city", StringType(), True),
        StructField("state", StringType(), True),
        StructField("postal_code", StringType(), True),
        StructField("specialization", StringType(), True),
        StructField("license_number", StringType(), True),
        StructField("hospital_id", StringType(), True),
        *METADATA_FIELDS
    ]),

    "pet": StructType([
        StructField("pet_id", StringType(), True),
        StructField("user_id", StringType(), True),
        StructField("hospital_id", StringType(), True),
        StructField("pet_name", StringType(), True),
        StructField("species", StringType(), True),
        StructField("breed", StringType(), True),
        StructField("gender", StringType(), True),
        StructField("birth_date", DateType(), True),
        StructField("weight", DoubleType(), True),
        StructField("color", StringType(), True),
        StructField("microchip_number", StringType(), True),
        StructField("vaccination_status", StringType(), True),
        *METADATA_FIELDS
    ]),

    "visit": StructType([
        StructField("visit_id", StringType(), True),
        StructField("pet_id", StringType(), True),
        StructField("doctor_user_id", StringType(), True),
        StructField("hospital_id", StringType(), True),
        StructField("visit_date", DateType(), True),
        StructField("visit_time", TimestampType(), True),
        StructField("appointment_type", StringType(), True),
        StructField("diagnosis", StringType(), True),
        StructField("symptoms", StringType(), True),
        StructField("treatment_notes", StringType(), True),
        StructField("visit_status", StringType(), True),
        *METADATA_FIELDS
    ]),

    "invoice": StructType([
        StructField("invoice_id", StringType(), True),
        StructField("visit_id", StringType(), True),
        StructField("hospital_id", StringType(), True),
        StructField("invoice_date", DateType(), True),
        StructField("invoice_amount", DecimalType(18,2), True),
        StructField("tax_amount", DecimalType(18,2), True),
        StructField("discount_amount", DecimalType(18,2), True),
        StructField("net_amount", DecimalType(18,2), True),
        StructField("payment_method", StringType(), True),
        StructField("payment_status", StringType(), True),
        StructField("insurance_provider", StringType(), True),
        *METADATA_FIELDS
    ])
}