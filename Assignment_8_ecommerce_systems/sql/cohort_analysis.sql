
-- 15. Complex CTE: Cohort Analysis
-- Group customers by registration month (cohort).
-- For each cohort, calculate how many ordered in month 0 (registration month),
-- month 1, month 2, and month 3, along with their retention rates.
WITH customer_cohorts AS (
    SELECT 
        customer_id,
        strftime('%Y-%m', registration_date) AS cohort_month
    FROM customers
),
customer_orders AS (
    SELECT DISTINCT 
        o.customer_id,
        strftime('%Y-%m', o.order_date) AS order_month,
        cc.cohort_month,
        -- Calculate difference in months between order date and customer registration date
        (CAST(strftime('%Y', o.order_date) AS INTEGER) - CAST(strftime('%Y', c.registration_date) AS INTEGER)) * 12 +
        (CAST(strftime('%m', o.order_date) AS INTEGER) - CAST(strftime('%m', c.registration_date) AS INTEGER)) AS month_number
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    JOIN customer_cohorts cc ON o.customer_id = cc.customer_id
),
cohort_sizes AS (
    -- Size of each cohort (based on registration month)
    SELECT 
        strftime('%Y-%m', registration_date) AS cohort_month,
        COUNT(DISTINCT customer_id) AS cohort_size
    FROM customers
    GROUP BY cohort_month
),
cohort_activity AS (
    -- Count of unique active customers for each month after registration
    SELECT 
        cohort_month,
        month_number,
        COUNT(DISTINCT customer_id) AS active_customers
    FROM customer_orders
    WHERE month_number >= 0
    GROUP BY cohort_month, month_number
)
SELECT 
    cs.cohort_month,
    cs.cohort_size,
    -- Month 0 (Registration Month)
    COALESCE(m0.active_customers, 0) AS m0_active,
    ROUND(COALESCE(m0.active_customers, 0) * 100.0 / cs.cohort_size, 2) || '%' AS m0_retention,
    
    -- Month 1
    COALESCE(m1.active_customers, 0) AS m1_active,
    ROUND(COALESCE(m1.active_customers, 0) * 100.0 / cs.cohort_size, 2) || '%' AS m1_retention,
    
    -- Month 2
    COALESCE(m2.active_customers, 0) AS m2_active,
    ROUND(COALESCE(m2.active_customers, 0) * 100.0 / cs.cohort_size, 2) || '%' AS m2_retention,
    
    -- Month 3
    COALESCE(m3.active_customers, 0) AS m3_active,
    ROUND(COALESCE(m3.active_customers, 0) * 100.0 / cs.cohort_size, 2) || '%' AS m3_retention
FROM cohort_sizes cs
LEFT JOIN cohort_activity m0 ON cs.cohort_month = m0.cohort_month AND m0.month_number = 0
LEFT JOIN cohort_activity m1 ON cs.cohort_month = m1.cohort_month AND m1.month_number = 1
LEFT JOIN cohort_activity m2 ON cs.cohort_month = m2.cohort_month AND m2.month_number = 2
LEFT JOIN cohort_activity m3 ON cs.cohort_month = m3.cohort_month AND m3.month_number = 3
ORDER BY cs.cohort_month ASC;
