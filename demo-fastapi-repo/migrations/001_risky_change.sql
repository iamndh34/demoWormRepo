ALTER TABLE users DROP COLUMN email;

UPDATE orders SET status = 'processed' WHERE created_at < '2020-01-01';
