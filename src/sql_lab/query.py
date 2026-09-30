#!/usr/bin/env python3
"""Query the mock table in the student mock database."""

import logging
import os

import mysql.connector
import pandas as pd

DBHOST = os.environ.get("DBHOST")
DBUSER = os.environ.get("DBUSER")
DBPASS = os.environ.get("DBPASS")
DBNAME = os.environ.get("DBNAME")

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


def _connect():
    """Open a MySQL connection using environment credentials."""
    logger.info("Connecting to MySQL host %s database %s", DBHOST, DBNAME)
    return mysql.connector.connect(
        host=DBHOST,
        user=DBUSER,
        password=DBPASS,
        database=DBNAME,
    )


def get_data_by_group(value):
    """Return all mock rows whose `group` column equals ``value``.

    The filter column is ``group`` (a reserved word in MySQL, so it is
    quoted with backticks). The comparison uses a parameterized query.

    Args:
        value: Group label to match (for example, \"alpha\").

    Returns:
        A list of row tuples, or an empty list on error.
    """
    query = "SELECT * FROM mock WHERE `group` = %s"
    conn = None
    try:
        conn = _connect()
        cursor = conn.cursor()
        logger.info("Filtering mock rows where `group` = %s", value)
        cursor.execute(query, (value,))
        rows = cursor.fetchall()
        cursor.close()
        logger.info("Retrieved %s rows for group %s", len(rows), value)
        return rows
    except mysql.connector.Error:
        logger.exception("get_data_by_group failed")
        return []
    finally:
        if conn is not None and conn.is_connected():
            conn.close()


# Static GROUP BY queries so column names are never interpolated into SQL.
_COUNT_QUERIES = {
    "group": (
        "SELECT `group` AS bucket, COUNT(*) AS n FROM mock "
        "GROUP BY `group` ORDER BY n DESC"
    ),
    "first_name": (
        "SELECT first_name AS bucket, COUNT(*) AS n FROM mock "
        "GROUP BY first_name ORDER BY n DESC"
    ),
    "last_name": (
        "SELECT last_name AS bucket, COUNT(*) AS n FROM mock "
        "GROUP BY last_name ORDER BY n DESC"
    ),
    "email": (
        "SELECT email AS bucket, COUNT(*) AS n FROM mock "
        "GROUP BY email ORDER BY n DESC"
    ),
    "signup_date": (
        "SELECT signup_date AS bucket, COUNT(*) AS n FROM mock "
        "GROUP BY signup_date ORDER BY n DESC"
    ),
}


def plot_counts(groupby):
    """Count mock rows for each distinct value of ``groupby``.

    Args:
        groupby: A column name in mock (for example, \"group\" or \"last_name\").

    Returns:
        A two-column DataFrame of value and count, or None on error.
    """
    query = _COUNT_QUERIES.get(groupby)
    if query is None:
        raise ValueError(
            f"Unsupported groupby column {groupby!r}; "
            f"choose one of {sorted(_COUNT_QUERIES)}"
        )
    conn = None
    try:
        conn = _connect()
        cursor = conn.cursor()
        logger.info("Counting mock rows grouped by %s", groupby)
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        df = pd.DataFrame(rows, columns=["bucket", "n"])
        logger.info("Computed counts for %s distinct %s values", len(df), groupby)
        return df
    except mysql.connector.Error:
        logger.exception("plot_counts failed")
        return None
    finally:
        if conn is not None and conn.is_connected():
            conn.close()


def main() -> None:
    """Demonstrate group filter and grouped counts against mock."""
    _require_env()

    print("=== rows in group alpha ===")
    print(get_data_by_group("alpha"))

    print("=== counts by group ===")
    counts = plot_counts("group")
    if counts is not None:
        print(counts)


if __name__ == "__main__":
    main()
