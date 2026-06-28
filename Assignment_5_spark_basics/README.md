## Overview

This assignment covers the fundamentals of Apache Spark using PySpark, applied to the Sample Superstore Sales dataset. It includes a complete data processing pipeline — loading, cleaning, transforming, aggregating, and saving results.

---

## Dataset

**File:** Sample - Superstore.csv
Covers order details, customer info, geography, product categories, and financials (Sales, Profit, Discount).

---

## Folder Structure

```
Assignment_5_Spark/
│   └── Sample - Superstore.csv
│   └── spark_basics.ipynb
│   └── results.csv
└── README.md
```

---

## Pipeline Steps

| Step | Operation | Description |
|---|---|---|
| 1 | Load Data | Loaded CSV via Pandas, converted to Spark DataFrame |
| 2 | Data Cleaning | Removed duplicates, handled nulls and empty strings |
| 3 | Schema Transformation | Renamed columns, cast data types, parsed dates |
| 4 | Feature Engineering | Added Profit_Margin, Revenue_Class, Shipping_Days |
| 5 | Filtering | Filtered by Profit, Category, Region, Sales range |
| 6 | Aggregation | Computed Total Revenue, Profit, Avg Order Value |
| 7 | GroupBy | Grouped by Region and Category with full KPI summary |
| 8 | Save Output | Saved final results to output/results.csv |

---

## Key Concepts Covered

- **Spark vs MapReduce** — Spark processes data in-memory making it up to 100x faster than disk-based MapReduce
- **Narrow Transformations** — `filter()`, `select()`, `withColumn()` — no shuffle
- **Wide Transformations** — `groupBy()`, `orderBy()` — triggers shuffle across partitions
- **Immutability** — every transformation produces a new DataFrame, original is never modified
- **Lazy Evaluation** — Spark builds an execution plan and runs only when an action is called

---

## Key Insights

- Technology category generates the highest total sales
- West region leads overall revenue
- Copiers is the most profitable sub-category
- Tables and Bookcases are loss-making due to high discounts
- Orders with discounts above 40% almost always result in a loss

---

## How to Run

1. Open `notebook/spark_basics.ipynb`
2. Upload `Sample - Superstore.csv` when prompted
3. Run all cells from top to bottom

---

## Technologies Used

PySpark 3.x, Python 3.12, Google Colab, Pandas, Java 17 (OpenJDK)

---

## Author

**Lakshita**
Data Engineering Intern — Celebal Technologies
