"""Transform step: clean the known data problems in the BigMart dataset.

Each function does one job so it can be tested on its own.
"""
import logging

import pandas as pd

from .config import REFERENCE_YEAR

log = logging.getLogger(__name__)

FAT_CONTENT_MAP = {"low fat": "Low Fat", "lf": "Low Fat", "reg": "Regular", "regular": "Regular"}
CATEGORY_BY_PREFIX = {"FD": "Food", "DR": "Drinks", "NC": "Non-Consumable"}


def standardise_fat_content(df: pd.DataFrame) -> pd.DataFrame:
    """'LF', 'low fat' and 'Low Fat' are the same value; so are 'reg' and 'Regular'."""
    df = df.copy()
    key = df["Item_Fat_Content"].astype(str).str.strip().str.lower()
    df["Item_Fat_Content"] = key.map(FAT_CONTENT_MAP).fillna(df["Item_Fat_Content"])
    return df


def add_item_category(df: pd.DataFrame) -> pd.DataFrame:
    """The first two letters of Item_Identifier give a broad category (FD/DR/NC)."""
    df = df.copy()
    df["Item_Category"] = df["Item_Identifier"].str[:2].map(CATEGORY_BY_PREFIX).fillna("Unknown")
    # Fat content has no meaning for non-consumables such as household products.
    df.loc[df["Item_Category"] == "Non-Consumable", "Item_Fat_Content"] = "Non-Edible"
    return df


def impute_item_weight(df: pd.DataFrame) -> pd.DataFrame:
    """An item weighs the same in every outlet, so fill gaps with that item's
    known weight, and fall back to the overall median."""
    df = df.copy()
    before = int(df["Item_Weight"].isna().sum())
    item_mean = df.groupby("Item_Identifier")["Item_Weight"].transform("mean")
    df["Item_Weight"] = df["Item_Weight"].fillna(item_mean).fillna(df["Item_Weight"].median())
    log.info("Imputed %d missing Item_Weight values", before)
    return df


def fix_zero_visibility(df: pd.DataFrame) -> pd.DataFrame:
    """A product that is on sale cannot have 0% shelf visibility; treat 0 as
    missing and replace it with that item's average visibility elsewhere."""
    df = df.copy()
    zero = df["Item_Visibility"] == 0
    non_zero = df["Item_Visibility"].where(~zero)
    item_mean = non_zero.groupby(df["Item_Identifier"]).transform("mean")
    df["Item_Visibility"] = non_zero.fillna(item_mean).fillna(non_zero.median())
    log.info("Replaced %d zero Item_Visibility values", int(zero.sum()))
    return df


def impute_outlet_size(df: pd.DataFrame) -> pd.DataFrame:
    """Fill a missing outlet size with the most common size for that outlet type."""
    df = df.copy()
    before = int(df["Outlet_Size"].isna().sum())

    def mode_or_default(s: pd.Series) -> str:
        m = s.dropna().mode()
        return m.iloc[0] if not m.empty else "Medium"

    mode_by_type = df.groupby("Outlet_Type")["Outlet_Size"].agg(mode_or_default)
    df["Outlet_Size"] = df["Outlet_Size"].fillna(df["Outlet_Type"].map(mode_by_type))
    log.info("Imputed %d missing Outlet_Size values", before)
    return df


def add_outlet_age(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Outlet_Age"] = REFERENCE_YEAR - df["Outlet_Establishment_Year"]
    return df


def transform(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates()
    for step in (standardise_fat_content, add_item_category, impute_item_weight,
                 fix_zero_visibility, impute_outlet_size, add_outlet_age):
        df = step(df)
    df["Item_Weight"] = df["Item_Weight"].round(3)
    df["Item_Visibility"] = df["Item_Visibility"].round(6)
    log.info("Transformed %d rows", len(df))
    return df.reset_index(drop=True)
