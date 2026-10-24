WITH ranked_orders AS (
    SELECT 
        customer_id,
        id AS order_id,
        order_date,
        total_amount,
        SUM(total_amount) OVER(PARTITION BY customer_id) AS lifetime_customer_spent,
        ROW_NUMBER() OVER(PARTITION BY customer_id ORDER BY order_date DESC) as rn
    FROM orders
    WHERE order_date >= '2026-01-01' 
      AND order_date < '2027-01-01'
)
SELECT 
    customer_id,
    order_id,
    order_date,
    total_amount,
    lifetime_customer_spent
FROM ranked_orders
WHERE rn = 1
  AND lifetime_customer_spent > 500;