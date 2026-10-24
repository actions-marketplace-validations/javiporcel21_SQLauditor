-- Expected: SQL_003 (HIGH, autofix rewrites YEAR() as a date range)
SELECT id, order_date
FROM orders
WHERE YEAR(order_date) = 2026;
