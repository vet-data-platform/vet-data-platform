import random
from datetime import datetime
from io import StringIO
import os

import boto3
import pandas as pd
from faker import Faker
from dotenv import load_dotenv

load_dotenv()

s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION"),
)

fake = Faker("en_IN")

BUCKET_NAME = "vet-data-platform"
TOTAL_ROWS_PER_HOSPITAL = 50000


HOSPITAL_CONFIGS = {
    "hospital_a": {
        "hospital_id": "H001",
        "hospital_name": "Hospital A",
        "hospital_address": "12 MG Road, Bengaluru, Karnataka",
        "hospital_phone": "9876543210",
        "hospital_email": "contact@hospitala.com",
        "file_prefix": "hospital_a_export",
        "s3_folder": "hospital_a",
        "column_mapping": {
            "visit_id": "visit_id",
            "visit_date": "visit_date",
            "hospital_id": "hospital_id",
            "hospital_name": "hospital_name",
            "hospital_address": "hospital_address",
            "hospital_phone": "hospital_phone",
            "hospital_email": "hospital_email",
            "pet_id": "pet_id",
            "pet_name": "pet_name",
            "species": "species",
            "breed": "breed",
            "gender": "gender",
            "birth_date": "birth_date",
            "weight_kg": "weight_kg",
            "microchip_number": "microchip_number",
            "owner_id": "owner_id",
            "owner_first_name": "owner_first_name",
            "owner_last_name": "owner_last_name",
            "owner_gender": "owner_gender",
            "owner_dob": "owner_dob",
            "owner_phone": "owner_phone",
            "owner_email": "owner_email",
            "owner_address": "owner_address",
            "owner_city": "owner_city",
            "owner_state": "owner_state",
            "doctor_id": "doctor_id",
            "doctor_first_name": "doctor_first_name",
            "doctor_last_name": "doctor_last_name",
            "doctor_gender": "doctor_gender",
            "doctor_dob": "doctor_dob",
            "doctor_phone": "doctor_phone",
            "doctor_email": "doctor_email",
            "doctor_address": "doctor_address",
            "doctor_city": "doctor_city",
            "doctor_state": "doctor_state",
            "doctor_specialization": "doctor_specialization",
            "appointment_type": "appointment_type",
            "diagnosis_code": "diagnosis_code",
            "diagnosis_description": "diagnosis_description",
            "treatment_id": "treatment_id",
            "treatment_name": "treatment_name",
            "medication_name": "medication_name",
            "dosage": "dosage",
            "invoice_id": "invoice_id",
            "invoice_amount": "invoice_amount",
            "tax_amount": "tax_amount",
            "discount_amount": "discount_amount",
            "payment_method": "payment_method",
            "payment_status": "payment_status",
            "insurance_provider": "insurance_provider",
            "created_timestamp": "created_timestamp",
            "updated_timestamp": "updated_timestamp",
        },
    },

    "hospital_b": {
        "hospital_id": "H002",
        "hospital_name": "Hospital B",
        "hospital_address": "45 Residency Road, Bengaluru, Karnataka",
        "hospital_phone": "9876543211",
        "hospital_email": "contact@hospitalb.com",
        "file_prefix": "hospital_b_export",
        "s3_folder": "hospital_b",
        "column_mapping": {
            "visit_id": "appointment_id",
            "visit_date": "appointment_date",
            "hospital_id": "clinic_code",
            "hospital_name": "clinic_name",
            "hospital_address": "clinic_address",
            "hospital_phone": "clinic_phone",
            "hospital_email": "clinic_email",
            "pet_id": "animal_id",
            "pet_name": "animal_name",
            "species": "animal_type",
            "breed": "animal_breed",
            "gender": "sex",
            "birth_date": "dob",
            "weight_kg": "weight",
            "microchip_number": "chip_no",
            "owner_id": "customer_id",
            "owner_first_name": "customer_first_name",
            "owner_last_name": "customer_last_name",
            "owner_gender": "customer_gender",
            "owner_dob": "customer_dob",
            "owner_phone": "contact_number",
            "owner_email": "email_address",
            "owner_address": "customer_address",
            "owner_city": "customer_city",
            "owner_state": "customer_state",
            "doctor_id": "vet_id",
            "doctor_first_name": "vet_first_name",
            "doctor_last_name": "vet_last_name",
            "doctor_gender": "vet_gender",
            "doctor_dob": "vet_dob",
            "doctor_phone": "vet_contact_number",
            "doctor_email": "vet_email_address",
            "doctor_address": "vet_address",
            "doctor_city": "vet_city",
            "doctor_state": "vet_state",
            "doctor_specialization": "speciality",
            "appointment_type": "appointment_category",
            "diagnosis_code": "disease_code",
            "diagnosis_description": "disease_desc",
            "treatment_id": "procedure_id",
            "treatment_name": "procedure_name",
            "medication_name": "medicine",
            "dosage": "medicine_dose",
            "invoice_id": "bill_id",
            "invoice_amount": "bill_amount",
            "tax_amount": "gst_amount",
            "discount_amount": "discount",
            "payment_method": "pay_mode",
            "payment_status": "payment_flag",
            "insurance_provider": "insurance_company",
            "created_timestamp": "created_at",
            "updated_timestamp": "modified_at",
        },
    },

    "hospital_c": {
        "hospital_id": "H003",
        "hospital_name": "Hospital C",
        "hospital_address": "78 Indiranagar, Bengaluru, Karnataka",
        "hospital_phone": "9876543212",
        "hospital_email": "contact@hospitalc.com",
        "file_prefix": "hospital_c_export",
        "s3_folder": "hospital_c",
        "column_mapping": {
            "visit_id": "record_id",
            "visit_date": "visit_timestamp",
            "hospital_id": "facility_id",
            "hospital_name": "facility_name",
            "hospital_address": "facility_address",
            "hospital_phone": "facility_phone",
            "hospital_email": "facility_email",
            "pet_id": "patient_id",
            "pet_name": "patient_name",
            "species": "patient_species",
            "breed": "patient_breed",
            "gender": "patient_gender",
            "birth_date": "patient_dob",
            "weight_kg": "body_weight",
            "microchip_number": "rfid_number",
            "owner_id": "owner_ref",
            "owner_first_name": "client_first_name",
            "owner_last_name": "client_last_name",
            "owner_gender": "client_gender",
            "owner_dob": "client_dob",
            "owner_phone": "client_mobile",
            "owner_email": "client_email",
            "owner_address": "client_address",
            "owner_city": "client_city",
            "owner_state": "client_state",
            "doctor_id": "physician_id",
            "doctor_first_name": "physician_first_name",
            "doctor_last_name": "physician_last_name",
            "doctor_gender": "physician_gender",
            "doctor_dob": "physician_dob",
            "doctor_phone": "physician_mobile",
            "doctor_email": "physician_email",
            "doctor_address": "physician_address",
            "doctor_city": "physician_city",
            "doctor_state": "physician_state",
            "doctor_specialization": "physician_speciality",
            "appointment_type": "visit_type",
            "diagnosis_code": "condition_code",
            "diagnosis_description": "condition_description",
            "treatment_id": "therapy_id",
            "treatment_name": "therapy_name",
            "medication_name": "drug_name",
            "dosage": "drug_dosage",
            "invoice_id": "invoice_ref",
            "invoice_amount": "invoice_total",
            "tax_amount": "tax_total",
            "discount_amount": "discount_total",
            "payment_method": "payment_type",
            "payment_status": "payment_state",
            "insurance_provider": "insurance_name",
            "created_timestamp": "inserted_ts",
            "updated_timestamp": "last_updated_ts",
        },
    },

    "hospital_d": {
        "hospital_id": "H004",
        "hospital_name": "Hospital D",
        "hospital_address": "22 Jayanagar, Bengaluru, Karnataka",
        "hospital_phone": "9876543213",
        "hospital_email": "contact@hospitald.com",
        "file_prefix": "hospital_d_export",
        "s3_folder": "hospital_d",
        "column_mapping": {
            "visit_id": "encounter_id",
            "visit_date": "encounter_date",
            "hospital_id": "branch_id",
            "hospital_name": "branch_name",
            "hospital_address": "branch_address",
            "hospital_phone": "branch_phone",
            "hospital_email": "branch_email",
            "pet_id": "pet_identifier",
            "pet_name": "pet_full_name",
            "species": "species_name",
            "breed": "breed_name",
            "gender": "gender_code",
            "birth_date": "birth_dt",
            "weight_kg": "weight_in_kg",
            "microchip_number": "microchip_id",
            "owner_id": "owner_identifier",
            "owner_first_name": "owner_first",
            "owner_last_name": "owner_last",
            "owner_gender": "owner_gender",
            "owner_dob": "owner_birth_date",
            "owner_phone": "phone_number",
            "owner_email": "email",
            "owner_address": "street",
            "owner_city": "city",
            "owner_state": "state",
            "doctor_id": "doctor_identifier",
            "doctor_first_name": "doctor_first",
            "doctor_last_name": "doctor_last",
            "doctor_gender": "doctor_gender",
            "doctor_dob": "doctor_birth_date",
            "doctor_phone": "doctor_phone_number",
            "doctor_email": "doctor_email",
            "doctor_address": "doctor_street",
            "doctor_city": "doctor_city",
            "doctor_state": "doctor_state",
            "doctor_specialization": "specialization",
            "appointment_type": "encounter_type",
            "diagnosis_code": "procedure_code",
            "diagnosis_description": "procedure_description",
            "treatment_id": "treatment_ref",
            "treatment_name": "treatment_desc",
            "medication_name": "prescribed_medication",
            "dosage": "prescribed_dosage",
            "invoice_id": "invoice_number",
            "invoice_amount": "gross_amount",
            "tax_amount": "tax_amount",
            "discount_amount": "discount_amount",
            "payment_method": "payment_method",
            "payment_status": "payment_status",
            "insurance_provider": "insurance_provider",
            "created_timestamp": "created_on",
            "updated_timestamp": "updated_on",
        },
    },

    "hospital_e": {
        "hospital_id": "H005",
        "hospital_name": "Hospital E",
        "hospital_address": "90 Whitefield, Bengaluru, Karnataka",
        "hospital_phone": "9876543214",
        "hospital_email": "contact@hospitale.com",
        "file_prefix": "hospital_e_export",
        "s3_folder": "hospital_e",
        "column_mapping": {
            "visit_id": "case_id",
            "visit_date": "case_date",
            "hospital_id": "center_id",
            "hospital_name": "center_name",
            "hospital_address": "center_address",
            "hospital_phone": "center_phone",
            "hospital_email": "center_email",
            "pet_id": "pet_code",
            "pet_name": "pet_nickname",
            "species": "species_category",
            "breed": "breed_category",
            "gender": "sex_code",
            "birth_date": "date_of_birth",
            "weight_kg": "current_weight",
            "microchip_number": "rfid_tag",
            "owner_id": "guardian_id",
            "owner_first_name": "guardian_first_name",
            "owner_last_name": "guardian_last_name",
            "owner_gender": "guardian_gender",
            "owner_dob": "guardian_dob",
            "owner_phone": "guardian_contact",
            "owner_email": "guardian_email",
            "owner_address": "guardian_address",
            "owner_city": "guardian_city",
            "owner_state": "guardian_state",
            "doctor_id": "staff_id",
            "doctor_first_name": "staff_first_name",
            "doctor_last_name": "staff_last_name",
            "doctor_gender": "staff_gender",
            "doctor_dob": "staff_dob",
            "doctor_phone": "staff_contact",
            "doctor_email": "staff_email",
            "doctor_address": "staff_address",
            "doctor_city": "staff_city",
            "doctor_state": "staff_state",
            "doctor_specialization": "staff_role",
            "appointment_type": "case_type",
            "diagnosis_code": "diagnosis_id",
            "diagnosis_description": "diagnosis_text",
            "treatment_id": "care_plan_id",
            "treatment_name": "care_plan",
            "medication_name": "medication",
            "dosage": "dosage",
            "invoice_id": "charge_id",
            "invoice_amount": "total_charge",
            "tax_amount": "tax_charge",
            "discount_amount": "discount_charge",
            "payment_method": "settlement_mode",
            "payment_status": "settlement_status",
            "insurance_provider": "insurance_provider",
            "created_timestamp": "created_ts",
            "updated_timestamp": "updated_ts",
        },
    },
}


def generate_base_data(config: dict, rows: int) -> pd.DataFrame:
    hospital_id = config["hospital_id"]

    hospital = {
        "hospital_id": config["hospital_id"],
        "hospital_name": config["hospital_name"],
        "hospital_address": config["hospital_address"],
        "hospital_phone": config["hospital_phone"],
        "hospital_email": config["hospital_email"],
    }

    species_list = ["Dog", "Cat", "Rabbit", "Bird"]
    breeds = {
        "Dog": ["Labrador", "Beagle", "Pug", "German Shepherd"],
        "Cat": ["Persian", "Siamese", "Maine Coon"],
        "Rabbit": ["Dutch", "Lionhead"],
        "Bird": ["Parrot", "Cockatiel"],
    }

    appointment_types = ["General Checkup", "Vaccination", "Emergency", "Surgery"]
    payment_methods = ["Cash", "Card", "UPI", "Insurance"]
    payment_statuses = ["Paid", "Pending", "Failed"]
    specializations = ["General", "Surgery", "Dermatology", "Orthopedics"]

    diagnosis_list = [
        ("D101", "Fever"),
        ("D102", "Skin Allergy"),
        ("D103", "Infection"),
        ("D104", "Injury"),
        ("D105", "Dental Issue"),
    ]

    treatment_list = [
        "Vaccination",
        "Medication",
        "Surgery",
        "Bandaging",
        "Dental Cleaning",
    ]

    owners = []
    for i in range(1, 5001):
        owners.append({
            "owner_id": f"{hospital_id}_O{i}",
            "owner_first_name": fake.first_name(),
            "owner_last_name": fake.last_name(),
            "owner_gender": random.choice(["Male", "Female"]),
            "owner_dob": fake.date_between(start_date="-70y", end_date="-18y"),
            "owner_phone": fake.msisdn()[:10],
            "owner_email": fake.email(),
            "owner_address": fake.street_address().replace("\n", ", "),
            "owner_city": fake.city(),
            "owner_state": fake.state(),
        })

    doctors = []
    for i in range(1, 101):
        doctors.append({
            "doctor_id": f"{hospital_id}_D{i}",
            "doctor_first_name": fake.first_name(),
            "doctor_last_name": fake.last_name(),
            "doctor_gender": random.choice(["Male", "Female"]),
            "doctor_dob": fake.date_between(start_date="-65y", end_date="-25y"),
            "doctor_phone": fake.msisdn()[:10],
            "doctor_email": fake.email(),
            "doctor_address": fake.street_address().replace("\n", ", "),
            "doctor_city": fake.city(),
            "doctor_state": fake.state(),
            "doctor_specialization": random.choice(specializations),
        })

    pets = []
    for i in range(1, 10001):
        owner = random.choice(owners)
        species = random.choice(species_list)

        pets.append({
            "pet_id": f"{hospital_id}_P{i}",
            "pet_name": fake.first_name(),
            "species": species,
            "breed": random.choice(breeds[species]),
            "gender": random.choice(["Male", "Female"]),
            "birth_date": fake.date_between(start_date="-15y", end_date="-1y"),
            "weight_kg": round(random.uniform(1, 45), 2),
            "microchip_number": fake.uuid4(),
            "owner_id": owner["owner_id"],
            "owner_first_name": owner["owner_first_name"],
            "owner_last_name": owner["owner_last_name"],
            "owner_gender": owner["owner_gender"],
            "owner_dob": owner["owner_dob"],
            "owner_phone": owner["owner_phone"],
            "owner_email": owner["owner_email"],
            "owner_address": owner["owner_address"],
            "owner_city": owner["owner_city"],
            "owner_state": owner["owner_state"],
        })

    data = []

    for i in range(1, rows + 1):
        pet = random.choice(pets)
        doctor = random.choice(doctors)

        invoice_amount = round(random.uniform(500, 15000), 2)
        diagnosis_code, diagnosis_description = random.choice(diagnosis_list)

        data.append({
            "visit_id": f"{hospital_id}_V{i}",
            "visit_date": fake.date_between(start_date="-2y", end_date="today"),
            **hospital,
            **pet,
            "doctor_id": doctor["doctor_id"],
            "doctor_first_name": doctor["doctor_first_name"],
            "doctor_last_name": doctor["doctor_last_name"],
            "doctor_gender": doctor["doctor_gender"],
            "doctor_dob": doctor["doctor_dob"],
            "doctor_phone": doctor["doctor_phone"],
            "doctor_email": doctor["doctor_email"],
            "doctor_address": doctor["doctor_address"],
            "doctor_city": doctor["doctor_city"],
            "doctor_state": doctor["doctor_state"],
            "doctor_specialization": doctor["doctor_specialization"],
            "appointment_type": random.choice(appointment_types),
            "diagnosis_code": diagnosis_code,
            "diagnosis_description": diagnosis_description,
            "treatment_id": f"{hospital_id}_T{i}",
            "treatment_name": random.choice(treatment_list),
            "medication_name": random.choice(["MedA", "MedB", "MedC"]),
            "dosage": random.choice(["5mg", "10mg", "20mg"]),
            "invoice_id": f"{hospital_id}_I{i}",
            "invoice_amount": invoice_amount,
            "tax_amount": round(invoice_amount * 0.18, 2),
            "discount_amount": round(random.uniform(0, 500), 2),
            "payment_method": random.choice(payment_methods),
            "payment_status": random.choice(payment_statuses),
            "insurance_provider": random.choice(["None", "PetCare", "VetSecure"]),
            "created_timestamp": datetime.now(),
            "updated_timestamp": datetime.now(),
        })

    return pd.DataFrame(data)

def inject_controlled_messy_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df.loc[df.sample(frac=0.02).index, "pet_name"] = None
    df.loc[df.sample(frac=0.02).index, "owner_email"] = "invalid_email"
    df.loc[df.sample(frac=0.01).index, "invoice_amount"] *= -1
    df.loc[df.sample(frac=0.01).index, "doctor_id"] = None

    duplicates = df.sample(frac=0.02)
    df = pd.concat([df, duplicates], ignore_index=True)

    return df


def apply_hospital_schema(df: pd.DataFrame, column_mapping: dict) -> pd.DataFrame:
    return df.rename(columns=column_mapping)


def build_s3_key(hospital_folder: str, file_prefix: str) -> str:
    today = datetime.now()
    date_folder = today.strftime("%Y-%m-%d")
    timestamp = today.strftime("%Y%m%d_%H%M%S")
    file_name = f"{file_prefix}_{timestamp}_001.csv"

    return f"raw/{hospital_folder}/{date_folder}/{file_name}"


def upload_to_s3(df: pd.DataFrame, hospital_folder: str, file_prefix: str) -> None:
    s3_key = build_s3_key(hospital_folder, file_prefix)

    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)

    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=csv_buffer.getvalue(),
    )
def generate_for_hospital(config: dict) -> None:
    base_df = generate_base_data(
        config=config,
        rows=TOTAL_ROWS_PER_HOSPITAL,
    )

    messy_df = inject_controlled_messy_data(base_df)

    final_df = apply_hospital_schema(
        messy_df,
        config["column_mapping"],
    )

    upload_to_s3(
        final_df,
        config["s3_folder"],
        config["file_prefix"],
    )

def main() -> None:
    for config in HOSPITAL_CONFIGS.values():
        generate_for_hospital(config)


if __name__ == "__main__":
    main()