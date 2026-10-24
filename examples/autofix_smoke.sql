SELECT *
FROM orders o
WHERE YEAR(o.order_date) = 2026
  AND o.customer_id IN (
      SELECT c.id 
      FROM customers c 
      WHERE c.country = 'España'
  )
  AND (o.status = 'PENDING' OR o.status = 'PROCESSING');