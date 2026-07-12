# E-Commerce Order Analytics System
## Overview
This assignment covers the design and development of an end-to-end e-commerce order analytics system combining Python and SQL. It simulates a real-world data engineering workflow — starting from raw, messy dataset generation, through cleaning and validation, loading into a relational database with proper constraints, and finally producing business-ready reports covering revenue, customer rankings, cohort retention, and RFM-based segmentation.

## Dataset
Files: `customers.csv`, `products.csv`, `orders.csv`, `order_items.csv`
Covers customer details, product catalog, order records, and order line items.
- `data/raw/` - synthetically generated data with intentional inconsistencies (NULL customer IDs, invalid emails, inconsistent date formats, duplicates, orphan order items, negative quantities, invalid discounts)
- `data/cleaned/` - validated and cleaned versions of the same datasets, ready to be loaded into SQL

## Folder Structure
```
Assignment_8_ecommerce_systems/
│
├── Report/
│   └── Week_8_Summary_Report.pdf
│
├── data/
│   ├── raw/
│   │   ├── customers.csv
│   │   ├── products.csv
│   │   ├── orders.csv
│   │   └── order_items.csv
│   │
│   ├── cleaned/
│   │   ├── clean_customers.csv
│   │   ├── clean_products.csv
│   │   ├── clean_orders.csv
│   │   └── clean_order_items.csv
│   │
│   └── sample_reports/
│       ├── revenue_by_category.png
│       ├── top_customers.png
│       └── retention.png
│
├── scripts/
│   ├── generate_data.py
│   ├── clean_data.py
│   ├── edge_cases.py
│   └── report_cli.py
│
└── sql/
    ├── schema.sql
    ├── aggregations.sql
    ├── window_functions.sql
    └── cohort_analysis.sql
```

## Pipeline Steps
| Step | Operation | Description |
|------|-----------|-------------|
| 1 | Generate Data | Generated customers, products, orders, and order_items datasets with realistic inconsistencies, exported to data/raw |
| 2 | Data Cleaning | Handled missing values, removed duplicates, standardized product names, corrected date formats, validated emails, and checked referential integrity |
| 3 | Load into SQL | Created a SQLite schema with Primary Keys, Foreign Keys, NOT NULL and CHECK constraints, then loaded the cleaned datasets |
| 4 | Aggregations | Wrote JOIN and aggregation queries for revenue by customer, category, and month, top products, and Average Order Value |
| 5 | Window Functions & CTEs | Used DENSE_RANK(), LAG(), NTILE(), SUM() OVER(), and AVG() OVER() for customer ranking, running totals, and lifetime value analysis |
| 6 | Cohort & Retention Analysis | Built registration and first-purchase cohorts and calculated monthly retention rates to identify repeat and churned customers |
| 7 | Customer Segmentation | Segmented customers by purchase frequency, spending tiers, and RFM (Recency, Frequency, Monetary) analysis |
| 8 | CLI Reporting Tool | Built report_cli.py to generate daily, monthly, revenue, retention, and top_customers reports as formatted console tables |
| 9 | Edge Case Handling | Validated orphan records, future dates, invalid discounts, zero-quantity orders, empty results, and invalid CLI inputs |
| 10 | Documentation | Wrote this README covering architecture, folder structure, setup, execution steps, and sample outputs |

## Key Concepts Covered
- **Data Generation with Intentional Noise** — simulating real-world messiness (nulls, duplicates, orphan records, invalid formats) to properly test the cleaning pipeline
- **Referential Integrity** — enforcing relationships between customers, orders, products, and order_items using Primary/Foreign Keys and CHECK constraints
- **Window Functions & CTEs** — DENSE_RANK(), LAG(), NTILE(), and OVER() clauses for ranking, running totals, and moving averages without collapsing rows
- **Cohort Analysis** — grouping customers by registration or first-purchase month and tracking retention across subsequent months
- **RFM Segmentation** — scoring customers on Recency, Frequency, and Monetary value to derive actionable segments like Core Loyal and At Risk Loyal
- **CLI Reporting** — wrapping SQL analytics behind a command-line tool that outputs formatted, business-readable tables

## Key Insights
- Introducing inconsistencies deliberately during data generation made the cleaning and validation logic meaningful to test, rather than trivial
- Enforcing constraints at the schema level (NOT NULL, CHECK, Foreign Keys) catches bad data at load time instead of surfacing as bugs later in reporting
- Window functions and CTEs made ranking and running-total logic far more readable than equivalent GROUP BY-only queries
- Anchoring cohorts on first-purchase month versus registration month gave noticeably different retention patterns, showing why the choice of anchor date matters
- RFM segmentation surfaced customer groups (like At Risk Loyal) that frequency-based segmentation alone would have missed
- Wrapping the analytics in a CLI tool made the reports repeatable and shareable without needing to rerun raw SQL each time

## How to Run
1. Run `scripts/generate_data.py` to create the raw datasets in `data/raw/`
2. Run `scripts/clean_data.py` to clean and validate the data, output saved to `data/cleaned/`
3. Run `sql/schema.sql` against SQLite to create the database schema, then load the cleaned CSVs
4. Run `sql/aggregations.sql`, `sql/window_functions.sql`, and `sql/cohort_analysis.sql` for the analytics layer
5. Run `scripts/report_cli.py` with a report type argument (e.g. `daily`, `revenue`, `retention`, `top_customers`) to generate formatted reports
6. Run `scripts/edge_cases.py` to validate edge case handling across the pipeline

## Technologies Used
Python, Pandas, SQLite, SQL, CLI (argparse)

## Author
Lakshita
Data Engineering Intern — Celebal Technologies
