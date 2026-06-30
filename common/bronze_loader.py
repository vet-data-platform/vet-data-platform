from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    current_date,
    current_timestamp,
    lit,
    regexp_extract,
    sha2,
    concat_ws
)
from common.config_loader import get_enabled_sources

spark = SparkSession.getActiveSession()

HOSPITAL_COLUMN_MAP = {
    "hospital_a": {
        "hospital_code": "hospital_id",
        "provider_name": "hospital_name",
        "zip": "postal_code",
        "visit_notes": "treatment_notes",
        "invoice_total": "invoice_amount",
        "visit_date_time": "visit_date"
    },
    "hospital_b": {
        "hospital_code": "hospital_id",
        "provider_name": "hospital_name",
        "zip_code": "postal_code",
        "visit_notes": "treatment_notes",
        "invoice_total": "invoice_amount",
        "visit_date_time": "visit_date"
    },
    "hospital_c": {
        "hospital_code": "hospital_id",
        "provider_name": "hospital_name",
        "zip_code": "postal_code",
        "visit_notes": "treatment_notes",
        "invoice_total": "invoice_amount",
        "visit_date_time": "visit_date"
    }
}

ENTITY_COLUMNS = {
    "hospital": [
        "hospital_id",
        "hospital_name",
        "hospital_type",
        "address",
        "city",
        "state",
        "country",
        "postal_code",
        "phone",
        "email"
    ],
    "user": [
        "user_id",
        "user_type",
        "first_name",
        "last_name",
        "gender",
        "dob",
        "email",
        "phone",
        "address",
        "city",
        "state",
        "postal_code",
        "specialization",
        "license_number",
        "hospital_id"
    ],
    "pet": [
        "pet_id",
        "user_id",
        "hospital_id",
        "pet_name",
        "species",
        "breed",
        "gender",
        "birth_date",
        "weight",
        "color",
        "microchip_number",
        "vaccination_status"
    ],
    "visit": [
        "visit_id",
        "pet_id",
        "doctor_user_id",
        "hospital_id",
        "visit_date",
        "visit_time",
        "appointment_type",
        "diagnosis",
        "symptoms",
        "treatment_notes",
        "visit_status"
    ],
    "invoice": [
        "invoice_id",
        "visit_id",
        "hospital_id",
        "invoice_date",
        "invoice_amount",
        "tax_amount",
        "discount_amount",
        "net_amount",
        "payment_method",
        "payment_status",
        "insurance_provider"
    ]
}

METADATA_COLUMNS = [
    "source_system",
    "ingest_date",
    "ingest_timestamp",
    "file_name",
    "record_hash"
]


def _rename_columns(df, source_name: str):
    mapping = HOSPITAL_COLUMN_MAP.get(source_name, {})
    renamed = []
    for c in df.columns:
        renamed.append(col(c).alias(mapping.get(c, c)))
    return df.select(*renamed)


def _with_ingest_metadata(df, source_name: str):
    return (
        df
        .withColumn("source_system", lit(source_name))
        .withColumn("file_name", regexp_extract(col("_metadata.file_path"), "([^/]+)$", 1))
        .withColumn("ingest_timestamp", current_timestamp())
        .withColumn("ingest_date", current_date())
    )


def _with_record_hash(df):
    hash_columns = [col(c).cast("string") for c in df.columns if c != "record_hash"]
    return df.withColumn("record_hash", sha2(concat_ws("||", *hash_columns), 256))


def _ensure_columns(df, columns):
    expressions = []
    existing_columns = set(df.columns)
    for column_name in columns:
        if column_name in existing_columns:
            expressions.append(col(column_name))
        else:
            expressions.append(lit(None).alias(column_name))
    return df.select(*expressions)


def _load_source(source_name: str, source: dict):
    df = (
        spark.readStream
             .format("cloudFiles")
             .option("cloudFiles.format", "csv")
             .option("header", "true")
             .option("recursiveFileLookup", "true")
             .option("cloudFiles.inferColumnTypes", "true")
             .option("cloudFiles.schemaEvolutionMode", "addNewColumns")
             .option("cloudFiles.schemaLocation", source["schema_location"])
             .load(source["path"])
    )

    df = _rename_columns(df, source_name)
    df = _with_ingest_metadata(df, source_name)
    return _with_record_hash(df)


def _load_all_sources():
    enabled_sources = get_enabled_sources()
    master_df = None
    for source_name, source in enabled_sources.items():
        source_df = _load_source(source_name, source)
        master_df = source_df if master_df is None else master_df.unionByName(source_df, allowMissingColumns=True)
    if master_df is None:
        raise ValueError("No enabled sources found in config/sources.yaml")
    return master_df


def get_entity_df(entity_name: str):
    if entity_name not in ENTITY_COLUMNS:
        raise ValueError(f"Unknown entity: {entity_name}")

    df = _load_all_sources()
    entity_columns = ENTITY_COLUMNS[entity_name] + METADATA_COLUMNS
    return _ensure_columns(df, entity_columns)