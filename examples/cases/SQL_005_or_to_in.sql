-- Expected: SQL_005 (LOW, autofix rewrites OR as IN)
SELECT id, status
FROM orders
WHERE status = 'PENDING'
   OR status = 'PROCESSING';
