-- Expected: no issues (COUNT(*) is intentional; trailing wildcard is index-friendly)
SELECT customer_id, COUNT(*) AS order_count
FROM orders
WHERE customer_name LIKE 'Garcia%'
GROUP BY customer_id;
