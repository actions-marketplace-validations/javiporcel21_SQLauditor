WITH recent_orders AS (
    SELECT id, customer_id, order_date, status, total_amount
    FROM sales.orders
    WHERE YEAR(order_date) = 2026
      AND (status = 'PAID' OR status = 'SHIPPED')
    ORDER BY order_date DESC
)
SELECT *
FROM recent_orders
WHERE customer_name LIKE '%garcia';
