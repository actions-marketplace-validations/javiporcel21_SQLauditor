SELECT 
    id,
    customer_id,
    order_date,
    status,
    total_amount
FROM orders
WHERE order_date >= '2026-01-01' 
  AND order_date < '2027-01-01'
  AND customer_id IN (
      SELECT id 
      FROM customers 
      WHERE country = 'España'
  )
  AND status IN ('PENDING', 'PROCESSING');