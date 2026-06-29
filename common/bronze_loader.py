from pyspark.sql.functions import (
    current_timestamp,
    col,
    regexp_extract,
    sha2,
    concat_ws,
    to_json,
    struct
)


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
        .withColumn("raw_json", to_json(struct(*df.columns)))
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
        .withColumn(
            "record_hash",
            sha2(
                concat_ws(
                    "||",
                    col("ingest_file_path"),
                    col("raw_json")
                ),
                256
            )
        )
    )

    return df.select(
        "raw_json",
        "ingest_file_path",
        "source_system",
        "ingest_load_ts",
        "record_hash"
    )