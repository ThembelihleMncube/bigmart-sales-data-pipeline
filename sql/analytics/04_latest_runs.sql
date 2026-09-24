-- Operational view: the 10 most recent pipeline runs.
SELECT run_id, started_at, status, rows_in, rows_loaded, error_message
FROM etl_run_log
ORDER BY started_at DESC
LIMIT 10;
