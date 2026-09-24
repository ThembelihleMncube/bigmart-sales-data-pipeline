"""End-to-end tests: run the whole pipeline into a temporary database."""
import sqlite3

import pytest

from src.pipeline.extract import SchemaError, extract
from src.pipeline.quality import DataQualityError
from src.pipeline.run import run


@pytest.fixture
def source(raw_df, tmp_path):
    path = tmp_path / "raw.csv"
    raw_df.to_csv(path, index=False)
    return path


def test_pipeline_loads_star_schema(source, tmp_path):
    db = tmp_path / "wh.db"
    assert run(source, db) == 5
    with sqlite3.connect(db) as conn:
        assert conn.execute("SELECT COUNT(*) FROM dim_item").fetchone()[0] == 3
        assert conn.execute("SELECT COUNT(*) FROM dim_outlet").fetchone()[0] == 3
        assert conn.execute("SELECT status FROM etl_run_log").fetchone()[0] == "success"


def test_rerun_is_idempotent(source, tmp_path):
    db = tmp_path / "wh.db"
    run(source, db)
    run(source, db)
    with sqlite3.connect(db) as conn:
        assert conn.execute("SELECT COUNT(*) FROM fact_sales").fetchone()[0] == 5
        assert conn.execute("SELECT COUNT(*) FROM etl_run_log").fetchone()[0] == 2


def test_failed_run_is_logged(raw_df, tmp_path):
    bad = tmp_path / "bad.csv"
    raw_df.assign(Item_MRP=-1).to_csv(bad, index=False)
    db = tmp_path / "wh.db"
    with pytest.raises(DataQualityError):
        run(bad, db)
    with sqlite3.connect(db) as conn:
        assert conn.execute("SELECT status FROM etl_run_log").fetchone()[0] == "failed"
        assert conn.execute("SELECT COUNT(*) FROM fact_sales").fetchone()[0] == 0


def test_missing_column_is_rejected(raw_df, tmp_path):
    path = tmp_path / "missing.csv"
    raw_df.drop(columns=["Item_MRP"]).to_csv(path, index=False)
    with pytest.raises(SchemaError):
        extract(path)
