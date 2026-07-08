"""Lightweight, dependency-free forecasting for time-series query results.

Uses Holt's linear trend method (double exponential smoothing) with a small
grid search over the smoothing parameters. Pure Python so it deploys cleanly to
serverless. Forecasts are always presented as *projections*, never as facts.
"""

from __future__ import annotations

import re
from datetime import date, timedelta

_FORECAST_RE = re.compile(
    r"\b(forecast|forecasts|forecasting|predict|prediction|projected|projection|"
    r"upcoming|future|expected|estimate\s+future|next\s+(?:month|months|quarter|"
    r"quarters|year|years|week|weeks|\d+))\b",
    re.IGNORECASE,
)

_HORIZON_RE = re.compile(r"next\s+(\d+)", re.IGNORECASE)

_MONTH_RE = re.compile(r"^(\d{4})-(\d{2})$")
_YEAR_RE = re.compile(r"^(\d{4})$")
_DAY_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
_QUARTER_RE = re.compile(r"^(\d{4})-Q([1-4])$", re.IGNORECASE)


def is_forecast_request(question: str) -> bool:
    """True when the user is asking to predict/forecast future values."""
    return bool(_FORECAST_RE.search(question or ""))


def parse_horizon(question: str, default: int = 3) -> int:
    """Number of future periods to project (clamped to a sane range)."""
    m = _HORIZON_RE.search(question or "")
    if m:
        return max(1, min(24, int(m.group(1))))
    return default


def looks_like_period(label: str) -> bool:
    """Whether a label is a recognizable time period we can extend."""
    s = str(label)
    return bool(
        _MONTH_RE.match(s)
        or _YEAR_RE.match(s)
        or _DAY_RE.match(s)
        or _QUARTER_RE.match(s)
    )


def _next_labels(labels: list[str], n: int) -> list[str]:
    """Produce the next n period labels, inferring the granularity."""
    last = str(labels[-1])

    m = _MONTH_RE.match(last)
    if m:
        year, month = int(m.group(1)), int(m.group(2))
        out = []
        for _ in range(n):
            month += 1
            if month > 12:
                month = 1
                year += 1
            out.append(f"{year:04d}-{month:02d}")
        return out

    q = _QUARTER_RE.match(last)
    if q:
        year, quarter = int(q.group(1)), int(q.group(2))
        out = []
        for _ in range(n):
            quarter += 1
            if quarter > 4:
                quarter = 1
                year += 1
            out.append(f"{year:04d}-Q{quarter}")
        return out

    d = _DAY_RE.match(last)
    if d:
        current = date(int(d.group(1)), int(d.group(2)), int(d.group(3)))
        return [(current + timedelta(days=i + 1)).isoformat() for i in range(n)]

    y = _YEAR_RE.match(last)
    if y:
        year = int(y.group(1))
        return [f"{year + i + 1:04d}" for i in range(n)]

    return [f"+{i + 1}" for i in range(n)]


def _holt(
    values: list[float], n: int, alpha: float, beta: float, phi: float
) -> list[float]:
    """Damped Holt's trend forecast for n future steps.

    phi < 1 dampens the trend so projections flatten out instead of running
    away (which otherwise plunges volatile series to zero / negatives).
    """
    level = values[0]
    trend = values[1] - values[0]
    for v in values[1:]:
        prev_level = level
        level = alpha * v + (1 - alpha) * (level + phi * trend)
        trend = beta * (level - prev_level) + (1 - beta) * phi * trend
    preds = []
    damp_sum = 0.0
    for i in range(n):
        damp_sum += phi ** (i + 1)
        preds.append(level + damp_sum * trend)
    return preds


def _fit_error(values: list[float], alpha: float, beta: float, phi: float) -> float:
    """In-sample one-step-ahead squared error for parameter selection."""
    level = values[0]
    trend = values[1] - values[0]
    sse = 0.0
    for v in values[1:]:
        forecast = level + phi * trend
        sse += (v - forecast) ** 2
        prev_level = level
        level = alpha * v + (1 - alpha) * (level + phi * trend)
        trend = beta * (level - prev_level) + (1 - beta) * phi * trend
    return sse


def forecast_series(values: list[float], n: int) -> list[float]:
    """Forecast the next n values, picking smoothing params via a small grid."""
    if n <= 0 or not values:
        return []
    if len(values) < 2:
        return [round(float(values[0]), 2)] * n

    ab_grid = [0.1, 0.3, 0.5, 0.7, 0.9]
    phi_grid = [0.8, 0.9, 1.0]
    best = min(
        ((a, b, p) for a in ab_grid for b in ab_grid for p in phi_grid),
        key=lambda t: _fit_error(values, t[0], t[1], t[2]),
    )
    preds = _holt(values, n, best[0], best[1], best[2])
    # Sales/quantities can't be negative; clamp and round.
    return [round(max(0.0, p), 2) for p in preds]


def build_forecast(
    labels: list[str], values: list[float], n: int
) -> tuple[list[str], list[float]]:
    """Return (future_labels, future_values) for a period-labelled series."""
    if len(labels) < 3 or len(values) != len(labels):
        return [], []
    if not all(looks_like_period(l) for l in labels):
        return [], []
    future_values = forecast_series(values, n)
    future_labels = _next_labels(labels, n)
    return future_labels, future_values
