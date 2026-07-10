
-- 7. Running Totals with Window Functions
-- Calculate running total of revenue per region, ordered by date.
-- Daily revenue is computed first, then windowed SUM is applied.

WITH daily_region_revenue AS (
    SELECT 
        o.region_code,
        date(o.order_date) AS order_day,
        ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS daily_revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY o.region_code, order_day
)
SELECT 
    region_code,
    order_day AS order_date,
    daily_revenue,
    ROUND(SUM(daily_revenue) OVER (PARTITION BY region_code ORDER BY order_day), 2) AS running_total
FROM daily_region_revenue
ORDER BY region_code, order_day;

-- 8. Ranking with DENSE_RANK
-- For each category, rank products by total revenue.
-- Products with same revenue have same rank.

WITH product_revenue AS (
    SELECT 
        p.category,
        p.product_name,
        ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS total_revenue
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY p.category, p.product_name
)
SELECT 
    category,
    product_name,
    total_revenue,
    DENSE_RANK() OVER (PARTITION BY category ORDER BY total_revenue DESC) AS rank_in_category
FROM product_revenue
ORDER BY category, rank_in_category;

-- 9. LAG/LEAD Analysis

-- For each customer, calculate days between consecutive orders.
-- Flag customers with average gap > 30 days as "At Risk".

WITH order_dates AS (
    SELECT 
        customer_id,
        order_date,
        LAG(order_date) OVER (PARTITION BY customer_id ORDER BY order_date) AS previous_order_date
    FROM orders
),
order_gaps AS (
    SELECT 
        customer_id,
        order_date,
        previous_order_date,
        CASE 
            WHEN previous_order_date IS NULL THEN NULL
            ELSE ROUND(julianday(order_date) - julianday(previous_order_date), 2)
        END AS days_gap
    FROM order_dates
),
customer_avg_gaps AS (
    SELECT 
        customer_id,
        AVG(days_gap) AS avg_days_gap
    FROM order_gaps
    GROUP BY customer_id
)
SELECT 
    g.customer_id,
    g.order_date,
    g.previous_order_date,
    g.days_gap,
    ROUND(a.avg_days_gap, 2) AS avg_gap,
    CASE 
        WHEN a.avg_days_gap > 30 THEN 'At Risk'
        ELSE 'Active'
    END AS risk_status
FROM order_gaps g
JOIN customer_avg_gaps a ON g.customer_id = a.customer_id
ORDER BY g.customer_id, g.order_date;


-- 10. CTE with Multiple Levels
-- Categorize customers by monthly spend and count them per tier.

WITH customer_monthly_revenue AS (
    SELECT 
        o.customer_id,
        strftime('%Y-%m', o.order_date) AS order_month,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS monthly_revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY o.customer_id, order_month
),
customer_categories AS (
    SELECT 
        customer_id,
        order_month,
        monthly_revenue,
        CASE 
            WHEN monthly_revenue > 10000 THEN 'High'
            WHEN monthly_revenue BETWEEN 5000 AND 10000 THEN 'Medium'
            ELSE 'Low'
        END AS spend_tier
    FROM customer_monthly_revenue
)
SELECT 
    order_month,
    spend_tier,
    COUNT(DISTINCT customer_id) AS customer_count,
    ROUND(SUM(monthly_revenue), 2) AS tier_revenue
FROM customer_categories
GROUP BY order_month, spend_tier
ORDER BY order_month DESC, spend_tier ASC;

-- 11. NTILE for Segmentation
-- Divide customers into 4 quartiles based on total lifetime value.

WITH customer_ltv AS (
    SELECT 
        o.customer_id,
        ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS total_value
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY o.customer_id
),
customer_quartiles AS (
    SELECT 
        customer_id,
        total_value,
        NTILE(4) OVER (ORDER BY total_value DESC) AS quartile
    FROM customer_ltv
)
SELECT 
    customer_id,
    total_value,
    quartile,
    CASE 
        WHEN quartile = 1 THEN 'Platinum'
        WHEN quartile = 2 THEN 'Gold'
        WHEN quartile = 3 THEN 'Silver'
        ELSE 'Bronze'
    END AS quartile_label
FROM customer_quartiles
ORDER BY total_value DESC;

-- 12. Year-over-Year Comparison
-- Compare each month's revenue with same month previous year.
WITH monthly_revenue AS (
    SELECT 
        CAST(strftime('%Y', order_date) AS INTEGER) AS r_year,
        CAST(strftime('%m', order_date) AS INTEGER) AS r_month,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY r_year, r_month
),
yoy_revenue AS (
    SELECT 
        r_year,
        r_month,
        ROUND(revenue, 2) AS revenue,
        ROUND(LAG(revenue, 1) OVER (PARTITION BY r_month ORDER BY r_year), 2) AS prev_year_revenue
    FROM monthly_revenue
)
SELECT 
    r_year AS year,
    printf('%02d', r_month) AS month,
    revenue,
    COALESCE(prev_year_revenue, 0.0) AS prev_year_revenue,
    CASE 
        WHEN prev_year_revenue IS NULL OR prev_year_revenue = 0 THEN 'N/A'
        ELSE ROUND(((revenue - prev_year_revenue) * 100.0 / prev_year_revenue), 2) || '%'
    END AS yoy_growth_percent
FROM yoy_revenue
ORDER BY year DESC, month DESC;

-- 13. First/Last Value Analysis
-- Show each customer's first and last purchased categories.

WITH item_categories AS (
    SELECT 
        o.customer_id,
        o.order_date,
        p.category,
        FIRST_VALUE(p.category) OVER (
            PARTITION BY o.customer_id 
            ORDER BY o.order_date ASC, oi.item_id ASC
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS first_category,
        LAST_VALUE(p.category) OVER (
            PARTITION BY o.customer_id 
            ORDER BY o.order_date ASC, oi.item_id ASC
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS last_category
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
)
SELECT DISTINCT 
    customer_id,
    first_category,
    last_category,
    CASE 
        WHEN first_category = last_category THEN 'No'
        ELSE 'Yes'
    END AS category_shift
FROM item_categories
ORDER BY customer_id;

-- 14. Cumulative Distribution
.
WITH customer_revenue AS (
    SELECT 
        o.customer_id,
        ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS customer_rev
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY o.customer_id
),
overall_revenue AS (
    SELECT SUM(customer_rev) AS total_rev FROM customer_revenue
),
cumulative_revs AS (
    SELECT 
        c.customer_id,
        c.customer_rev AS revenue,
        ROUND(SUM(c.customer_rev) OVER (ORDER BY c.customer_rev DESC), 2) AS cumulative_revenue
    FROM customer_revenue c
)
SELECT 
    cr.customer_id,
    cr.revenue,
    cr.cumulative_revenue,
    ROUND((cr.cumulative_revenue * 100.0 / o.total_rev), 2) AS cumulative_percent
FROM cumulative_revs cr
CROSS JOIN overall_revenue o
ORDER BY cr.revenue DESC;

-- 16. Self-Join for Co-Purchase Analysis
-- Find products frequently bought together.
SELECT 
    p1.product_name AS product_a,
    p2.product_name AS product_b,
    COUNT(*) AS times_bought_together
FROM order_items oi1
JOIN order_items oi2 ON oi1.order_id = oi2.order_id AND oi1.product_id < oi2.product_id
JOIN products p1 ON oi1.product_id = p1.product_id
JOIN products p2 ON oi2.product_id = p2.product_id
WHERE p1.product_name != p2.product_name
GROUP BY product_a, product_b
ORDER BY times_bought_together DESC, product_a, product_b;
