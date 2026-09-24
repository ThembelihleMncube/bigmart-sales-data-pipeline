import pandas as pd
import pytest


@pytest.fixture
def raw_df() -> pd.DataFrame:
    """A tiny hand-made dataset containing each data problem the pipeline fixes."""
    return pd.DataFrame({
        "Item_Identifier": ["FDA01", "FDA01", "DRB02", "NCC03", "NCC03"],
        "Item_Weight": [9.3, None, 5.9, None, None],
        "Item_Fat_Content": ["Low Fat", "LF", "reg", "Low Fat", "low fat"],
        "Item_Visibility": [0.016, 0.0, 0.019, 0.0, 0.05],
        "Item_Type": ["Dairy", "Dairy", "Soft Drinks", "Household", "Household"],
        "Item_MRP": [249.8, 249.8, 48.3, 141.6, 141.6],
        "Outlet_Identifier": ["OUT049", "OUT018", "OUT018", "OUT049", "OUT010"],
        "Outlet_Establishment_Year": [1999, 2009, 2009, 1999, 1998],
        "Outlet_Size": ["Medium", "Medium", "Medium", "Medium", None],
        "Outlet_Location_Type": ["Tier 1", "Tier 3", "Tier 3", "Tier 1", "Tier 3"],
        "Outlet_Type": ["Supermarket Type1", "Supermarket Type2", "Supermarket Type2",
                        "Supermarket Type1", "Grocery Store"],
        "Item_Outlet_Sales": [3735.1, 443.4, 2097.3, 732.4, 994.7],
    })
