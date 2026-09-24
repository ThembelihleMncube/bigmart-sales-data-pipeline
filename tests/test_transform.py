from src.pipeline.transform import (
    add_item_category,
    fix_zero_visibility,
    impute_item_weight,
    impute_outlet_size,
    standardise_fat_content,
    transform,
)


def test_fat_content_spellings_are_unified(raw_df):
    out = standardise_fat_content(raw_df)
    assert set(out["Item_Fat_Content"]) == {"Low Fat", "Regular"}


def test_non_consumables_are_marked_non_edible(raw_df):
    out = add_item_category(standardise_fat_content(raw_df))
    nc = out[out["Item_Identifier"].str.startswith("NC")]
    assert (nc["Item_Fat_Content"] == "Non-Edible").all()
    assert (nc["Item_Category"] == "Non-Consumable").all()


def test_weight_uses_same_item_before_median(raw_df):
    out = impute_item_weight(raw_df)
    assert out["Item_Weight"].notna().all()
    # FDA01 is 9.3 kg in one outlet, so its missing weight must also be 9.3
    assert (out.loc[out["Item_Identifier"] == "FDA01", "Item_Weight"] == 9.3).all()


def test_zero_visibility_is_replaced(raw_df):
    out = fix_zero_visibility(raw_df)
    assert (out["Item_Visibility"] > 0).all()
    assert out.loc[1, "Item_Visibility"] == 0.016  # FDA01's visibility elsewhere


def test_outlet_size_filled_from_outlet_type(raw_df):
    out = impute_outlet_size(raw_df)
    assert out["Outlet_Size"].notna().all()


def test_transform_does_not_change_row_count(raw_df):
    assert len(transform(raw_df)) == len(raw_df)
    assert transform(raw_df).notna().all().all()
