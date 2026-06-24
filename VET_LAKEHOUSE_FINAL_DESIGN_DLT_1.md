
### ARCHITECTURE OVERVIEW

Bronze (raw CSVs in DBFS) → Delta Live Tables (DLT) Bronze pipeline → DLT Silver pipeline (masters facts) → Gold (analytics). DLT provides declarative incremental processing, built-in quality (@dlt.expect), lineage and SCD support.

## UNITY CATALOG STRUCTURE

`
vet_platform/
  ├─ bronze/
  │  ├─ hospital_a_export
  │  ├─ hospital_b_export
  │  └─ hospital_c_export
  │
  ├─ silver/
  │  ├─ hospital_master
  │  ├─ owner_master
  │  ├─ pet_master
  │  ├─ doctor_master
  │  ├─ medication_master
  │  ├─ visit_fact
  │  ├─ treatment_fact
  │  └─ invoice_fact
  │
  ├─ gold/
  │  ├─ revenue_by_hospital
  │  ├─ revenue_by_doctor
  │  └─ visit_patterns
  │
  ├─ audit/
  │  ├─ pipeline_run_metrics
  │  └─ data_quality_records
  │
  └─ reference/
     ├─ holiday_calendar
     └─ lookup_tables
`

## SILVER LAYER DETAILED SCHEMA

### Master Tables (Dimensions)

#### hospital_master
`sql
hospital_key      BIGINT   PK
hospital_id       STRING
hospital_name     STRING
source_system     STRING
created_at        TIMESTAMP
updated_at        TIMESTAMP
`

#### owner_master
`sql
owner_key         BIGINT   PK
owner_id          STRING
first_name        STRING
last_name         STRING
phone             STRING
email             STRING
address           STRING
city              STRING
state             STRING
zip_code          STRING
source_system     STRING
created_at        TIMESTAMP
updated_at        TIMESTAMP
`

#### pet_master
`sql
pet_key           BIGINT   PK
pet_id            STRING
pet_name          STRING
species           STRING
breed             STRING
gender            STRING
birth_date        DATE
weight_kg         DECIMAL(5,2)
microchip_number  STRING
owner_key         BIGINT   FK -> owner_master.owner_key
source_system     STRING
created_at        TIMESTAMP
updated_at        TIMESTAMP
`

#### doctor_master
`sql
doctor_key        BIGINT   PK
doctor_id         STRING
doctor_name       STRING
specialization    STRING
source_system     STRING
created_at        TIMESTAMP
updated_at        TIMESTAMP
`

#### medication_master
`sql
medication_key    BIGINT   PK
medication_id     STRING
medication_name   STRING
source_system     STRING
created_at        TIMESTAMP
updated_at        TIMESTAMP
`

### Fact Tables

#### visit_fact
`sql
visit_key             BIGINT   PK
visit_id              STRING
visit_date            DATE
pet_key               BIGINT  FK -> pet_master.pet_key
doctor_key            BIGINT  FK -> doctor_master.doctor_key
hospital_key          BIGINT  FK -> hospital_master.hospital_key
appointment_type      STRING
visit_reason          STRING
diagnosis_code        STRING
diagnosis_description STRING
source_system         STRING
created_at            TIMESTAMP
updated_at            TIMESTAMP
`

#### treatment_fact
`sql
treatment_key       BIGINT   PK
treatment_id        STRING
visit_key           BIGINT   FK -> visit_fact.visit_key
medication_key      BIGINT   FK -> medication_master.medication_key
treatment_name      STRING
treatment_category  STRING
source_system        STRING
dosage              STRING
frequency           STRING
created_at          TIMESTAMP
`

#### invoice_fact
`sql
invoice_key         BIGINT   PK
invoice_id          STRING
visit_key           BIGINT   FK -> visit_fact.visit_key
invoice_amount      DECIMAL(10,2)
tax_amount          DECIMAL(10,2)
discount_amount     DECIMAL(10,2)
payment_method      STRING
payment_status      STRING
source_system        STRING
created_at          TIMESTAMP
`

## DATA QUALITY FRAMEWORK

- Use DLT @dlt.expect() for rules in Bronze & Silver.
- Core rules: pet_name IS NOT NULL; visit_date IS NOT NULL; invoice_amount > 0; email LIKE '%@%' OR email IS NULL; doctor exists; hospital exists; medication exists.
- On expectation failure, write rejected rows to vet_platform.audit.data_quality_quarantine:
  - columns: source_system, rejected_from_table, bad_record_id, rejected_timestamp, error_reason, raw_data (JSON).
- Monitor DLT quality metrics dashboard and record summary in audit.pipeline_run_metrics.

## INCREMENTAL PROCESSING STRATEGY

- Bronze ingestion: DLT auto-detects new files in DBFS and ingests incrementally.
- Silver merges: use DLT's APPLY CHANGES / built-in incremental semantics. Avoid manual .write() MERGE logic.
- Idempotency: capture file_name, batch_id, record_hash at Bronze. Use these to prevent duplicate processing if needed.
- SCD: implement SCD Type 2 for owner_master if history required; otherwise SCD Type 1 for other masters. Use created_at/updated_at for change detection.

## AUDIT FRAMEWORK

- vet_platform.audit.pipeline_run_metrics:
  - job_name, pipeline_name, start_time, end_time, status, rows_read, rows_processed, rows_failed, rows_quarantined, source_system, error_message, duration_seconds.
- vet_platform.audit.data_quality_quarantine (see Data Quality Framework).
- Use Delta DESCRIBE HISTORY and Time Travel for forensic queries. All Silver tables include timestamps (created_at/updated_at) for traceability.

## PROJECT STRUCTURE

`
vet-lakehouse/
│
├── pipelines/
│   ├── bronze_pipeline.py        ← Bronze ingestion script
│   ├── silver_pipeline.py        ← Silver transformation script
│   └── quality_expectations.py   ← Shared quality rules
│
├── src/
│   ├── generate/
│   │   └── generate_data.py      ← Synthetic data generation
│   ├── common/
│   │   ├── config.py             ← Configuration loader
│   │   ├── constants.py          ← Constants & configs
│   │   └── spark.py              ← Spark session setup
│   └── utils/
│       └── quality_helpers.py    ← Reusable quality functions
│
├── configs/
│   ├── bronze.yml                ← Bronze pipeline config
│   └── silver.yml                ← Silver pipeline config
│
├── resources/
│   └── workflow.yml              ← Databricks Workflow definition
│
├── tests/
│   ├── test_bronze_quality.py
│   ├── test_silver_transforms.py
│   └── conftest.py
│
├── requirements.txt
├── README.md
└── .gitignore
`

## SETUP WORKFLOW (IN DATABRICKS UI)

1. Create Unity Catalog `vet_platform` and schemas: bronze, silver, gold, audit, reference.
2. Upload repository to Workspace (Git clone or import).
3. Create DLT pipeline: Bronze
   - Notebook/python: dlt_pipelines/bronze_pipeline.py
   - Target schema: vet_platform.bronze
   - Configure storage location and libraries.
4. Create DLT pipeline: Silver
   - Notebook/python: dlt_pipelines/silver_pipeline.py
   - Target schema: vet_platform.silver
   - Configure pipeline to run after Bronze (or schedule accordingly).
5. Create Databricks Workflow:
   - Task 1: generate_data (optional)
   - Task 2: bronze DLT pipeline (pipeline task)
   - Task 3: silver DLT pipeline (pipeline task; depends on bronze)
6. Run and monitor via DLT dashboard and audit.pipeline_run_metrics.


## GOLD TABLE DETAILED SCHEMA

#### gold.daily_revenue_summary
`sql
revenue_id        BIGINT   PK
revenue_date      DATE
hospital_key      BIGINT   FK -> hospital_master.hospital_key
doctor_key        BIGINT   FK -> doctor_master.doctor_key
hospital_name     STRING
doctor_name       STRING
total_revenue     DECIMAL(18,2)
total_tax         DECIMAL(18,2)
total_discount    DECIMAL(18,2)
net_revenue       DECIMAL(18,2)
invoice_count     INT
visit_count       INT
refreshed_at      TIMESTAMP
`

#### gold.top_treatment_summary
`sql
treatment_key         BIGINT   PK
treatment_name        STRING
treatment_category    STRING
usage_count           INT
unique_pets_treated   INT
usage_rank            INT
most_used_medication  STRING
snapshot_date         DATE
refreshed_at          TIMESTAMP
`

#### gold.repeat_visit_summary
`sql
pet_key              BIGINT   PK -> pet_master.pet_key
pet_name             STRING
owner_name           STRING
total_visit_count    INT
first_visit_date     DATE
last_visit_date      DATE
avg_days_between_visits DECIMAL(5,2)
is_repeat_visitor    BOOLEAN
refreshed_at         TIMESTAMP
`

#### gold.active_pet_summary
`sql
pet_key             BIGINT   PK -> pet_master.pet_key
pet_name            STRING
species             STRING
owner_name          STRING
hospital_name       STRING
last_visit_date     DATE
days_since_last_visit INT
is_active           BOOLEAN
active_window_days   INT
refreshed_at        TIMESTAMP
`

`

--- 