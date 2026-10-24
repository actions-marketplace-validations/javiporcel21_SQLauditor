WITH recent_orders AS (
  SELECT
    id,
    customer_id,
    status,
    order_date,
    total_amount
  FROM orders
  WHERE
    status IN ('PENDING', 'PROCESSING')
)
SELECT
  id,
  customer_id,
  status,
  order_date,
  total_amount
FROM recent_orders
