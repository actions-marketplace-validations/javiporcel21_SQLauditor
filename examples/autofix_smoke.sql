SELECT 
    customer_id,
    COUNT(id) AS total_orders,
    AVG(total_amount) AS avg_ticket
FROM orders
WHERE status <> 'CANCELLED'
  AND order_date LIKE '2026%'
GROUP BY customer_id
HAVING AVG(total_amount) > 100;