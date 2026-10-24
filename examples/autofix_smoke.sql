WITH customer_totals AS (
    SELECT 
        customer_id,
        SUM(total_amount) AS total_spent,
        COUNT(id) AS total_orders
    FROM orders
    WHERE order_date >= '2026-01-01' 
      AND order_date < '2027-01-01'
    GROUP BY customer_id
)
SELECT 
    customer_id,
    total_spent,
    total_orders,
    CASE 
        WHEN total_spent > 1000 THEN 'VIP'
        ELSE 'STANDARD'
    END AS customer_tier
FROM customer_totals
WHERE total_orders >= 2;