# Week 6 — Apache Spark: Architecture & Data Processing
---
## Overview
This assignment applies Apache Spark fundamentals to the Sample Superstore dataset. It covers the full data engineering lifecycle — schema definition, cleaning, transformation, aggregation, and output — while demonstrating core Spark concepts like lazy evaluation, shuffle, and predicate pushdown.

---

## Dataset
**File:** `Sample - Superstore.csv` — 9,994 rows across 21 columns covering orders, customers, geography, product categories, and financials (Sales, Profit, Discount).

---

## Folder Structure
```
Assignment_6_Spark/
├── Sample - Superstore.csv
├── spark_basics.ipynb
├── results.csv
└── README.md
```

---

## Pipeline

| Step | Operation | Detail |
|------|-----------|--------|
| 1 | Load | CSV read with explicit schema — no inferSchema scan |
| 2 | Clean | Nulls filled, duplicates dropped, empty strings handled |
| 3 | Transform | Columns renamed, dates parsed, types cast |
| 4 | Enrich | Added Profit_Margin, Revenue_Band, Days_to_Ship, Order_Year |
| 5 | Filter | Profit > 0, Discount <= 30% |
| 6 | Aggregate | Total Sales, Profit, Avg Order Value by Region and Category |
| 7 | Write | Final output saved to `results.csv` |

---

## Spark Concepts Applied

**Architecture** — Ran in `local[*]` mode where Driver and Executors share one JVM. In production, a Cluster Manager (YARN / Kubernetes) would distribute this across worker nodes.

**Lazy Evaluation** — Every transformation built a DAG without executing. Spark's Catalyst optimizer reviewed the full plan before running anything, triggered only by actions like `count()` or `show()`.

**Shuffle** — `groupBy` redistributes rows across partitions by key. Filtering before aggregation reduced the data volume going into the shuffle, which is the primary way to keep it cheap.

**Predicate Pushdown** — Parquet filters were pushed to the file reader level, skipping irrelevant row groups before data entered memory. Visible in the execution plan as `PushedFilters`.

**CSV vs Parquet** — Parquet produced a smaller file than the raw CSV through columnar compression, and read faster by loading only the queried columns rather than every field in every row.

**Best Practices** — Used `show()` over `collect()`, `cache()` for reused DataFrames, `coalesce(1)` before CSV write to avoid small files, and early `select()` to reduce data carried into joins and aggregations.

---

## Key Insights

- Technology is the highest-revenue category; Copiers is the most profitable sub-category
- The West region leads overall sales across all segments
- Tables and Bookcases operate at a loss — driven by discounts exceeding 40%
- Orders with discount above 40% result in negative profit in nearly all cases
- Removing loss-making and heavily discounted orders left ~6,000 rows in the final output

---

## How to Run

1. Open `spark_basics.ipynb` in Google Colab
2. Upload `Sample - Superstore.csv` via the Files panel
3. Run all cells top to bottom — Step 0 installs PySpark and must complete before any other cell

---

## Technologies
PySpark 3.x · Python 3.12 · Google Colab · Java 17 (OpenJDK)
