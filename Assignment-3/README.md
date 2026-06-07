# Assignment 3 — Superstore SQL Analysis

## Objective
Analyze sales data from the Superstore dataset using advanced SQL concepts — 
Subqueries, CTEs, and Window Functions — to solve real business queries.

## Dataset
[Kaggle Superstore Dataset](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final)  
9,994 sales records across customers, products, orders and regions.

## Tools Used
- PostgreSQL
- pgAdmin 4
  
### 1. Data Setup
- Loaded the Superstore CSV into a raw table called `superstore_raw`
- Created 3 normalized tables from it using `SELECT DISTINCT`:
  - `customers` — unique customer records (name, segment, region)
  - `products` — unique product records (name, category, sub-category)
  - `orders` — all order transactions (sales, profit, quantity, discount)

### 2. Subqueries
- Found all orders where sales are **greater than the average sales**
- Found the **highest sales order** for each customer using a correlated subquery

### 3. CTEs (Common Table Expressions)
- Calculated **total sales per customer** using a CTE
- Found customers whose **total sales are above average** using CTE + Subquery combined

### 4. Window Functions
- **Ranked all customers** by total sales using `RANK()`
- Assigned **row numbers to each order within a customer** using `ROW_NUMBER()` + `PARTITION BY`
- Displayed the **top 3 customers** by total sales using `RANK()` filtered to top 3

### 5. Final Combined Query
Wrote one final query combining **JOIN + CTE + Window Function** together to display:
- Customer Name
- Total Sales
- Total Profit
- Total Orders
- Rank

### 6. Mini Project — Customer Sales Insights
Answered 5 real business questions using SQL:

## Key Insights
- Top 5 customers contribute a disproportionately high share of total revenue
- Single-order customers represent a significant churn risk and need re-engagement
- Above-average customers are strong candidates for loyalty and VIP programs
- The gap between top and bottom customers is large, indicating diverse buyer segments

## Files in This Folder
- `superstore_clean.sql` — complete SQL script with all queries
- `screenshots/` — query results captured from pgAdmin
