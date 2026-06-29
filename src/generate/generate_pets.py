import random
from datetime import datetime

import pandas as pd
from faker import Faker

fake = Faker("en_IN")


def generate_pets(
    user_df: pd.DataFrame,
    max_pets_per_owner: int = 3,
) -> pd.DataFrame:
    """
    Generates Bronze Pet data.

    Only Owners can own pets.
    One owner can have multiple pets.
    """

    species_breeds = {
        "Dog": [
            "Labrador",
            "Golden Retriever",
            "German Shepherd",
            "Beagle",
            "Pug",
        ],
        "Cat": [
            "Persian",
            "Siamese",
            "Maine Coon",
            "British Shorthair",
        ],
        "Rabbit": [
            "Dutch",
            "Lionhead",
            "Mini Lop",
        ],
        "Bird": [
            "Parrot",
            "Cockatiel",
            "Budgie",
        ],
    }

    colors = [
        "Black",
        "Brown",
        "White",
        "Golden",
        "Grey",
        "Cream",
        "Mixed",
    ]

    vaccination_status = [
        "Vaccinated",
        "Pending",
        "Overdue",
    ]

    pets = []

    pet_counter = 1

    owners = user_df[
        user_df["user_type"] == "Owner"
    ]

    for _, owner in owners.iterrows():

        number_of_pets = random.randint(
            1,
            max_pets_per_owner,
        )

        for _ in range(number_of_pets):

            species = random.choice(
                list(species_breeds.keys())
            )

            pets.append(
                {
                    "pet_id": f"P{pet_counter:06}",

                    # FK to bronze_user
                    "user_id": owner["user_id"],

                    # FK to bronze_hospital
                    "hospital_id": owner["hospital_id"],

                    "pet_name": fake.first_name(),

                    "species": species,

                    "breed": random.choice(
                        species_breeds[species]
                    ),

                    "gender": random.choice(
                        ["Male", "Female"]
                    ),

                    "birth_date": fake.date_between(
                        start_date="-15y",
                        end_date="-3m",
                    ),

                    "weight_kg": round(
                        random.uniform(0.5, 45),
                        2,
                    ),

                    "color": random.choice(colors),

                    "microchip_number": fake.uuid4(),

                    "vaccination_status": random.choice(
                        vaccination_status
                    ),

                    # Bronze Metadata

                    "source_system": owner["source_system"],

                    "ingest_date": datetime.now().date(),

                    "ingest_timestamp": datetime.now(),

                    "file_name": f"{owner['source_system']}.csv",

                    "record_hash": fake.uuid4(),
                }
            )

            pet_counter += 1

    return pd.DataFrame(pets)

