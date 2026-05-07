-- MIGRATION ERROR: Dropping critical column without backup
ALTER TABLE users DROP COLUMN email;

-- MIGRATION ERROR: Long running operation on large table without batching
UPDATE orders SET status = 'processed' WHERE created_at < '2020-01-01';
