WITH recent_orders AS (
    SELECT id, status
    FROM orders
    WHERE status = 'pending' OR status = 'paid'
    ORDER BY id
)
SELECT id
FROM recent_orders;
