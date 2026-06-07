-- ================================================================
--  SUPERSTORE SALES ANALYSIS
--  PostgreSQL Script
-- ================================================================


-- ── Create superstore_raw table ──────────────────────────────────
DROP TABLE IF EXISTS superstore_raw;

CREATE TABLE superstore_raw (
    row_id        INTEGER,
    order_id      VARCHAR(25),
    order_date    VARCHAR(15),
    ship_date     VARCHAR(15),
    ship_mode     VARCHAR(30),
    customer_id   VARCHAR(15),
    customer_name VARCHAR(100),
    segment       VARCHAR(30),
    country       VARCHAR(50),
    city          VARCHAR(50),
    state         VARCHAR(50),
    postal_code   VARCHAR(10),
    region        VARCHAR(20),
    product_id    VARCHAR(20),
    category      VARCHAR(30),
    sub_category  VARCHAR(30),
    product_name  VARCHAR(255),
    sales         NUMERIC(10,2),
    quantity      INTEGER,
    discount      NUMERIC(5,2),
    profit        NUMERIC(10,2)
);


SELECT COUNT(*) AS total_rows FROM superstore_raw;


-- ── Create normalized tables using SELECT DISTINCT ───────────────

-- Stores unique customer records
CREATE TABLE customers AS
SELECT DISTINCT customer_id, customer_name, segment, region
FROM superstore_raw;

-- Stores unique product records
CREATE TABLE products AS
SELECT DISTINCT product_id, product_name, category, sub_category
FROM superstore_raw;

-- Stores all order transactions
CREATE TABLE orders AS
SELECT DISTINCT row_id, order_id, order_date, ship_date, ship_mode,
    customer_id, product_id, sales, quantity, discount, profit
FROM superstore_raw;

-- Verify all tables
SELECT 'superstore_raw' AS table_name, COUNT(*) AS rows FROM superstore_raw
UNION ALL
SELECT 'customers', COUNT(*) FROM customers
UNION ALL
SELECT 'products',  COUNT(*) FROM products
UNION ALL
SELECT 'orders',    COUNT(*) FROM orders;


-- ── View table data ──────────────────────────────────────────────
SELECT * FROM superstore_raw LIMIT 10;
SELECT * FROM customers      LIMIT 10;
SELECT * FROM products       LIMIT 10;
SELECT * FROM orders         LIMIT 10;


-- ================================================================
--  SUBQUERIES
-- ================================================================

--Orders where sales are greater than average sales

SELECT
    o.order_id,
    c.customer_name,
    ROUND(o.sales::NUMERIC, 2) AS order_sales,
    ROUND((SELECT AVG(sales)::NUMERIC FROM orders), 2) AS avg_sales
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.sales > (SELECT AVG(sales) FROM orders)
ORDER BY o.sales DESC;


-- Highest sales order for each customer

SELECT
    c.customer_name,
    o.order_id,
    ROUND(o.sales::NUMERIC, 2) AS highest_order_sales
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.sales = (
    SELECT MAX(o2.sales)
    FROM orders o2
    WHERE o2.customer_id = o.customer_id
)
ORDER BY highest_order_sales DESC;


-- ================================================================
--  CTEs
-- ================================================================

-- Total sales per customer

WITH customer_sales AS (
    SELECT
        customer_id,
        ROUND(SUM(sales)::NUMERIC, 2) AS total_sales,
        COUNT(DISTINCT order_id)       AS total_orders
    FROM orders
    GROUP BY customer_id
)
SELECT
    c.customer_name,
    c.segment,
    c.region,
    cs.total_sales,
    cs.total_orders
FROM customer_sales cs
JOIN customers c ON cs.customer_id = c.customer_id
ORDER BY cs.total_sales DESC;


-- Customers whose total sales are above average

WITH customer_sales AS (
    SELECT
        customer_id,
        ROUND(SUM(sales)::NUMERIC, 2) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT
    c.customer_name,
    c.segment,
    c.region,
    cs.total_sales,
    ROUND((SELECT AVG(total_sales) FROM customer_sales)::NUMERIC, 2) AS avg_benchmark
FROM customer_sales cs
JOIN customers c ON cs.customer_id = c.customer_id
WHERE cs.total_sales > (SELECT AVG(total_sales) FROM customer_sales)
ORDER BY cs.total_sales DESC;


-- ================================================================
--  WINDOW FUNCTIONS
-- ================================================================

-- Rank all customers by total sales

WITH customer_sales AS (
    SELECT
        customer_id,
        ROUND(SUM(sales)::NUMERIC, 2) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT
    RANK() OVER (ORDER BY cs.total_sales DESC) AS sales_rank,
    c.customer_name,
    c.segment,
    c.region,
    cs.total_sales
FROM customer_sales cs
JOIN customers c ON cs.customer_id = c.customer_id
ORDER BY sales_rank;


-- Row numbers for each order within a customer

SELECT
    c.customer_name,
    o.order_id,
    o.order_date,
    ROUND(o.sales::NUMERIC, 2) AS sales,
    ROW_NUMBER() OVER (
        PARTITION BY o.customer_id
        ORDER BY o.sales DESC
    ) AS order_rank_within_customer
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
ORDER BY c.customer_name, order_rank_within_customer;


-- Top 3 customers by total sales

WITH customer_sales AS (
    SELECT
        customer_id,
        ROUND(SUM(sales)::NUMERIC, 2) AS total_sales
    FROM orders
    GROUP BY customer_id
),
ranked AS (
    SELECT
        c.customer_name,
        c.segment,
        c.region,
        cs.total_sales,
        RANK() OVER (ORDER BY cs.total_sales DESC) AS sales_rank
    FROM customer_sales cs
    JOIN customers c ON cs.customer_id = c.customer_id
)
SELECT * FROM ranked WHERE sales_rank <= 3;


-- ================================================================
--  FINAL COMBINED QUERY (JOIN + CTE + Window Function)
--  Shows Customer Name, Total Sales, Rank
-- ================================================================

WITH customer_sales AS (
    SELECT
        o.customer_id,
        ROUND(SUM(o.sales)::NUMERIC,  2) AS total_sales,
        ROUND(SUM(o.profit)::NUMERIC, 2) AS total_profit,
        COUNT(DISTINCT o.order_id)        AS total_orders
    FROM orders o
    GROUP BY o.customer_id
),
ranked_customers AS (
    SELECT
        c.customer_name,
        c.segment,
        c.region,
        cs.total_sales,
        cs.total_profit,
        cs.total_orders,
        RANK() OVER (ORDER BY cs.total_sales DESC) AS sales_rank
    FROM customer_sales cs
    JOIN customers c ON cs.customer_id = c.customer_id
)
SELECT
    sales_rank    AS "Rank",
    customer_name AS "Customer Name",
    segment       AS "Segment",
    region        AS "Region",
    total_sales   AS "Total Sales ($)",
    total_profit  AS "Total Profit ($)",
    total_orders  AS "Total Orders"
FROM ranked_customers
ORDER BY sales_rank;


-- ================================================================
--  MINI PROJECT: CUSTOMER SALES INSIGHTS
-- ================================================================

-- Top 5 customers by total sales

WITH cs AS (
    SELECT customer_id, ROUND(SUM(sales)::NUMERIC, 2) AS total_sales
    FROM orders GROUP BY customer_id
)
SELECT
    RANK() OVER (ORDER BY cs.total_sales DESC) AS rank,
    c.customer_name, c.segment, c.region, cs.total_sales
FROM cs
JOIN customers c ON cs.customer_id = c.customer_id
ORDER BY total_sales DESC LIMIT 5;


-- Bottom 5 customers by total sales

WITH cs AS (
    SELECT customer_id, ROUND(SUM(sales)::NUMERIC, 2) AS total_sales
    FROM orders GROUP BY customer_id
)
SELECT
    RANK() OVER (ORDER BY cs.total_sales ASC) AS rank,
    c.customer_name, c.segment, c.region, cs.total_sales
FROM cs
JOIN customers c ON cs.customer_id = c.customer_id
ORDER BY total_sales ASC LIMIT 5;


-- Customers who made only one order

SELECT
    c.customer_name,
    c.segment,
    c.region,
    COUNT(DISTINCT o.order_id)      AS order_count,
    ROUND(SUM(o.sales)::NUMERIC, 2) AS total_sales
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY o.customer_id, c.customer_name, c.segment, c.region
HAVING COUNT(DISTINCT o.order_id) = 1
ORDER BY total_sales DESC;


-- Customers with above-average total sales

WITH cs AS (
    SELECT customer_id, ROUND(SUM(sales)::NUMERIC, 2) AS total_sales
    FROM orders GROUP BY customer_id
)
SELECT
    c.customer_name, c.segment, c.region, cs.total_sales,
    ROUND((SELECT AVG(total_sales) FROM cs)::NUMERIC, 2) AS avg_sales
FROM cs
JOIN customers c ON cs.customer_id = c.customer_id
WHERE cs.total_sales > (SELECT AVG(total_sales) FROM cs)
ORDER BY cs.total_sales DESC;


-- Highest order value per customer

SELECT
    c.customer_name,
    c.segment,
    o.order_id,
    ROUND(o.sales::NUMERIC, 2) AS highest_order_value,
    o.order_date
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.sales = (
    SELECT MAX(o2.sales)
    FROM orders o2
    WHERE o2.customer_id = o.customer_id
)
ORDER BY highest_order_value DESC;
