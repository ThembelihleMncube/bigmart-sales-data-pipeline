"""Generate a small SYNTHETIC dataset with the same columns and the same data
problems as the real BigMart file, so the pipeline and tests run without
downloading anything. The numbers are made up; use the real dataset for analysis.

    python scripts/generate_sample_data.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
OUT = Path(__file__).resolve().parents[1] / "data" / "sample" / "bigmart_sample.csv"

ITEM_TYPES = {
    "FD": ["Dairy", "Snack Foods", "Fruits and Vegetables", "Frozen Foods", "Breads", "Meat", "Canned"],
    "DR": ["Soft Drinks", "Hard Drinks"],
    "NC": ["Household", "Health and Hygiene", "Others"],
}
OUTLETS = [  # id, year, size, tier, type
    ("OUT010", 1998, None,     "Tier 3", "Grocery Store"),
    ("OUT013", 1987, "High",   "Tier 3", "Supermarket Type1"),
    ("OUT017", 2007, None,     "Tier 2", "Supermarket Type1"),
    ("OUT018", 2009, "Medium", "Tier 3", "Supermarket Type2"),
    ("OUT019", 1985, "Small",  "Tier 1", "Grocery Store"),
    ("OUT027", 1985, "Medium", "Tier 3", "Supermarket Type3"),
    ("OUT035", 2004, "Small",  "Tier 2", "Supermarket Type1"),
    ("OUT045", 2002, None,     "Tier 2", "Supermarket Type1"),
    ("OUT046", 1997, "Small",  "Tier 1", "Supermarket Type1"),
    ("OUT049", 1999, "Medium", "Tier 1", "Supermarket Type1"),
]
TYPE_FACTOR = {"Grocery Store": 0.25, "Supermarket Type1": 1.0,
               "Supermarket Type2": 0.9, "Supermarket Type3": 1.6}
FAT_SPELLINGS = ["Low Fat", "Low Fat", "Low Fat", "LF", "low fat", "Regular", "Regular", "reg"]


def make_items(n: int) -> pd.DataFrame:
    rows = []
    for i in range(n):
        prefix = rng.choice(["FD", "FD", "FD", "DR", "NC"])
        rows.append({
            "Item_Identifier": f"{prefix}{chr(65 + i % 26)}{i:02d}",
            "Item_Weight": round(float(rng.uniform(4.5, 21.5)), 3),
            "Item_Fat_Content": rng.choice(FAT_SPELLINGS),
            "Item_Type": rng.choice(ITEM_TYPES[prefix]),
            "Item_MRP": round(float(rng.uniform(31, 267)), 4),
            "base_visibility": float(rng.uniform(0.01, 0.2)),
        })
    return pd.DataFrame(rows)


def main(n_items: int = 150) -> None:
    items = make_items(n_items)
    rows = []
    for _, item in items.iterrows():
        for oid, year, size, tier, otype in OUTLETS:
            if rng.random() < 0.3:  # not every item is stocked in every outlet
                continue
            visibility = round(item.base_visibility * rng.uniform(0.7, 1.3), 6)
            if rng.random() < 0.06:  # the real data has zeros that must be cleaned
                visibility = 0.0
            sales = item.Item_MRP * TYPE_FACTOR[otype] * rng.uniform(8, 18)
            rows.append({
                "Item_Identifier": item.Item_Identifier,
                "Item_Weight": item.Item_Weight if rng.random() > 0.17 else np.nan,
                "Item_Fat_Content": item.Item_Fat_Content,
                "Item_Visibility": visibility,
                "Item_Type": item.Item_Type,
                "Item_MRP": item.Item_MRP,
                "Outlet_Identifier": oid,
                "Outlet_Establishment_Year": year,
                "Outlet_Size": size,
                "Outlet_Location_Type": tier,
                "Outlet_Type": otype,
                "Item_Outlet_Sales": round(float(sales), 4),
            })
    df = pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"Wrote {len(df)} synthetic rows to {OUT}")


if __name__ == "__main__":
    main()
