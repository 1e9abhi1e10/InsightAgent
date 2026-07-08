"""SQL safety guardrails: read-only enforcement and injection prevention."""

from __future__ import annotations

import re

FORBIDDEN_KEYWORDS = {
    "insert",
    "update",
    "delete",
    "drop",
    "alter",
    "create",
    "truncate",
    "replace",
    "attach",
    "detach",
    "pragma",
    "vacuum",
    "grant",
    "revoke",
}

ALLOWED_TABLES = {
    "categories",
    "products",
    "customers",
    "orders",
    "order_items",
}


class SQLGuardrailError(ValueError):
    pass


def _strip_comments(sql: str) -> str:
    sql = re.sub(r"--.*?$", "", sql, flags=re.MULTILINE)
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)
    return sql


def _first_statement(sql: str) -> str:
    parts = [p.strip() for p in sql.split(";") if p.strip()]
    if len(parts) > 1:
        raise SQLGuardrailError("Multiple SQL statements are not allowed.")
    return parts[0] if parts else ""


def _cte_names(lower_sql: str) -> set[str]:
    names = set(re.findall(r"\bwith\s+([a-z_][a-z0-9_]*)\s+as\b", lower_sql))
    names.update(re.findall(r",\s*([a-z_][a-z0-9_]*)\s+as\s+\(", lower_sql))
    return names


def validate_read_only_sql(sql: str) -> str:
    """Validate and normalize a read-only SQL query."""
    if not sql or not sql.strip():
        raise SQLGuardrailError("Empty SQL query.")

    cleaned = _strip_comments(sql.strip())
    statement = _first_statement(cleaned)
    if not statement:
        raise SQLGuardrailError("No executable SQL statement found.")

    normalized = statement.strip().rstrip(";")
    lower = normalized.lower()

    if not lower.startswith("select") and not lower.startswith("with"):
        raise SQLGuardrailError("Only SELECT queries (including CTEs) are allowed.")

    tokens = set(re.findall(r"\b[a-z_]+\b", lower))
    blocked = tokens & FORBIDDEN_KEYWORDS
    if blocked:
        raise SQLGuardrailError(
            f"Destructive or unsafe SQL keywords detected: {', '.join(sorted(blocked))}"
        )

    referenced_tables = set(re.findall(r"\b(?:from|join)\s+([a-z_][a-z0-9_]*)", lower))
    unknown = referenced_tables - ALLOWED_TABLES - _cte_names(lower)
    if unknown:
        raise SQLGuardrailError(
            f"Query references unknown tables: {', '.join(sorted(unknown))}"
        )

    # Block obvious injection patterns in string literals used as sub-queries
    if re.search(r";\s*(insert|update|delete|drop)", lower):
        raise SQLGuardrailError("Chained destructive statements are not allowed.")

    return normalized


def is_likely_prompt_injection(user_message: str) -> bool:
    """Basic heuristic to flag prompt-injection attempts."""
    lower = user_message.lower()
    injection_patterns = [
        "ignore previous instructions",
        "ignore all instructions",
        "disregard your instructions",
        "you are now",
        "system prompt",
        "reveal your prompt",
        "drop table",
        "delete from",
        "insert into",
        "update ",
        "run this sql:",
        "execute:",
    ]
    return any(pattern in lower for pattern in injection_patterns)
