from pyspark.sql.functions import (
    current_timestamp,
    col,
    regexp_extract,
    sha2,
    concat_ws,
    to_json,
    struct
)
from pyspark.sql import SparkSession

spark = SparkSession.getActiveSession()

def load_bronze(source):

    df = (
        spark.readStream
            .format("cloudFiles")
            .option("cloudFiles.format", "csv")
            .option("header", "true")
            .option("recursiveFileLookup", "true")
            .option("cloudFiles.inferColumnTypes", "true")
            .option("cloudFiles.schemaEvolutionMode", "addNewColumns")
            .load(source["path"])
    )

    df = (
        df
        # .withColumn("raw_json", to_json(struct(*df.columns)))
        .withColumn("ingest_file_path", col("_metadata.file_path"))
        .withColumn("ingest_load_ts", current_timestamp())
        .withColumn(
            "source_system",
            regexp_extract(
                col("_metadata.file_path"),
                ".*/raw/([^/]+)/.*",
                1
            )
        )

    return df.withColumn(
    "record_hash",
    sha2(
        concat_ws("||", *[col(c).cast("string") for c in df.columns]),
        256
    )
)