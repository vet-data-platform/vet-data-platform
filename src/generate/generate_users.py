import random
from datetime import datetime

import pandas as pd
from faker import Faker

fake = Faker("en_IN")


def generate_users(
    hospital_df: pd.DataFrame,
    doctors_per_hospital: int = 20,
    owners_per_hospital: int = 500,
) -> pd.DataFrame:
    """
    Generates Bronze User data.

    Contains both Doctors and Owners.
    """

    specializations = [
        "General",
        "Surgery",
        "Dermatology",
        "Orthopedics",
        "Dentistry",
        "Cardiology",
    ]

    users = []

    user_counter = 1

    for _, hospital in hospital_df.iterrows():

        hospital_id = hospital["hospital_id"]
        source_system = hospital["source_system"]

        # -------------------------
        # Generate Doctors
        # -------------------------

        for _ in range(doctors_per_hospital):

            users.append(
                {
                    "user_id": f"U{user_counter:06}",
                    "user_type": "Doctor",

                    "first_name": fake.first_name(),
                    "last_name": fake.last_name(),

                    "gender": random.choice(
                        ["Male", "Female"]
                    ),

                    "dob": fake.date_of_birth(
                        minimum_age=28,
                        maximum_age=65,
                    ),

                    "email": fake.email(),
                    "phone": fake.msisdn()[:10],

                    "address": fake.street_address().replace("\n", ", "),
                    "city": fake.city(),
                    "state": fake.state(),
                    "postal_code": fake.postcode(),

                    "specialization": random.choice(
                        specializations
                    ),

                    "license_number": f"LIC-{fake.random_number(digits=6)}",

                    "hospital_id": hospital_id,

                    # Bronze Metadata

                    "source_system": source_system,
                    "ingest_date": datetime.now().date(),
                    "ingest_timestamp": datetime.now(),
                    "file_name": f"{source_system}.csv",
                    "record_hash": fake.uuid4(),
                }
            )

            user_counter += 1

        # -------------------------
        # Generate Owners
        # -------------------------

        for _ in range(owners_per_hospital):

            users.append(
                {
                    "user_id": f"U{user_counter:06}",
                    "user_type": "Owner",

                    "first_name": fake.first_name(),
                    "last_name": fake.last_name(),

                    "gender": random.choice(
                        ["Male", "Female"]
                    ),

                    "dob": fake.date_of_birth(
                        minimum_age=18,
                        maximum_age=80,
                    ),

                    "email": fake.email(),
                    "phone": fake.msisdn()[:10],

                    "address": fake.street_address().replace("\n", ", "),
                    "city": fake.city(),
                    "state": fake.state(),
                    "postal_code": fake.postcode(),

                    "specialization": None,
                    "license_number": None,

                    "hospital_id": hospital_id,

                    # Bronze Metadata

                    "source_system": source_system,
                    "ingest_date": datetime.now().date(),
                    "ingest_timestamp": datetime.now(),
                    "file_name": f"{source_system}.csv",
                    "record_hash": fake.uuid4(),
                }
            )

            user_counter += 1

    return pd.DataFrame(users)

