# Veterinary Hospital Lakehouse Platform

## Overview

This project demonstrates the design and implementation of a modern Data Engineering platform using Databricks Lakehouse architecture.

The objective is to consolidate data from multiple veterinary hospitals that operate on different source systems and schemas into a centralized, governed, and analytics-ready platform.

The solution leverages Databricks, Delta Live Tables (DLT), Delta Lake, Unity Catalog, SQL Warehouse, and Python to build an end-to-end data pipeline.

---

# Business Problem

A veterinary healthcare organization operates multiple hospitals, each maintaining data in different formats and structures.

### Challenges

- Multiple source systems with different schemas
- Data duplication and inconsistency
- Lack of centralized reporting
- No standard data governance framework
- Manual analytics and reporting processes

The goal is to build a scalable and governed platform capable of ingesting, standardizing, and serving data for analytics and future AI use cases.

---

# Solution Architecture

```text
Hospital A
Hospital B
Hospital C
      |
      ▼
Delta Live Tables (Bronze)
      |
      ▼
Delta Live Tables (Silver)
      |
      ▼
Gold Analytics Layer
      |
      ├── SQL Warehouse
      ├── Dashboard
      └── APIs
```

---

# Technology Stack

| Component | Technology |
|------------|------------|
| Data Platform | Databricks |
| Data Processing | PySpark |
| ETL Framework | Delta Live Tables (DLT) |
| Storage Format | Delta Lake |
| Governance | Unity Catalog |
| Language | Python |
| Configuration | YAML |
| Analytics | SQL Warehouse |
| Dashboard | Streamlit |
| APIs | FastAPI |
| Deployment | Databricks Asset Bundles |

---

# Data Architecture

## Bronze Layer

Stores raw data exactly as received from source systems.

### Objectives

- Preserve source data
- Enable traceability
- Support data replay and auditing

---

## Silver Layer

Stores standardized and cleansed business entities.

### Objectives

- Data standardization
- Schema harmonization
- Data quality validation
- Incremental processing

Example entities:

```text
Owner
Pet
Doctor
Visit
Treatment
Invoice
```

---

## Gold Layer

Stores business-ready analytical datasets.

### Objectives

- Reporting
- KPI generation
- Dashboard consumption
- API consumption

Example outputs:

```text
Hospital Performance
Doctor Performance
Revenue Analytics
Executive Dashboard
```

---

# Key Databricks Concepts Covered

## Delta Live Tables (DLT)

Used to build managed and declarative data pipelines.

Benefits:

- Automated pipeline management
- Built-in monitoring
- Data lineage
- Data quality enforcement

---

## Delta Lake

Provides:

- ACID Transactions
- Schema Evolution
- Time Travel
- Optimized Storage

---

## Incremental Processing

Supports processing only newly arrived or modified records instead of reloading complete datasets.

Benefits:

- Improved performance
- Reduced processing cost
- Faster pipeline execution

---

## Unity Catalog

Provides centralized governance for:

- Catalogs
- Schemas
- Tables
- Permissions
- Data Discovery

---

# Data Quality

Validation rules are implemented during processing.

Examples:

```text
Pet ID cannot be null

Owner ID cannot be null

Invoice Amount must be greater than zero
```

Data quality checks are enforced within DLT pipelines.

---

# Analytics Layer

The Gold layer serves as the central consumption layer for:

### Business Users

- Revenue Analysis
- Hospital Performance
- Doctor Performance
- Operational Metrics

### Applications

- Dashboards
- APIs
- Future AI Assistants

---

# Expected Outcome

The project delivers a complete modern Lakehouse implementation capable of:

- Multi-source data ingestion
- Data standardization
- Incremental processing
- Data governance
- Analytics enablement
- Dashboard integration
- API-based data consumption

The implementation provides practical exposure to real-world Databricks Data Engineering concepts including DLT, Delta Lake, Unity Catalog, and Lakehouse architecture.
