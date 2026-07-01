import dlt

from pyspark.sql.functions import (
    col,
    lit,
    trim,
    lower,
    regexp_replace,
    when,
    concat_ws,
    sha2,
    xxhash64,
    abs as spark_abs,
    current_timestamp
)


# -------------------------
# COMMON HELPERS
# -------------------------

def add_surrogate_key(df, key_col, *source_cols):
    return df.withColumn(
        key_col,
        spark_abs(xxhash64(*[col(c) for c in source_cols]))
    )


def clean_string(column_name):
    return trim(regexp_replace(col(column_name), "\\s+", " "))


def clean_email(column_name):
    return when(
        lower(trim(col(column_name))).rlike(
            "^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$"
        ),
        lower(trim(col(column_name)))
    ).otherwise(lit(None))


def clean_phone(column_name):
    return regexp_replace(col(column_name), "[^0-9]", "")


def create_change_hash(columns):
    return sha2(
        concat_ws("||", *[col(c).cast("string") for c in columns]),
        256
    )


# -------------------------
# SCD TYPE 2 SOURCE: OWNER
# -------------------------

def owner_source():
    df = dlt.read_stream("bronze_user")

    df = (
        df
        .filter((col("user_type") == "OWNER") & col("user_id").isNotNull())
        .select(
            col("user_id").alias("owner_id"),
            clean_string("first_name").alias("first_name"),
            clean_string("last_name").alias("last_name"),
            clean_string("gender").alias("gender"),
            col("dob"),
            clean_phone("phone").alias("phone"),
            clean_email("email").alias("email"),
            clean_string("address").alias("address"),
            clean_string("city").alias("city"),
            clean_string("state").alias("state"),
            col("source_system"),
            col("ingest_timestamp")
        )
    )

    change_cols = [
        "first_name", "last_name", "gender", "dob", "phone",
        "email", "address", "city", "state", "source_system"
    ]

    df = df.withColumn("change_hash", create_change_hash(change_cols))

    df = add_surrogate_key(df, "owner_key", "owner_id", "change_hash")

    return df.dropDuplicates(["owner_id", "change_hash"])


# -------------------------
# SCD TYPE 2 SOURCE: DOCTOR
# -------------------------

def doctor_source():
    df = dlt.read_stream("bronze_user")

    hospital = (
        dlt.read("silver_hospital_master")
        .select("hospital_id", "hospital_key")
    )

    df = (
        df
        .filter((col("user_type") == "DOCTOR") & col("user_id").isNotNull())
        .join(hospital, "hospital_id", "left")
        .select(
            col("user_id").alias("doctor_id"),
            concat_ws(" ", clean_string("first_name"), clean_string("last_name")).alias("doctor_name"),
            clean_string("gender").alias("gender"),
            col("dob"),
            clean_phone("phone").alias("phone"),
            clean_email("email").alias("email"),
            clean_string("address").alias("address"),
            clean_string("city").alias("city"),
            clean_string("state").alias("state"),
            clean_string("specialization").alias("specialization"),
            col("hospital_key"),
            col("source_system"),
            col("ingest_timestamp")
        )
    )

    change_cols = [
        "doctor_name", "gender", "dob", "phone", "email",
        "address", "city", "state", "specialization",
        "hospital_key", "source_system"
    ]

    df = df.withColumn("change_hash", create_change_hash(change_cols))

    df = add_surrogate_key(df, "doctor_key", "doctor_id", "change_hash")

    return df.dropDuplicates(["doctor_id", "change_hash"])


# -------------------------
# SCD TYPE 2 SOURCE: PET
# -------------------------

def pet_source():
    df = dlt.read_stream("bronze_pet")

    owner = (
        dlt.read("silver_owner_master")
        .filter(col("__END_AT").isNull())
        .select("owner_id", "owner_key")
    )

    hospital = (
        dlt.read("silver_hospital_master")
        .select("hospital_id", "hospital_key")
    )

    df = (
        df
        .filter(col("pet_id").isNotNull())
        .join(owner, df.user_id == owner.owner_id, "left")
        .join(hospital, "hospital_id", "left")
        .select(
            df.pet_id,
            clean_string("pet_name").alias("pet_name"),
            clean_string("species").alias("species"),
            clean_string("breed").alias("breed"),
            clean_string("gender").alias("gender"),
            df.birth_date,
            col("weight").alias("weight_kg"),
            df.microchip_number,
            owner.owner_key,
            hospital.hospital_key,
            df.source_system,
            df.ingest_timestamp
        )
    )

    change_cols = [
        "pet_name", "species", "breed", "gender",
        "birth_date", "weight_kg", "microchip_number",
        "owner_key", "hospital_key", "source_system"
    ]

    df = df.withColumn("change_hash", create_change_hash(change_cols))

    df = add_surrogate_key(df, "pet_key", "pet_id", "change_hash")

    return df.dropDuplicates(["pet_id", "change_hash"])


# -------------------------
# TYPE 1: HOSPITAL MASTER
# -------------------------

def hospital_master():
    df = dlt.read_stream("bronze_hospital")

    df = (
        df
        .filter(col("hospital_id").isNotNull())
        .select(
            "hospital_id",
            clean_string("hospital_name").alias("hospital_name"),
            clean_string("hospital_address").alias("hospital_address"),
            clean_phone("hospital_phone").alias("hospital_phone"),
            clean_email("hospital_email").alias("hospital_email"),
            "source_system",
            "ingest_timestamp"
        )
        .dropDuplicates(["hospital_id"])
    )

    return add_surrogate_key(df, "hospital_key", "hospital_id")


# -------------------------
# TYPE 1: MEDICATION MASTER
# -------------------------

def medication_master():
    df = dlt.read_stream("bronze_visit")

    df = (
        df
        .filter(col("medication_name").isNotNull())
        .select(
            sha2(
                concat_ws("||", clean_string("medication_name"), clean_string("dosage")),
                256
            ).alias("medication_id"),
            clean_string("medication_name").alias("medication_name"),
            clean_string("dosage").alias("dosage"),
            "source_system",
            "ingest_timestamp"
        )
        .dropDuplicates(["medication_id"])
    )

    return add_surrogate_key(df, "medication_key", "medication_id")


# -------------------------
# FACT: VISIT
# -------------------------

def visit_fact():
    visit = dlt.read_stream("bronze_visit")

    pet = (
        dlt.read("silver_pet_master")
        .filter(col("__END_AT").isNull())
        .select("pet_id", "pet_key")
    )

    doctor = (
        dlt.read("silver_doctor_master")
        .filter(col("__END_AT").isNull())
        .select("doctor_id", "doctor_key")
    )

    hospital = (
        dlt.read("silver_hospital_master")
        .select("hospital_id", "hospital_key")
    )

    df = (
        visit
        .filter(
            col("visit_id").isNotNull() &
            col("pet_id").isNotNull() &
            col("doctor_id").isNotNull()
        )
        .join(pet, "pet_id", "left")
        .join(doctor, "doctor_id", "left")
        .join(hospital, "hospital_id", "left")
        .select(
            visit.visit_id,
            visit.visit_date,
            pet.pet_key,
            doctor.doctor_key,
            hospital.hospital_key,
            clean_string("appointment_type").alias("appointment_type"),
            clean_string("diagnosis_code").alias("diagnosis_code"),
            clean_string("diagnosis_description").alias("diagnosis_description"),
            visit.source_system,
            visit.ingest_timestamp
        )
        .dropDuplicates(["visit_id"])
    )

    return add_surrogate_key(df, "visit_key", "visit_id")


# -------------------------
# FACT: TREATMENT
# -------------------------

def treatment_fact():
    visit = dlt.read_stream("bronze_visit")

    visit_fact_df = (
        dlt.read("silver_visit_fact")
        .select("visit_id", "visit_key")
    )

    medication = (
        dlt.read("silver_medication_master")
        .select("medication_id", "medication_key")
    )

    df = (
        visit
        .filter(
            col("treatment_id").isNotNull() &
            col("visit_id").isNotNull()
        )
        .select(
            "treatment_id",
            "visit_id",
            sha2(
                concat_ws("||", clean_string("medication_name"), clean_string("dosage")),
                256
            ).alias("medication_id"),
            clean_string("treatment_name").alias("treatment_name"),
            lit(None).cast("string").alias("treatment_category"),
            "source_system",
            "ingest_timestamp"
        )
        .join(visit_fact_df, "visit_id", "left")
        .join(medication, "medication_id", "left")
        .select(
            "treatment_id",
            "visit_key",
            "medication_key",
            "treatment_name",
            "treatment_category",
            "source_system",
            "ingest_timestamp"
        )
        .dropDuplicates(["treatment_id"])
    )

    return add_surrogate_key(df, "treatment_key", "treatment_id")


# -------------------------
# FACT: INVOICE
# -------------------------

def invoice_fact():
    invoice = dlt.read_stream("bronze_invoice")

    visit = (
        dlt.read("silver_visit_fact")
        .select("visit_id", "visit_key", "hospital_key")
    )

    df = (
        invoice
        .filter(
            col("invoice_id").isNotNull() &
            col("visit_id").isNotNull() &
            col("invoice_amount").isNotNull() &
            (col("invoice_amount") >= 0)
        )
        .join(visit, "visit_id", "left")
        .withColumn(
            "net_amount",
            col("invoice_amount") + col("tax_amount") - col("discount_amount")
        )
        .select(
            invoice.invoice_id,
            visit.visit_key,
            visit.hospital_key,
            invoice.invoice_amount,
            invoice.tax_amount,
            invoice.discount_amount,
            col("net_amount"),
            clean_string("payment_method").alias("payment_method"),
            clean_string("payment_status").alias("payment_status"),
            clean_string("insurance_provider").alias("insurance_provider"),
            invoice.source_system,
            invoice.ingest_timestamp
        )
        .dropDuplicates(["invoice_id"])
    )

    return add_surrogate_key(df, "invoice_key", "invoice_id")