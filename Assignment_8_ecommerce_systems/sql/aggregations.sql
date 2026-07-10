
-- BASIC QUERIES

-- 1. Total revenue per category
SELECT 
    p.category,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS total_revenue
FROM 
    order_items oi
JOIN 
    products p ON oi.product_id = p.product_id
GROUP BY 
    p.category
ORDER BY 
    total_revenue DESC;


-- 2. Top 10 customers by total order value 
SELECT 
    c.customer_id,
    c.customer_name,
    c.customer_type,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS total_order_value
FROM 
    order_items oi
JOIN 
    orders o ON oi.order_id = o.order_id
JOIN 
    customers c ON o.customer_id = c.customer_id
GROUP BY 
    c.customer_id, 
    c.customer_name,
    c.customer_type
ORDER BY 
    total_order_value DESC
LIMIT 10;

-- 3. Month-wise order count for the last 12 months

SELECT 
    strftime('%Y-%m', o.order_date) AS order_month,
    COUNT(DISTINCT o.order_id) AS total_orders
FROM 
    orders o
WHERE 
    o.order_date >= date((SELECT MAX(order_date) FROM orders), '-12 months')
GROUP BY 
    order_month
ORDER BY 
    order_month DESC;

-- INTERMEDIATE QUERIES
-- 4. Find customers who placed orders but never had any item delivered

SELECT DISTINCT 
    c.customer_id, 
    c.customer_name,
    c.email
FROM 
    customers c
JOIN 
    orders o ON c.customer_id = o.customer_id
WHERE 
    c.customer_id NOT IN (
        SELECT DISTINCT customer_id 
        FROM orders 
        WHERE status = 'DELIVERED'
    )
ORDER BY 
    c.customer_id;


-- 5. Products that were ordered but had more returns than purchases
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    SUM(CASE WHEN oi.quantity > 0 THEN oi.quantity ELSE 0 END) AS total_purchased,
    SUM(CASE WHEN oi.quantity < 0 THEN -oi.quantity ELSE 0 END) AS total_returned
FROM 
    order_items oi
JOIN 
    products p ON oi.product_id = p.product_id
GROUP BY 
    p.product_id, 
    p.product_name,
    p.category
HAVING 
    total_returned > total_purchased;


-- 6. Calculate the return rate (returned items / total items purchased) per category
SELECT 
    p.category,
    SUM(CASE WHEN oi.quantity > 0 THEN oi.quantity ELSE 0 END) AS items_purchased,
    SUM(CASE WHEN oi.quantity < 0 THEN -oi.quantity ELSE 0 END) AS items_returned,
    ROUND(
        SUM(CASE WHEN oi.quantity < 0 THEN -oi.quantity ELSE 0 END) * 100.0 / 
        NULLIF(SUM(CASE WHEN oi.quantity > 0 THEN oi.quantity ELSE 0 END), 0), 
        2
    ) AS return_rate_percent
FROM 
    order_items oi
JOIN 
    products p ON oi.product_id = p.product_id
GROUP BY 
    p.category
ORDER BY 
    return_rate_percent DESC;
