-- Expected: SQL_004 (HIGH, manual fix)
SELECT orders.id, customers.name
FROM orders
JOIN customers;
