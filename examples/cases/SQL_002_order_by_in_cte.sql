-- Expected: SQL_002 (MEDIUM, autofix removes the inner ORDER BY)
WITH recent_orders AS (
    SELECT id, customer_id, created_at
    FROM orders
    ORDER BY created_at DESC
)
SELECT id, customer_id, created_at
FROM recent_orders;
