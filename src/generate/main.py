from io import StringIO
from datetime import datetime

import boto3

from generate_hospitals import generate_hospitals
from generate_users import generate_users
from generate_pets import generate_pets
from generate_visits import generate_visits
from generate_invoices import generate_invoices


# ==========================================
# CONFIGURATION
# ==========================================

BUCKET_NAME = "vet-data-platform"

s3_client = boto3.client("s3")


# ==========================================
# S3 Upload Utility
# ==========================================

def upload_dataframe_to_s3(
    df,
    hospital_folder,
    file_name,
):
    """
    Uploads a dataframe as CSV directly to S3.
    """

    today = datetime.now()

    date_folder = today.strftime("%Y-%m-%d")

    s3_key = (
        f"raw/"
        f"{hospital_folder}/"
        f"{date_folder}/"
        f"{file_name}"
    )

    csv_buffer = StringIO()

    df.to_csv(
        csv_buffer,
        index=False,
    )

    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=csv_buffer.getvalue(),
    )

    print(f"Uploaded : {s3_key}")


# ==========================================
# MAIN
# ==========================================

def main():

    print("Generating Hospitals...")
    hospital_df = generate_hospitals()

    print("Generating Users...")
    user_df = generate_users(hospital_df)

    print("Generating Pets...")
    pet_df = generate_pets(user_df)

    print("Generating Visits...")
    visit_df = generate_visits(
        pet_df,
        user_df,
    )

    print("Generating Invoices...")
    invoice_df = generate_invoices(
        visit_df,
    )

    print("Uploading files to S3...\n")

    hospitals = hospital_df["source_system"].unique()

    for hospital in hospitals:

        upload_dataframe_to_s3(
            hospital_df[
                hospital_df["source_system"] == hospital
            ],
            hospital,
            "bronze_hospital.csv",
        )

        upload_dataframe_to_s3(
            user_df[
                user_df["source_system"] == hospital
            ],
            hospital,
            "bronze_user.csv",
        )

        upload_dataframe_to_s3(
            pet_df[
                pet_df["source_system"] == hospital
            ],
            hospital,
            "bronze_pet.csv",
        )

        upload_dataframe_to_s3(
            visit_df[
                visit_df["source_system"] == hospital
            ],
            hospital,
            "bronze_visit.csv",
        )

        upload_dataframe_to_s3(
            invoice_df[
                invoice_df["source_system"] == hospital
            ],
            hospital,
            "bronze_invoice.csv",
        )

    print("\nAll Bronze files uploaded successfully.")


# ==========================================
# ENTRY POINT
# ==========================================

if __name__ == "__main__":
    main()