"""Load step: write clean data into a star schema in SQLite.

Loads are idempotent: re-running the pipeline on the same file replaces rows
by their natural keys instead of creating duplicates.
"""
import logging
import sqlite3
from pathlib import Path

import pandas as pd

log = logging.getLogger(__name__)


def create_schema(conn: sqlite3.Connection, schema_sql: Path) -> None:
    conn.executescript(schema_sql.read_text())


def _upsert(conn: sqlite3.Connection, table: str, rows: pd.DataFrame) -> int:
    cols = list(rows.columns)
    sql = f"INSERT OR REPLACE INTO {table} ({', '.join(cols)}) VALUES ({', '.join('?' * len(cols))})"
    records = [tuple(v.item() if hasattr(v, "item") else v for v in r)
               for r in rows.itertuples(index=False)]
    conn.executemany(sql, records)
    return len(records)


def load(df: pd.DataFrame, conn: sqlite3.Connection) -> int:
    dim_item = (
        df[["Item_Identifier", "Item_Weight", "Item_Fat_Content", "Item_Type", "Item_Category"]]
        .drop_duplicates("Item_Identifier")
        .rename(columns={
            "Item_Identifier": "item_id", "Item_Weight": "weight_kg",
            "Item_Fat_Content": "fat_content", "Item_Type": "item_type",
            "Item_Category": "item_category",
        })
    )
    dim_outlet = (
        df[["Outlet_Identifier", "Outlet_Establishment_Year", "Outlet_Age", "Outlet_Size",
            "Outlet_Location_Type", "Outlet_Type"]]
        .drop_duplicates("Outlet_Identifier")
        .rename(columns={
            "Outlet_Identifier": "outlet_id", "Outlet_Establishment_Year": "established_year",
            "Outlet_Age": "outlet_age", "Outlet_Size": "outlet_size",
            "Outlet_Location_Type": "location_tier", "Outlet_Type": "outlet_type",
        })
    )
    fact = df[["Item_Identifier", "Outlet_Identifier", "Item_MRP", "Item_Visibility",
               "Item_Outlet_Sales"]].rename(columns={
        "Item_Identifier": "item_id", "Outlet_Identifier": "outlet_id",
        "Item_MRP": "mrp", "Item_Visibility": "visibility", "Item_Outlet_Sales": "sales",
    })

    with conn:  # one transaction: all tables load, or none do
        n_items = _upsert(conn, "dim_item", dim_item)
        n_outlets = _upsert(conn, "dim_outlet", dim_outlet)
        n_facts = _upsert(conn, "fact_sales", fact)

    log.info("Loaded %d items, %d outlets, %d sales rows", n_items, n_outlets, n_facts)
    return n_facts
