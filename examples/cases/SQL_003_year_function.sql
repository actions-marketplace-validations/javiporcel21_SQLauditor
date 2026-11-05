-- Expected: SQL_003 (HIGH, diagnostic only; no autofix)
SELECT id, order_date
FROM orders
WHERE YEAR(order_date) = 2026;
