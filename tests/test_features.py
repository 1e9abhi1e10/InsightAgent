"""Unit tests for advanced features — cache, groundedness, eval scaffolding.

No API calls; these are deterministic offline checks.
"""

from __future__ import annotations

import time

import pytest

from src.cache import TTLCache, make_key
from src.quality import groundedness_label, groundedness_score
from src.seed_data import seed_database


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    seed_database(force=True)


class TestCache:
    def test_set_and_get(self):
        c = TTLCache(max_size=10, ttl_seconds=60)
        c.set("k", 123)
        assert c.get("k") == 123
        assert c.hits == 1

    def test_miss(self):
        c = TTLCache()
        assert c.get("nope") is None
        assert c.misses == 1

    def test_ttl_expiry(self):
        c = TTLCache(ttl_seconds=0.05)
        c.set("k", "v")
        time.sleep(0.1)
        assert c.get("k") is None

    def test_lru_eviction(self):
        c = TTLCache(max_size=2, ttl_seconds=60)
        c.set("a", 1)
        c.set("b", 2)
        c.set("c", 3)  # evicts "a"
        assert c.get("a") is None
        assert c.get("b") == 2
        assert c.get("c") == 3

    def test_hit_rate(self):
        c = TTLCache()
        c.set("a", 1)
        c.get("a")
        c.get("missing")
        assert c.hit_rate == 0.5

    def test_make_key_normalizes(self):
        assert make_key("  Total   REVENUE ") == "total revenue"

    def test_make_key_ignores_history(self):
        # Same question is the same cache key regardless of conversation history.
        assert make_key("Total revenue?") == make_key(
            "Total revenue?", [{"role": "user", "content": "prev"}]
        )


class TestGroundedness:
    def test_supported_numbers_score_high(self):
        rows = [("North", 4134.93), ("South", 3120.0)]
        score = groundedness_score("North had 4134.93 and South had 3120.", rows)
        assert score == 1.0

    def test_hallucinated_number_scores_low(self):
        rows = [("North", 100.0)]
        score = groundedness_score("Revenue was 999999.", rows)
        assert score < 0.6

    def test_rounding_tolerance(self):
        rows = [("North", 4134.93)]
        score = groundedness_score("About 4135 in revenue.", rows)
        assert score == 1.0

    def test_no_numbers_is_grounded(self):
        score = groundedness_score("There are no results for this query.", [])
        assert score == 1.0

    def test_years_ignored(self):
        rows = [("Jan", 50)]
        score = groundedness_score("In 2024, sales were 50.", rows)
        assert score == 1.0

    def test_ranking_markers_ignored(self):
        rows = [("South", 4134.93), ("East", 3120.0), ("North", 2000.0)]
        answer = "1. South: 4,134.93, 2. East: 3,120.00, 3. North: 2,000.00"
        score = groundedness_score(answer, rows)
        assert score == 1.0

    def test_magnitude_suffix(self):
        rows = [("South", 4100.0)]
        score = groundedness_score("Revenue was about 4.1K.", rows)
        assert score == 1.0

    def test_textual_results_not_penalized(self):
        rows = [("Electronics",), ("Clothing",)]
        score = groundedness_score("The categories are Electronics and Clothing.", rows)
        assert score == 1.0

    def test_labels(self):
        assert groundedness_label(1.0) == "High"
        assert groundedness_label(0.7) == "Medium"
        assert groundedness_label(0.2) == "Low"


class TestEvalScaffolding:
    def test_golden_cases_build(self):
        from src.evaluation import build_golden_cases

        cases = build_golden_cases()
        assert len(cases) >= 10
        categories = {c.category for c in cases}
        assert {"sql", "ambiguity", "guardrail"}.issubset(categories)

    def test_report_math(self):
        from src.evaluation import CaseResult, EvalReport

        report = EvalReport(
            results=[
                CaseResult("q1", "sql", True, 1.0, 100, "SELECT 1", "ok"),
                CaseResult("q2", "sql", False, 0.5, 200, "SELECT 2", "no"),
            ]
        )
        assert report.total == 2
        assert report.passed == 1
        assert report.pass_rate == 0.5
        assert report.avg_latency_ms == 150
        assert report.avg_groundedness == 0.75


class TestForecast:
    def test_intent_detection(self):
        from src.forecast import is_forecast_request

        assert is_forecast_request("Forecast revenue for the next 3 months")
        assert is_forecast_request("predict sales next quarter")
        assert is_forecast_request("what will demand be next year")
        assert not is_forecast_request("What was total revenue by region?")
        assert not is_forecast_request("Show monthly revenue trend in 2024")

    def test_horizon_parsing(self):
        from src.forecast import parse_horizon

        assert parse_horizon("forecast next 6 months") == 6
        assert parse_horizon("predict sales") == 3  # default
        assert parse_horizon("next 999 months") == 24  # clamped

    def test_monthly_labels_extend(self):
        from src.forecast import build_forecast

        labels = ["2024-10", "2024-11", "2024-12"]
        values = [100.0, 200.0, 300.0]
        fut_labels, fut_values = build_forecast(labels, values, 3)
        assert fut_labels == ["2025-01", "2025-02", "2025-03"]
        assert len(fut_values) == 3
        # Upward trend should keep increasing.
        assert fut_values[0] > 300

    def test_forecast_non_negative(self):
        from src.forecast import forecast_series

        preds = forecast_series([100.0, 60.0, 20.0], 5)  # steep decline
        assert all(p >= 0 for p in preds)

    def test_rejects_non_period_labels(self):
        from src.forecast import build_forecast

        labels = ["North", "South", "East"]
        fut_labels, fut_values = build_forecast(labels, [1.0, 2.0, 3.0], 3)
        assert fut_labels == [] and fut_values == []

    def test_year_labels_extend(self):
        from src.forecast import build_forecast

        fut_labels, _ = build_forecast(["2022", "2023", "2024"], [10.0, 20.0, 30.0], 2)
        assert fut_labels == ["2025", "2026"]
