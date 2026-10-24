-- Expected: SQL_004 (HIGH, manual fix)
SELECT id, name
FROM customers
WHERE name LIKE '%garcia';
