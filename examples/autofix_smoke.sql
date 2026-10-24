WITH recent_orders AS (
    SELECT id, customer_id, status, order_date, total_amount
    FROM orders
    WHERE status = 'PENDING' OR status = 'PROCESSING'
    ORDER BY order_date DESC
)
SELECT id, customer_id, status, order_date, total_amount
FROM recent_orders;
