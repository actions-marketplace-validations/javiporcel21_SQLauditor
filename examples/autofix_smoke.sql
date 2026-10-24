WITH recent_orders AS (
  SELECT
    id,
    status
  FROM orders
  WHERE
    status IN ('pending', 'paid')
)
SELECT
  id
FROM recent_orders
