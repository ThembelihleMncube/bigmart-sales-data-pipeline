"""Command-line entry point.

    python -m src.pipeline.run                 # uses data/raw/bigmart_sales.csv if present
    python -m src.pipeline.run --source data/sample/bigmart_sample.csv
"""
import argparse
import logging
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from . import config
from .extract import extract
from .load import create_schema, load
from .quality import validate
from .transform import transform

log = logging.getLogger("pipeline")


def run(source: Path, warehouse: Path) -> int:
    run_id = uuid.uuid4().hex[:8]
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    warehouse.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(warehouse)
    create_schema(conn, config.SCHEMA_SQL)

    rows_in = rows_out = 0
    status, error = "success", None
    try:
        raw = extract(source)
        rows_in = len(raw)
        clean = transform(raw)
        validate(clean, config.REPORTS_DIR / f"dq_report_{run_id}.json")
        rows_out = load(clean, conn)
    except Exception as exc:
        status, error = "failed", str(exc)
        log.error("Run %s failed: %s", run_id, exc)
        raise
    finally:
        with conn:
            conn.execute(
                "INSERT INTO etl_run_log VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (run_id, started, datetime.now(timezone.utc).isoformat(timespec="seconds"),
                 str(source), rows_in, rows_out, status, error),
            )
        conn.close()
    log.info("Run %s finished: %d rows in, %d rows loaded", run_id, rows_in, rows_out)
    return rows_out


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-7s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(description="Run the BigMart ETL pipeline")
    default = config.RAW_DATA if config.RAW_DATA.exists() else config.SAMPLE_DATA
    parser.add_argument("--source", type=Path, default=default)
    parser.add_argument("--warehouse", type=Path, default=config.WAREHOUSE)
    args = parser.parse_args()
    run(args.source, args.warehouse)


if __name__ == "__main__":
    main()
