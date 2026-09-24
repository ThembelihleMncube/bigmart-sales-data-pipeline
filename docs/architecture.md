# Design decisions

## Why a star schema?
Sales are the measurable events (facts); items and outlets describe them (dimensions). Splitting them avoids repeating outlet details on every sales row, and makes analytical queries simple joins. This is the standard layout for reporting tools such as Power BI.

## Why validate before loading?
If bad data reaches the warehouse, every report and model built on it is wrong, and it is hard to undo. Checking first means a failed run leaves the warehouse exactly as it was.

Checks have two severities:
- **error**: stops the run (for example, negative sales or duplicate keys).
- **warning**: logged but allowed (for example, unusually high sales, which can be real).

## Why idempotent loads?
Pipelines get re-run after failures or fixes. `INSERT OR REPLACE` on natural keys (`item_id`, `outlet_id`) means running the same file twice gives the same result, not double the rows. The whole load runs in one transaction, so it either fully succeeds or changes nothing.

## Why a run log?
`etl_run_log` records every run with its row counts and status. When something looks wrong in a report, it answers "when was this data loaded, from which file, and did the run succeed?"

## Cleaning rules and their reasoning
| Problem | Rule | Reason |
|---|---|---|
| `LF`, `low fat`, `reg` | Map to `Low Fat` / `Regular` | Same meaning, different spelling |
| Fat content on household items | Set to `Non-Edible` | Fat content does not apply |
| Missing `Item_Weight` | Same item's weight in another store, then median | An item weighs the same everywhere |
| `Item_Visibility = 0` | Same item's average visibility, then median | A product on sale must be visible |
| Missing `Outlet_Size` | Most common size for that outlet type | Outlet type is the best predictor available |
