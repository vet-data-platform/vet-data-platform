import random
import sys
import os
from datetime import datetime
from io import StringIO

import boto3
import pandas as pd
from faker import Faker
from dotenv import load_dotenv

# Make common/ importable when running this script from any directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from common.constants import HOSPITAL_COLUMN_MAP

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
    },
    "hospital_b": {
        "hospital_id": "H002",
        "hospital_name": "Hospital B",
        "hospital_address": "45 Residency Road, Bengaluru, Karnataka",
        "hospital_phone": "9876543211",
        "hospital_email": "contact@hospitalb.com",
        "file_prefix": "hospital_b_export",
        "s3_folder": "hospital_b",
    },
    "hospital_c": {
        "hospital_id": "H003",
        "hospital_name": "Hospital C",
        "hospital_address": "78 Indiranagar, Bengaluru, Karnataka",
        "hospital_phone": "9876543212",
        "hospital_email": "contact@hospitalc.com",
        "file_prefix": "hospital_c_export",
        "s3_folder": "hospital_c",
    },
    "hospital_d": {
        "hospital_id": "H004",
        "hospital_name": "Hospital D",
        "hospital_address": "22 Jayanagar, Bengaluru, Karnataka",
        "hospital_phone": "9876543213",
        "hospital_email": "contact@hospitald.com",
        "file_prefix": "hospital_d_export",
        "s3_folder": "hospital_d",
    },
    "hospital_e": {
        "hospital_id": "H005",
        "hospital_name": "Hospital E",
        "hospital_address": "90 Whitefield, Bengaluru, Karnataka",
        "hospital_phone": "9876543214",
        "hospital_email": "contact@hospitale.com",
        "file_prefix": "hospital_e_export",
        "s3_folder": "hospital_e",
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
    return f"raw/{hospital_folder}/{date_folder}/{file_prefix}_{timestamp}_001.csv"


def upload_to_s3(df: pd.DataFrame, hospital_folder: str, file_prefix: str) -> None:
    s3_key = build_s3_key(hospital_folder, file_prefix)
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=csv_buffer.getvalue(),
    )
    print(f"    Uploaded → s3://{BUCKET_NAME}/{s3_key}")


def generate_for_hospital(hospital_key: str, config: dict) -> None:
    print(f"[{hospital_key}] Generating {TOTAL_ROWS_PER_HOSPITAL} rows...")
    base_df = generate_base_data(config=config, rows=TOTAL_ROWS_PER_HOSPITAL)

    print(f"[{hospital_key}] Injecting messy data...")
    messy_df = inject_controlled_messy_data(base_df)

    # Derive column mapping from constants — inverts standard→source so generator
    # produces CSVs with each hospital's native column names, matching what the
    # bronze loader expects to rename back.
    column_mapping = {v: k for k, v in HOSPITAL_COLUMN_MAP[hospital_key].items()}
    final_df = apply_hospital_schema(messy_df, column_mapping)

    upload_to_s3(final_df, config["s3_folder"], config["file_prefix"])
    print(f"[{hospital_key}] Done. {len(final_df)} rows uploaded.\n")


def main() -> None:
    for hospital_key, config in HOSPITAL_CONFIGS.items():
        generate_for_hospital(hospital_key, config)


if __name__ == "__main__":
    main()
