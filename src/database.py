"""SQLite database setup and read-only query execution."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path


def _resolve_data_dir() -> Path:
    """Pick a writable data directory.

    On serverless platforms (Vercel/Lambda) the project filesystem is read-only,
    so fall back to /tmp. An explicit AGENT_DATA_DIR override always wins.
    """
    override = os.getenv("AGENT_DATA_DIR")
    if override:
        return Path(override)
    if os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
        return Path("/tmp/agent_data")
    return Path(__file__).resolve().parent.parent / "data"


DATA_DIR = _resolve_data_dir()
DB_PATH = DATA_DIR / "analytics.db"


def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_schema_description() -> str:
    """Return a human-readable schema for the LLM prompt."""
    return """
Tables (SQLite):

1. categories
   - category_id (INTEGER PK)
   - name (TEXT) — e.g. Electronics, Clothing, Home & Garden

2. products
   - product_id (INTEGER PK)
   - name (TEXT)
   - category_id (INTEGER FK → categories.category_id)
   - unit_price (REAL)
   - stock_quantity (INTEGER)

3. customers
   - customer_id (INTEGER PK)
   - name (TEXT)
   - email (TEXT)
   - region (TEXT) — North, South, East, West
   - signup_date (TEXT, ISO date YYYY-MM-DD)

4. orders
   - order_id (INTEGER PK)
   - customer_id (INTEGER FK → customers.customer_id)
   - order_date (TEXT, ISO date YYYY-MM-DD)
   - status (TEXT) — completed, pending, cancelled, refunded

5. order_items
   - item_id (INTEGER PK)
   - order_id (INTEGER FK → orders.order_id)
   - product_id (INTEGER FK → products.product_id)
   - quantity (INTEGER)
   - unit_price (REAL) — price at time of purchase

Revenue for a line item = quantity * unit_price.
Join path example: order_items → orders → customers; order_items → products → categories.
""".strip()


def execute_read_query(sql: str) -> tuple[list[str], list[tuple]]:
    """Execute a validated read-only query and return (columns, rows)."""
    conn = get_connection()
    try:
        cursor = conn.execute(sql)
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = [tuple(row) for row in cursor.fetchall()]
        return columns, rows
    finally:
        conn.close()
