"""Central settings for the pipeline. Paths are relative to the repo root."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

RAW_DATA = ROOT / "data" / "raw" / "bigmart_sales.csv"
SAMPLE_DATA = ROOT / "data" / "sample" / "bigmart_sample.csv"
WAREHOUSE = ROOT / "data" / "warehouse.db"
SCHEMA_SQL = ROOT / "sql" / "schema.sql"
REPORTS_DIR = ROOT / "reports"

# The BigMart data describes sales in 2013; outlet age is measured from here.
REFERENCE_YEAR = 2013

REQUIRED_COLUMNS = [
    "Item_Identifier", "Item_Weight", "Item_Fat_Content", "Item_Visibility",
    "Item_Type", "Item_MRP", "Outlet_Identifier", "Outlet_Establishment_Year",
    "Outlet_Size", "Outlet_Location_Type", "Outlet_Type", "Item_Outlet_Sales",
]
