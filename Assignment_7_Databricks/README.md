# Delta Lake Incremental Processing Assignment

## Overview
This assignment covers incremental data processing using Delta Lake on Databricks. It simulates a real-world scenario where a customer dataset needs to be kept up to date as new and changed records arrive over time, using Delta Lake's MERGE operation to handle updates and inserts together.

## Dataset
Files: `customer_master.csv`, `customer_incremental.csv`
Covers customer details — customer_id, name, email, city, status, and updated_at.

- `customer_master.csv` - the existing/base customer data
- `customer_incremental.csv` - new and updated customer records simulating a later data load

## Folder Structure
```
delta-lake-assignment/
│
├── data/
│   ├── customer_master.csv
│   └── customer_incremental.csv
│
├── notebook/
│   └── delta_scd_assignment.ipynb
│
├── screenshots/
│   ├── data_loading/
│   ├── data_cleaning/
│   ├── scd1/
│   ├── validation/
│   └── final_output/
│
└── README.md
```

## Pipeline Steps

| Step | Operation | Description |
|------|-----------|-------------|
| 1 | Load Data | Loaded customer_master.csv into a Spark DataFrame and saved as a Delta table |
| 2 | Data Cleaning | Removed duplicate customer_id rows and dropped rows with missing email |
| 3 | Load Incremental Data | Loaded customer_incremental.csv simulating new/updated records |
| 4 | Merge Operation | Used SQL MERGE INTO to update matching customers and insert new ones |
| 5 | Validation | Checked row counts and confirmed no duplicate customer_id values remained |
| 6 | Final Output | Displayed the updated Delta table and reviewed table version history |

## Key Concepts Covered
- **Delta Lake** — an open-source storage layer that brings ACID transactions and reliability to data lakes
- **MERGE INTO** — combines update and insert logic into a single atomic operation (also known as an upsert)
- **SCD Type 1** — old values are overwritten with new ones, no history is kept
- **Data Cleaning** — handling nulls and duplicate records before loading into a table
- **DESCRIBE HISTORY** — Delta Lake automatically tracks every version of a table, allowing you to see what changed and when

## Key Insights
- Delta Lake's MERGE removes the need to write separate update/insert logic manually
- Cleaning the master data before merging avoids carrying forward duplicate or incomplete records
- Delta table versioning (visible via DESCRIBE HISTORY) makes it possible to trace changes over time without extra setup
- Running MERGE repeatedly with the same incremental file is safe since matching records are simply updated again rather than duplicated

## How to Run
1. Open `notebooks/delta_scd_assignment.ipynb` in Databricks
2. Upload `customer_master.csv` and `customer_incremental.csv` to a Unity Catalog volume
3. Update the file paths in the notebook to match your volume path
4. Run all cells from top to bottom

## Technologies Used
PySpark (Databricks Runtime), Delta Lake, SQL, Databricks Notebooks

## Author
Lakshita
Data Engineering Intern — Celebal Technologies
