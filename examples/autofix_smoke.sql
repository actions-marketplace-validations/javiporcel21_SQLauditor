SELECT id
FROM orders
WHERE status = 'pending' OR status = 'paid';
