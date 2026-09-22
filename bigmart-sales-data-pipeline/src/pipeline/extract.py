"""Extract step: read the raw CSV and check it has the expected shape."""
import logging
from pathlib import Path

import pandas as pd

from .config import REQUIRED_COLUMNS

log = logging.getLogger(__name__)


class SchemaError(ValueError):
    """Raised when the source file is missing required columns."""


def extract(path: Path) -> pd.DataFrame:
    if not Path(path).exists():
        raise FileNotFoundError(f"Source file not found: {path}")

    df = pd.read_csv(path)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise SchemaError(f"Source is missing columns: {missing}")

    log.info("Extracted %d rows from %s", len(df), path)
    return df[REQUIRED_COLUMNS].copy()
