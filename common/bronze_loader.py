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

spark = SparkSession.getActiveSession()

HOSPITAL_COLUMN_MAP = {
    'hospital_a': {'visit_id': 'visit_id', 'visit_date': 'visit_date', 'hospital_id': 'hospital_id', 'hospital_name': 'hospital_name', 'hospital_address': 'hospital_address', 'hospital_phone': 'hospital_phone', 'hospital_email': 'hospital_email', 'pet_id': 'pet_id', 'pet_name': 'pet_name', 'species': 'species', 'breed': 'breed', 'gender': 'gender', 'birth_date': 'birth_date', 'weight_kg': 'weight_kg', 'microchip_number': 'microchip_number', 'owner_id': 'owner_id', 'owner_first_name': 'owner_first_name', 'owner_last_name': 'owner_last_name', 'owner_gender': 'owner_gender', 'owner_dob': 'owner_dob', 'owner_phone': 'owner_phone', 'owner_email': 'owner_email', 'owner_address': 'owner_address', 'owner_city': 'owner_city', 'owner_state': 'owner_state', 'doctor_id': 'doctor_id', 'doctor_first_name': 'doctor_first_name', 'doctor_last_name': 'doctor_last_name', 'doctor_gender': 'doctor_gender', 'doctor_dob': 'doctor_dob', 'doctor_phone': 'doctor_phone', 'doctor_email': 'doctor_email', 'doctor_address': 'doctor_address', 'doctor_city': 'doctor_city', 'doctor_state': 'doctor_state', 'doctor_specialization': 'doctor_specialization', 'appointment_type': 'appointment_type', 'diagnosis_code': 'diagnosis_code', 'diagnosis_description': 'diagnosis_description', 'treatment_id': 'treatment_id', 'treatment_name': 'treatment_name', 'medication_name': 'medication_name', 'dosage': 'dosage', 'invoice_id': 'invoice_id', 'invoice_amount': 'invoice_amount', 'tax_amount': 'tax_amount', 'discount_amount': 'discount_amount', 'payment_method': 'payment_method', 'payment_status': 'payment_status', 'insurance_provider': 'insurance_provider', 'created_timestamp': 'created_timestamp', 'updated_timestamp': 'updated_timestamp'}, 
    'hospital_b': {'appointment_id': 'visit_id', 'appointment_date': 'visit_date', 'clinic_code': 'hospital_id', 'clinic_name': 'hospital_name', 'clinic_address': 'hospital_address', 'clinic_phone': 'hospital_phone', 'clinic_email': 'hospital_email', 'animal_id': 'pet_id', 'animal_name': 'pet_name', 'animal_type': 'species', 'animal_breed': 'breed', 'sex': 'gender', 'dob': 'birth_date', 'weight': 'weight_kg', 'chip_no': 'microchip_number', 'customer_id': 'owner_id', 'customer_first_name': 'owner_first_name', 'customer_last_name': 'owner_last_name', 'customer_gender': 'owner_gender', 'customer_dob': 'owner_dob', 'contact_number': 'owner_phone', 'email_address': 'owner_email', 'customer_address': 'owner_address', 'customer_city': 'owner_city', 'customer_state': 'owner_state', 'vet_id': 'doctor_id', 'vet_first_name': 'doctor_first_name', 'vet_last_name': 'doctor_last_name', 'vet_gender': 'doctor_gender', 'vet_dob': 'doctor_dob', 'vet_contact_number': 'doctor_phone', 'vet_email_address': 'doctor_email', 'vet_address': 'doctor_address', 'vet_city': 'doctor_city', 'vet_state': 'doctor_state', 'speciality': 'doctor_specialization', 'appointment_category': 'appointment_type', 'disease_code': 'diagnosis_code', 'disease_desc': 'diagnosis_description', 'procedure_id': 'treatment_id', 'procedure_name': 'treatment_name', 'medicine': 'medication_name', 'medicine_dose': 'dosage', 'bill_id': 'invoice_id', 'bill_amount': 'invoice_amount', 'gst_amount': 'tax_amount', 'discount': 'discount_amount', 'pay_mode': 'payment_method', 'payment_flag': 'payment_status', 'insurance_company': 'insurance_provider', 'created_at': 'created_timestamp', 'modified_at': 'updated_timestamp'},
    'hospital_c': {'record_id': 'visit_id', 'visit_timestamp': 'visit_date', 'facility_id': 'hospital_id', 'facility_name': 'hospital_name', 'facility_address': 'hospital_address', 'facility_phone': 'hospital_phone', 'facility_email': 'hospital_email', 'patient_id': 'pet_id', 'patient_name': 'pet_name', 'patient_species': 'species', 'patient_breed': 'breed', 'patient_gender': 'gender', 'patient_dob': 'birth_date', 'body_weight': 'weight_kg', 'rfid_number': 'microchip_number', 'owner_ref': 'owner_id', 'client_first_name': 'owner_first_name', 'client_last_name': 'owner_last_name', 'client_gender': 'owner_gender', 'client_dob': 'owner_dob', 'client_mobile': 'owner_phone', 'client_email': 'owner_email', 'client_address': 'owner_address', 'client_city': 'owner_city', 'client_state': 'owner_state', 'physician_id': 'doctor_id', 'physician_first_name': 'doctor_first_name', 'physician_last_name': 'doctor_last_name', 'physician_gender': 'doctor_gender', 'physician_dob': 'doctor_dob', 'physician_mobile': 'doctor_phone', 'physician_email': 'doctor_email', 'physician_address': 'doctor_address', 'physician_city': 'doctor_city', 'physician_state': 'doctor_state', 'physician_speciality': 'doctor_specialization', 'visit_type': 'appointment_type', 'condition_code': 'diagnosis_code', 'condition_description': 'diagnosis_description', 'therapy_id': 'treatment_id', 'therapy_name': 'treatment_name', 'drug_name': 'medication_name', 'drug_dosage': 'dosage', 'invoice_ref': 'invoice_id', 'invoice_total': 'invoice_amount', 'tax_total': 'tax_amount', 'discount_total': 'discount_amount', 'payment_type': 'payment_method', 'payment_state': 'payment_status', 'insurance_name': 'insurance_provider', 'inserted_ts': 'created_timestamp', 'last_updated_ts': 'updated_timestamp'}, 
    'hospital_d': {'encounter_id': 'visit_id', 'encounter_date': 'visit_date', 'branch_id': 'hospital_id', 'branch_name': 'hospital_name', 'branch_address': 'hospital_address', 'branch_phone': 'hospital_phone', 'branch_email': 'hospital_email', 'pet_identifier': 'pet_id', 'pet_full_name': 'pet_name', 'species_name': 'species', 'breed_name': 'breed', 'gender_code': 'gender', 'birth_dt': 'birth_date', 'weight_in_kg': 'weight_kg', 'microchip_id': 'microchip_number', 'owner_identifier': 'owner_id', 'owner_first': 'owner_first_name', 'owner_last': 'owner_last_name', 'owner_gender': 'owner_gender', 'owner_birth_date': 'owner_dob', 'phone_number': 'owner_phone', 'email': 'owner_email', 'street': 'owner_address', 'city': 'owner_city', 'state': 'owner_state', 'doctor_identifier': 'doctor_id', 'doctor_first': 'doctor_first_name', 'doctor_last': 'doctor_last_name', 'doctor_gender': 'doctor_gender', 'doctor_birth_date': 'doctor_dob', 'doctor_phone_number': 'doctor_phone', 'doctor_email': 'doctor_email', 'doctor_street': 'doctor_address', 'doctor_city': 'doctor_city', 'doctor_state': 'doctor_state', 'specialization': 'doctor_specialization', 'encounter_type': 'appointment_type', 'procedure_code': 'diagnosis_code', 'procedure_description': 'diagnosis_description', 'treatment_ref': 'treatment_id', 'treatment_desc': 'treatment_name', 'prescribed_medication': 'medication_name', 'prescribed_dosage': 'dosage', 'invoice_number': 'invoice_id', 'gross_amount': 'invoice_amount', 'tax_amount': 'tax_amount', 'discount_amount': 'discount_amount', 'payment_method': 'payment_method', 'payment_status': 'payment_status', 'insurance_provider': 'insurance_provider', 'created_on': 'created_timestamp', 'updated_on': 'updated_timestamp'}, 
    'hospital_e': {'case_id': 'visit_id', 'case_date': 'visit_date', 'center_id': 'hospital_id', 'center_name': 'hospital_name', 'center_address': 'hospital_address', 'center_phone': 'hospital_phone', 'center_email': 'hospital_email', 'pet_code': 'pet_id', 'pet_nickname': 'pet_name', 'species_category': 'species', 'breed_category': 'breed', 'sex_code': 'gender', 'date_of_birth': 'birth_date', 'current_weight': 'weight_kg', 'rfid_tag': 'microchip_number', 'guardian_id': 'owner_id', 'guardian_first_name': 'owner_first_name', 'guardian_last_name': 'owner_last_name', 'guardian_gender': 'owner_gender', 'guardian_dob': 'owner_dob', 'guardian_contact': 'owner_phone', 'guardian_email': 'owner_email', 'guardian_address': 'owner_address', 'guardian_city': 'owner_city', 'guardian_state': 'owner_state', 'staff_id': 'doctor_id', 'staff_first_name': 'doctor_first_name', 'staff_last_name': 'doctor_last_name', 'staff_gender': 'doctor_gender', 'staff_dob': 'doctor_dob', 'staff_contact': 'doctor_phone', 'staff_email': 'doctor_email', 'staff_address': 'doctor_address', 'staff_city': 'doctor_city', 'staff_state': 'doctor_state', 'staff_role': 'doctor_specialization', 'case_type': 'appointment_type', 'diagnosis_id': 'diagnosis_code', 'diagnosis_text': 'diagnosis_description', 'care_plan_id': 'treatment_id', 'care_plan': 'treatment_name', 'medication': 'medication_name', 'dosage': 'dosage', 'charge_id': 'invoice_id', 'total_charge': 'invoice_amount', 'tax_charge': 'tax_amount', 'discount_charge': 'discount_amount', 'settlement_mode': 'payment_method', 'settlement_status': 'payment_status', 'insurance_provider': 'insurance_provider', 'created_ts': 'created_timestamp', 'updated_ts': 'updated_timestamp'}
}

PRIMARY_KEYS = {
    "hospital": ["hospital_id"],
    "user": ["user_id"],
    "pet": ["pet_id"],
    "visit": ["visit_id"],
    "invoice": ["invoice_id"],
}


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
    entity_columns = ENTITY_SCHEMAS[entity_name]
    df = _ensure_columns(df, entity_columns)
    if entity_name in PRIMARY_KEYS:
        df = _deduplicate(df, PRIMARY_KEYS[entity_name])

    return df

# def _deduplicate(df, primary_keys):
#     window = Window.partitionBy(*primary_keys).orderBy(desc("ingest_timestamp"))
#     return (
#         df.withColumn("rn", row_number().over(window))
#           .filter(col("rn") == 1)
#           .drop("rn")
#     )

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