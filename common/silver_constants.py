SILVER_TABLE_CONFIG = {
    "hospital_master": {
        "target_table": "silver_hospital_master",
        "source_table": "bronze_hospital",
        "table_type": "dimension",
        "primary_key": "hospital_key",
        "business_key": "hospital_id",
        "history_tracking": "type_1",
        "columns": [
            "hospital_key",
            "hospital_id",
            "hospital_name",
            "hospital_address",
            "hospital_phone",
            "hospital_email",
            "source_system",
            "ingest_timestamp"
        ],
        "foreign_keys": {}
    },

    "owner_master": {
        "target_table": "silver_owner_master",
        "source_table": "bronze_user",
        "table_type": "dimension",
        "primary_key": "owner_key",
        "business_key": "owner_id",
        "history_tracking": "type_2",
        "columns": [
            "owner_key",
            "owner_id",
            "first_name",
            "last_name",
            "gender",
            "dob",
            "phone",
            "email",
            "address",
            "city",
            "state",
            "source_system",
            "ingest_timestamp"
        ],
        "foreign_keys": {}
    },

    "pet_master": {
        "target_table": "silver_pet_master",
        "source_table": "bronze_pet",
        "table_type": "dimension",
        "primary_key": "pet_key",
        "business_key": "pet_id",
        "history_tracking": "type_2",
        "columns": [
            "pet_key",
            "pet_id",
            "pet_name",
            "species",
            "breed",
            "gender",
            "birth_date",
            "weight_kg",
            "microchip_number",
            "owner_key",
            "hospital_key",
            "source_system",
            "ingest_timestamp"
        ],
        "foreign_keys": {
            "owner_key": {
                "reference_table": "silver_owner_master",
                "reference_key": "owner_key",
                "join_key": "owner_id"
            },
            "hospital_key": {
                "reference_table": "silver_hospital_master",
                "reference_key": "hospital_key",
                "join_key": "hospital_id"
            }
        }
    },

    "doctor_master": {
        "target_table": "silver_doctor_master",
        "source_table": "bronze_user",
        "table_type": "dimension",
        "primary_key": "doctor_key",
        "business_key": "doctor_id",
        "history_tracking": "type_2",
        "columns": [
            "doctor_key",
            "doctor_id",
            "doctor_name",
            "gender",
            "dob",
            "phone",
            "email",
            "address",
            "city",
            "state",
            "specialization",
            "hospital_key",
            "source_system",
            "ingest_timestamp"
        ],
        "foreign_keys": {
            "hospital_key": {
                "reference_table": "silver_hospital_master",
                "reference_key": "hospital_key",
                "join_key": "hospital_id"
            }
        }
    },

    "medication_master": {
        "target_table": "silver_medication_master",
        "source_table": "bronze_visit",
        "table_type": "lookup",
        "primary_key": "medication_key",
        "business_key": "medication_id",
        "history_tracking": "type_1",
        "columns": [
            "medication_key",
            "medication_id",
            "medication_name",
            "dosage",
            "source_system",
            "ingest_timestamp"
        ],
        "foreign_keys": {}
    },

    "visit_fact": {
        "target_table": "silver_visit_fact",
        "source_table": "bronze_visit",
        "table_type": "fact",
        "primary_key": "visit_key",
        "business_key": "visit_id",
        "history_tracking": "none",
        "columns": [
            "visit_key",
            "visit_id",
            "visit_date",
            "pet_key",
            "doctor_key",
            "hospital_key",
            "appointment_type",
            "diagnosis_code",
            "diagnosis_description",
            "source_system",
            "ingest_timestamp"
        ],
        "foreign_keys": {
            "pet_key": {
                "reference_table": "silver_pet_master",
                "reference_key": "pet_key",
                "join_key": "pet_id"
            },
            "doctor_key": {
                "reference_table": "silver_doctor_master",
                "reference_key": "doctor_key",
                "join_key": "doctor_id"
            },
            "hospital_key": {
                "reference_table": "silver_hospital_master",
                "reference_key": "hospital_key",
                "join_key": "hospital_id"
            }
        }
    },

    "treatment_fact": {
        "target_table": "silver_treatment_fact",
        "source_table": "bronze_visit",
        "table_type": "fact",
        "primary_key": "treatment_key",
        "business_key": "treatment_id",
        "history_tracking": "none",
        "columns": [
            "treatment_key",
            "treatment_id",
            "visit_key",
            "medication_key",
            "treatment_name",
            "treatment_category",
            "source_system",
            "ingest_timestamp"
        ],
        "foreign_keys": {
            "visit_key": {
                "reference_table": "silver_visit_fact",
                "reference_key": "visit_key",
                "join_key": "visit_id"
            },
            "medication_key": {
                "reference_table": "silver_medication_master",
                "reference_key": "medication_key",
                "join_key": "medication_id"
            }
        }
    },

    "invoice_fact": {
        "target_table": "silver_invoice_fact",
        "source_table": "bronze_invoice",
        "table_type": "fact",
        "primary_key": "invoice_key",
        "business_key": "invoice_id",
        "history_tracking": "none",
        "columns": [
            "invoice_key",
            "invoice_id",
            "visit_key",
            "hospital_key",
            "invoice_amount",
            "tax_amount",
            "discount_amount",
            "net_amount",
            "payment_method",
            "payment_status",
            "insurance_provider",
            "source_system",
            "ingest_timestamp"
        ],
        "foreign_keys": {
            "visit_key": {
                "reference_table": "silver_visit_fact",
                "reference_key": "visit_key",
                "join_key": "visit_id"
            },
            "hospital_key": {
                "reference_table": "silver_hospital_master",
                "reference_key": "hospital_key",
                "join_key": "hospital_id"
            }
        }
    }
}