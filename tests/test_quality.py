import pytest

from src.pipeline.quality import DataQualityError, validate
from src.pipeline.transform import transform


def test_clean_data_passes(raw_df):
    results = validate(transform(raw_df))
    assert all(r.passed for r in results if r.severity == "error")


def test_negative_sales_fail(raw_df):
    df = transform(raw_df)
    df.loc[0, "Item_Outlet_Sales"] = -10
    with pytest.raises(DataQualityError, match="sales_not_negative"):
        validate(df)


def test_duplicate_item_outlet_fails(raw_df):
    df = transform(raw_df)
    df.loc[1, "Outlet_Identifier"] = df.loc[0, "Outlet_Identifier"]
    with pytest.raises(DataQualityError, match="unique_item_outlet"):
        validate(df)


def test_report_is_written(raw_df, tmp_path):
    report = tmp_path / "dq.json"
    validate(transform(raw_df), report)
    assert report.exists()
