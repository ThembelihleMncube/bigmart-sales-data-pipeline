-- Star schema for BigMart sales.
-- One fact table (a product's sales at one outlet) and two dimensions.

CREATE TABLE IF NOT EXISTS dim_item (
    item_id        TEXT PRIMARY KEY,
    weight_kg      REAL NOT NULL,
    fat_content    TEXT NOT NULL CHECK (fat_content IN ('Low Fat', 'Regular', 'Non-Edible')),
    item_type      TEXT NOT NULL,
    item_category  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_outlet (
    outlet_id         TEXT PRIMARY KEY,
    established_year  INTEGER NOT NULL,
    outlet_age        INTEGER NOT NULL,
    outlet_size       TEXT NOT NULL,
    location_tier     TEXT NOT NULL,
    outlet_type       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_sales (
    item_id     TEXT NOT NULL REFERENCES dim_item (item_id),
    outlet_id   TEXT NOT NULL REFERENCES dim_outlet (outlet_id),
    mrp         REAL NOT NULL CHECK (mrp > 0),
    visibility  REAL NOT NULL CHECK (visibility BETWEEN 0 AND 1),
    sales       REAL NOT NULL CHECK (sales >= 0),
    PRIMARY KEY (item_id, outlet_id)
);

CREATE INDEX IF NOT EXISTS ix_fact_sales_outlet ON fact_sales (outlet_id);

-- Audit trail: one row per pipeline run, successful or not.
CREATE TABLE IF NOT EXISTS etl_run_log (
    run_id        TEXT PRIMARY KEY,
    started_at    TEXT NOT NULL,
    finished_at   TEXT NOT NULL,
    source_file   TEXT NOT NULL,
    rows_in       INTEGER NOT NULL,
    rows_loaded   INTEGER NOT NULL,
    status        TEXT NOT NULL,
    error_message TEXT
);
