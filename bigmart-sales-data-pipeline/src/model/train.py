"""Train a sales prediction model on data read from the warehouse.

The model is compared against a simple baseline (predict the average), so
the reported improvement is meaningful.

    python -m src.model.train
"""
import json
import logging
import sqlite3

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from src.pipeline import config

log = logging.getLogger("model")

QUERY = """
SELECT f.sales, f.mrp, f.visibility,
       i.weight_kg, i.fat_content, i.item_type, i.item_category,
       o.outlet_age, o.outlet_size, o.location_tier, o.outlet_type
FROM fact_sales f
JOIN dim_item   i ON i.item_id   = f.item_id
JOIN dim_outlet o ON o.outlet_id = f.outlet_id
"""
NUMERIC = ["mrp", "visibility", "weight_kg", "outlet_age"]
CATEGORICAL = ["fat_content", "item_type", "item_category", "outlet_size", "location_tier", "outlet_type"]


def evaluate(name: str, y_true, y_pred) -> dict:
    return {
        "model": name,
        "rmse": round(float(np.sqrt(mean_squared_error(y_true, y_pred))), 2),
        "mae": round(float(mean_absolute_error(y_true, y_pred)), 2),
        "r2": round(float(r2_score(y_true, y_pred)), 3),
    }


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)-7s %(name)s: %(message)s")
    with sqlite3.connect(config.WAREHOUSE) as conn:
        df = pd.read_sql_query(QUERY, conn)
    if df.empty:
        raise SystemExit("Warehouse is empty. Run the pipeline first: python -m src.pipeline.run")

    X, y = df[NUMERIC + CATEGORICAL], df["sales"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = Pipeline([
        ("prep", ColumnTransformer([
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
            ("num", "passthrough", NUMERIC),
        ])),
        ("rf", RandomForestRegressor(n_estimators=200, min_samples_leaf=5, random_state=42, n_jobs=-1)),
    ])
    model.fit(X_train, y_train)
    baseline = DummyRegressor(strategy="mean").fit(X_train, y_train)

    results = [
        evaluate("baseline_mean", y_test, baseline.predict(X_test)),
        evaluate("random_forest", y_test, model.predict(X_test)),
    ]
    for r in results:
        log.info("%-14s RMSE=%-9s MAE=%-9s R2=%s", r["model"], r["rmse"], r["mae"], r["r2"])

    config.REPORTS_DIR.mkdir(exist_ok=True)
    (config.REPORTS_DIR / "model_metrics.json").write_text(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
