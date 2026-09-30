#!/usr/bin/env python3
"""Read, clean, and load MOCK_DATA.csv into the mock MySQL table."""

import logging
import os
import re
from pathlib import Path

import mysql.connector
import pandas as pd

# Credentials come from the environment (never hard-code passwords).
DBHOST = os.environ.get("DBHOST")
DBUSER = os.environ.get("DBUSER")
DBPASS = os.environ.get("DBPASS")
DBNAME = os.environ.get("DBNAME")

# Default CSV lives next to README.md at the repo root.
DEFAULT_CSV = Path(__file__).resolve().parents[2] / "MOCK_DATA.csv"

# pandas dtype name -> MySQL type (from the lab writeup).
TYPE_MAPPING = {
    "int64": "BIGINT",
    "int32": "INT",
    "float64": "DOUBLE",
    "bool": "TINYINT(1)",
    "datetime64[ns]": "DATETIME",
    "object": "VARCHAR(255)",
    "string": "VARCHAR(255)",
}

# Safe SQL identifiers only (letters, numbers, underscore).
_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


def _require_env() -> None:
    """Raise if any required database environment variable is missing."""
    missing = [name for name, val in (
        ("DBHOST", DBHOST),
        ("DBUSER", DBUSER),
        ("DBPASS", DBPASS),
        ("DBNAME", DBNAME),
    ) if not val]
    if missing:
        raise SystemExit(f"Set environment variables: {', '.join(missing)}")


def _quote_ident(name: str) -> str:
    """Return a backtick-quoted identifier after validating the name."""
    if not _IDENT.match(name):
        raise ValueError(f"Unsafe SQL identifier: {name!r}")
    return f"`{name}`"


def read_data(filename: str) -> pd.DataFrame:
    """Load a CSV (or Excel) file into a DataFrame.

    Args:
        filename: Path to a .csv or .xlsx file.

    Returns:
        A pandas DataFrame with the file contents.
    """
    path = Path(filename)
    logger.info("Reading data from %s", path)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        data = pd.read_csv(path)
    elif suffix in {".xlsx", ".xls"}:
        data = pd.read_excel(path)
    else:
        raise ValueError(f"Unsupported file extension: {suffix}")
    logger.info("Loaded %s rows and %s columns", len(data), len(data.columns))
    return data


def clean_data(data: pd.DataFrame) -> pd.DataFrame:
    """Prepare a DataFrame for upload by dropping incomplete rows.

    Args:
        data: Raw DataFrame from read_data.

    Returns:
        A copy of the DataFrame with missing-value rows removed.
    """
    logger.info("Cleaning data (%s rows before dropna)", len(data))
    cleaned = data.dropna().copy()
    # Normalize column names so `group` is a stable identifier.
    cleaned.columns = [str(col).strip() for col in cleaned.columns]
    logger.info("Cleaning complete (%s rows after dropna)", len(cleaned))
    return cleaned


def _sql_type_for_series(series: pd.Series) -> str:
    """Map a pandas Series dtype to a MySQL column type."""
    dtype_name = str(series.dtype)
    return TYPE_MAPPING.get(dtype_name, "VARCHAR(255)")


def load_data(data: pd.DataFrame, table: str) -> None:
    """Create the destination table if needed and insert DataFrame rows.

    Uses parameterized INSERT statements (approach A) so values are never
    interpolated into the SQL string.

    Args:
        data: Cleaned DataFrame to upload.
        table: Destination table name (always pass \"mock\").
    """
    if table != "mock":
        raise ValueError('Destination table must be "mock"')
    if data.empty:
        logger.warning("No rows to load; skipping upload")
        return

    table_sql = _quote_ident(table)
    columns = list(data.columns)
    col_defs = []
    for col in columns:
        col_defs.append(f"{_quote_ident(col)} {_sql_type_for_series(data[col])}")
    create_sql = (
        f"CREATE TABLE IF NOT EXISTS {table_sql} ("
        + ", ".join(col_defs)
        + ")"
    )

    placeholders = ", ".join(["%s"] * len(columns))
    insert_sql = (
        f"INSERT INTO {table_sql} ("
        + ", ".join(_quote_ident(c) for c in columns)
        + f") VALUES ({placeholders})"
    )

    conn = None
    try:
        logger.info("Connecting to MySQL host %s database %s", DBHOST, DBNAME)
        conn = mysql.connector.connect(
            host=DBHOST,
            user=DBUSER,
            password=DBPASS,
            database=DBNAME,
        )
        cursor = conn.cursor()
        cursor.execute(create_sql)
        # Re-runs should not stack duplicate rows on top of a previous load.
        cursor.execute(f"DELETE FROM {table_sql}")

        row_count = 0
        for row in data.itertuples(index=False, name=None):
            cursor.execute(insert_sql, tuple(row))
            row_count += 1

        conn.commit()
        cursor.close()
        logger.info("Inserted %s rows into %s.%s", row_count, DBNAME, table)
    except mysql.connector.Error:
        logger.exception("Failed to load data into MySQL")
        if conn is not None:
            conn.rollback()
        raise
    finally:
        if conn is not None and conn.is_connected():
            conn.close()
            logger.info("Closed MySQL connection")


def main() -> None:
    """Read MOCK_DATA.csv, clean it, and upload it to the mock table."""
    _require_env()
    raw = read_data(str(DEFAULT_CSV))
    cleaned = clean_data(raw)
    load_data(cleaned, "mock")


if __name__ == "__main__":
    main()
