import random
from datetime import datetime

import pandas as pd
from faker import Faker

fake = Faker("en_IN")


def generate_visits(
    pet_df: pd.DataFrame,
    user_df: pd.DataFrame,
    max_visits_per_pet: int = 5,
) -> pd.DataFrame:
    """
    Generates Bronze Visit data.

    Each visit:
        - belongs to one pet
        - is treated by one doctor
        - occurs at the same hospital as the pet
    """

    appointment_types = [
        "General Checkup",
        "Vaccination",
        "Emergency",
        "Surgery",
        "Follow-up",
    ]

    diagnoses = [
        "Fever",
        "Skin Allergy",
        "Ear Infection",
        "Dental Disease",
        "Fracture",
        "Vaccination",
        "Digestive Issue",
    ]

    visit_statuses = [
        "Completed",
        "Scheduled",
        "Cancelled",
    ]

    visits = []

    visit_counter = 1

    for _, pet in pet_df.iterrows():

        hospital_id = pet["hospital_id"]

        doctors = user_df[
            (user_df["hospital_id"] == hospital_id)
            & (user_df["user_type"] == "Doctor")
        ]

        if doctors.empty:
            continue

        number_of_visits = random.randint(
            1,
            max_visits_per_pet,
        )

        for _ in range(number_of_visits):

            doctor = doctors.sample(1).iloc[0]

            visit_date = fake.date_between(
                start_date="-2y",
                end_date="today",
            )

            visits.append(
                {

                    "visit_id": f"V{visit_counter:08}",

                    # FK
                    "pet_id": pet["pet_id"],

                    # FK -> bronze_user
                    "doctor_user_id": doctor["user_id"],

                    # FK
                    "hospital_id": hospital_id,

                    "visit_date": visit_date,

                    "visit_time": fake.time(),

                    "appointment_type": random.choice(
                        appointment_types
                    ),

                    "diagnosis": random.choice(
                        diagnoses
                    ),

                    "symptoms": fake.sentence(
                        nb_words=8
                    ),

                    "treatment_notes": fake.paragraph(
                        nb_sentences=2
                    ),

                    "visit_status": random.choice(
                        visit_statuses
                    ),

                    # Bronze Metadata

                    "source_system": pet["source_system"],

                    "ingest_date": datetime.now().date(),

                    "ingest_timestamp": datetime.now(),

                    "file_name": f"{pet['source_system']}.csv",

                    "record_hash": fake.uuid4(),
                }
            )

            visit_counter += 1

    return pd.DataFrame(visits)

