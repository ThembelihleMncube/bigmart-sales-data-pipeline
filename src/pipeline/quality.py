"""Data quality checks that run after transform and before load.

A failed 'error' check stops the pipeline so bad data never reaches the
warehouse. Every run writes a report so results can be reviewed later.
"""
import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd

log = logging.getLogger(__name__)

VALID_FAT = {"Low Fat", "Regular", "Non-Edible"}
VALID_SIZES = {"Small", "Medium", "High"}
VALID_LOCATIONS = {"Tier 1", "Tier 2", "Tier 3"}


@dataclass
class CheckResult:
    name: str
    passed: bool
    failing_rows: int
    severity: str = "error"


class DataQualityError(RuntimeError):
    pass


def _check(name: str, failing: pd.Series, severity: str = "error") -> CheckResult:
    n = int(failing.sum())
    return CheckResult(name=name, passed=n == 0, failing_rows=n, severity=severity)


def run_checks(df: pd.DataFrame) -> list[CheckResult]:
    sales_limit = 3 * df["Item_Outlet_Sales"].quantile(0.99)
    return [
        _check("no_nulls", df.isna().any(axis=1)),
        _check("unique_item_outlet", df.duplicated(["Item_Identifier", "Outlet_Identifier"], keep=False)),
        _check("mrp_positive", df["Item_MRP"] <= 0),
        _check("sales_not_negative", df["Item_Outlet_Sales"] < 0),
        _check("visibility_between_0_and_1", ~df["Item_Visibility"].between(0, 1)),
        _check("fat_content_in_domain", ~df["Item_Fat_Content"].isin(VALID_FAT)),
        _check("outlet_size_in_domain", ~df["Outlet_Size"].isin(VALID_SIZES)),
        _check("location_in_domain", ~df["Outlet_Location_Type"].isin(VALID_LOCATIONS)),
        # Very high sales are possible, so this only warns.
        _check("sales_outliers", df["Item_Outlet_Sales"] > sales_limit, "warning"),
    ]


def validate(df: pd.DataFrame, report_path: Path | None = None) -> list[CheckResult]:
    results = run_checks(df)
    for r in results:
        level = logging.INFO if r.passed else (logging.WARNING if r.severity == "warning" else logging.ERROR)
        outcome = "PASS" if r.passed else "FAIL"
        log.log(level, "DQ %-28s %s (%d failing rows)", r.name, outcome, r.failing_rows)

    if report_path:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps([asdict(r) for r in results], indent=2))

    errors = [r.name for r in results if not r.passed and r.severity == "error"]
    if errors:
        raise DataQualityError(f"Data quality checks failed: {errors}")
    return results
