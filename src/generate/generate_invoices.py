import random
from datetime import datetime

import pandas as pd
from faker import Faker

fake = Faker("en_IN")


def generate_invoices(
    visit_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Generates Bronze Invoice data.

    One invoice per visit.
    """

    payment_methods = [
        "Cash",
        "Card",
        "UPI",
        "Insurance",
    ]

    payment_statuses = [
        "Paid",
        "Pending",
        "Cancelled",
    ]

    insurance_providers = [
        "None",
        "PetCare",
        "VetSecure",
        "AnimalHealth",
    ]

    invoices = []

    invoice_counter = 1

    for _, visit in visit_df.iterrows():

        invoice_amount = round(
            random.uniform(500, 15000),
            2,
        )

        tax_amount = round(
            invoice_amount * 0.18,
            2,
        )

        discount_amount = round(
            random.uniform(0, 1000),
            2,
        )

        net_amount = round(
            invoice_amount + tax_amount - discount_amount,
            2,
        )

        payment_method = random.choice(
            payment_methods
        )

        insurance_provider = random.choice(
            insurance_providers
        )

        if payment_method != "Insurance":
            insurance_provider = "None"

        invoices.append(
            {

                "invoice_id": f"I{invoice_counter:08}",

                # FK
                "visit_id": visit["visit_id"],

                # FK
                "hospital_id": visit["hospital_id"],

                "invoice_date": visit["visit_date"],

                "invoice_amount": invoice_amount,

                "tax_amount": tax_amount,

                "discount_amount": discount_amount,

                "net_amount": net_amount,

                "payment_method": payment_method,

                "payment_status": random.choice(
                    payment_statuses
                ),

                "insurance_provider": insurance_provider,

                # Bronze Metadata

                "source_system": visit["source_system"],

                "ingest_date": datetime.now().date(),

                "ingest_timestamp": datetime.now(),

                "file_name": f"{visit['source_system']}.csv",

                "record_hash": fake.uuid4(),
            }
        )

        invoice_counter += 1

    return pd.DataFrame(invoices)
