from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    current_date,
    current_timestamp,
    lit,
    regexp_extract,
    sha2,
    concat_ws,
    row_number,
    desc
)
from pyspark.sql.window import Window
from common.config_loader import get_enabled_sources
from common.schema import ENTITY_SCHEMAS
from functools import reduce
from common.constants import HOSPITAL_COLUMN_MAP, PRIMARY_KEYS

spark = SparkSession.getActiveSession()

def _drop_duplicate_columns(df):
    """Drop duplicate columns by keeping only the first occurrence."""
    seen = set()
    select_cols = []
    for c in df.columns:
        if c not in seen:
            select_cols.append(col(c))
            seen.add(c)
    return df.select(*select_cols)


def _rename_columns(df, source_name):
    mapping = HOSPITAL_COLUMN_MAP.get(source_name, {})

    seen = set()
    exprs = []

    for source_col in df.columns:
        target_col = mapping.get(source_col, source_col)

        if target_col not in seen:
            exprs.append(col(source_col).alias(target_col))
            seen.add(target_col)

    return df.select(*exprs)


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


def _ensure_columns(df, schema):
    existing = set(df.columns)
    expressions = []
    for field in schema.fields:
        if field.name in existing:
            expressions.append(col(field.name).cast(field.dataType).alias(field.name))
        else:
            expressions.append(lit(None).cast(field.dataType).alias(field.name))
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
            #  .option("cloudFiles.schemaLocation", source["schema_location"])
             .load(source["path"])
    )

    df = _drop_duplicate_columns(df)
    df = _rename_columns(df, source_name)
    df = df.select(*dict.fromkeys(df.columns))
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
    if entity_name not in ENTITY_SCHEMAS:
        raise ValueError(f"Unknown entity: {entity_name}")
    df = _load_all_sources()
    # Special handling for User entity
    if entity_name == "user":
        df = _build_user_df(df)
    if entity_name == "pet":
        df = df.withColumnRenamed("owner_id", "user_id")
        df = df.withColumnRenamed("weight_kg", "weight")

    entity_columns = ENTITY_SCHEMAS[entity_name]
    df = _ensure_columns(df, entity_columns)
    if entity_name in PRIMARY_KEYS:
        df = _deduplicate(df, PRIMARY_KEYS[entity_name])

    return df


def _build_user_df(df):
    """
    Builds a normalized user dataframe by combining
    Owners and Doctors into a single user entity.
    """

    owner_df = (
        df.select(
            col("owner_id").alias("user_id"),
            lit("OWNER").alias("user_type"),
            col("owner_first_name").alias("first_name"),
            col("owner_last_name").alias("last_name"),
            col("owner_gender").alias("gender"),
            col("owner_dob").alias("dob"),
            col("owner_email").alias("email"),
            col("owner_phone").alias("phone"),
            col("owner_address").alias("address"),
            col("owner_city").alias("city"),
            col("owner_state").alias("state"),
            col("hospital_id"),
            col("source_system"),
            col("ingest_date"),
            col("ingest_timestamp"),
            col("file_name"),
            col("record_hash")
        )
    )

    doctor_df = (
        df.select(
            col("doctor_id").alias("user_id"),
            lit("DOCTOR").alias("user_type"),
            col("doctor_first_name").alias("first_name"),
            col("doctor_last_name").alias("last_name"),
            col("doctor_gender").alias("gender"),
            col("doctor_dob").alias("dob"),
            col("doctor_email").alias("email"),
            col("doctor_phone").alias("phone"),
            col("doctor_address").alias("address"),
            col("doctor_city").alias("city"),
            col("doctor_state").alias("state"),
            col("doctor_specialization").alias("specialization"),
            col("hospital_id"),
            col("source_system"),
            col("ingest_date"),
            col("ingest_timestamp"),
            col("file_name"),
            col("record_hash")
        )
    )

    return (
        owner_df
        .unionByName(doctor_df, allowMissingColumns=True)
    )

def _deduplicate(df, primary_keys):

    if not primary_keys:
        return df

    condition = reduce(
        lambda x, y: x & y,
        [col(pk).isNotNull() for pk in primary_keys]
    )

    df = df.filter(condition)

    return df.dropDuplicates(primary_keys)