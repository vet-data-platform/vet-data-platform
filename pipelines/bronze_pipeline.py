import dlt
from pyspark.sql.functions import current_timestamp, col, regexp_extract, sha2, concat_ws, to_json, struct
from pyspark.sql.types import StringType

RAW_BASE_PATH = "s3a://vet-data-platform/raw/"
# SCHEMA_LOCATION = "dbfs:/FileStore/bronze_schema_checkpoint"

@dlt.table(
    comment="Raw bronze layer for hospital files with variable source schemas.",
    table_properties={"quality": "bronze"}
)
def bronze_hospitals_raw():
    """Ingest raw hospital file lines and preserve file metadata, avoiding schema union nulls."""
    raw = (
        spark.readStream
            .format("cloudFiles")
            .option("cloudFiles.format", "csv")
            # .option("cloudFiles.schemaLocation", SCHEMA_LOCATION)
            .option("cloudFiles.inferColumnTypes", "true")
            .option("cloudFiles.schemaEvolutionMode", "addNewColumns")
            .option("recursiveFileLookup", "true")
            .option("header", "true")
            .load(RAW_BASE_PATH)
    )

    raw = raw.withColumn("raw_json", to_json(struct(*raw.columns)))
    raw = raw.withColumn("ingest_file_path", col("_metadata.file_path"))
    raw = raw.withColumn("ingest_load_ts", current_timestamp())
    raw = raw.withColumn(
        "source_system",
        regexp_extract(col("_metadata.file_path"), ".*/raw/([^/]+)/.*", 1)
    )

    return raw.withColumn(
        "record_hash",
        sha2(concat_ws("||", col("raw_json"), col("ingest_file_path")), 256)
    ).select(
        "raw_json",
        "ingest_file_path",
        "source_system",
        "ingest_load_ts",
        "record_hash"
    )
