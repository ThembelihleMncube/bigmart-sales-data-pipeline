"""Run a SQL file against the warehouse and print the result as a table.

    python scripts/run_query.py sql/analytics/01_sales_by_outlet_type.sql
"""
import sqlite3
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Usage: python scripts/run_query.py <path-to-sql-file>")
    sql = Path(sys.argv[1]).read_text()
    with sqlite3.connect(ROOT / "data" / "warehouse.db") as conn:
        print(pd.read_sql_query(sql, conn).to_string(index=False))


if __name__ == "__main__":
    main()
