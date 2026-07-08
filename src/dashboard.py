"""Dashboard KPIs and sample prompts."""

from __future__ import annotations

from src.database import execute_read_query

SAMPLE_QUESTIONS = [
    "What was total revenue by region?",
    "Show monthly revenue trend in 2024",
    "Forecast revenue for the next 3 months",
    "Top 5 products by units sold",
    "Which category drives the most revenue?",
    "How many orders were cancelled?",
]


def get_kpis() -> dict[str, str]:
    queries = {
        "revenue": """
            SELECT ROUND(SUM(oi.quantity * oi.unit_price), 0)
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.order_id
            WHERE o.status = 'completed'
        """,
        "orders": """
            SELECT COUNT(*) FROM orders WHERE status = 'completed'
        """,
        "customers": "SELECT COUNT(*) FROM customers",
        "products": "SELECT COUNT(*) FROM products",
    }
    kpis: dict[str, str] = {}
    for key, sql in queries.items():
        _, rows = execute_read_query(sql)
        value = rows[0][0] if rows else 0
        if key == "revenue":
            kpis[key] = f"${value:,.0f}"
        else:
            kpis[key] = f"{int(value):,}"
    return kpis
