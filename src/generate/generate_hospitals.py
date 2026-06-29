import random
from datetime import datetime

import pandas as pd
from faker import Faker

fake = Faker("en_IN")


def generate_hospitals(num_hospitals: int = 5) -> pd.DataFrame:
    """
    Generates Bronze Hospital data.
    """

    hospital_types = [
        "General Hospital",
        "Veterinary Clinic",
        "Emergency Center",
        "Specialty Hospital"
    ]

    hospitals = []

    for i in range(1, num_hospitals + 1):

        hospital = {
            "hospital_id": f"H{i:03}",
            "hospital_name": f"{fake.city()} Vet Hospital",
            "hospital_type": random.choice(hospital_types),

            "address": fake.street_address().replace("\n", ", "),
            "city": fake.city(),
            "state": fake.state(),
            "country": "India",
            "postal_code": fake.postcode(),

            "phone": fake.msisdn()[:10],
            "email": f"contact{i}@hospital.com",

            # Bronze Metadata
            "source_system": f"hospital_{chr(96+i)}",
            "ingest_date": datetime.now().date(),
            "ingest_timestamp": datetime.now(),
            "file_name": f"hospital_{chr(96+i)}.csv",
            "record_hash": fake.uuid4()
        }

        hospitals.append(hospital)

    return pd.DataFrame(hospitals)
