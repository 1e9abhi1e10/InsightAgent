"""FastAPI backend for the Conversational Data Analyst.

Wraps the existing agent (src/) and exposes a small JSON API. Runs locally with
uvicorn and deploys to Vercel as a Python serverless function.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make the project root importable (so `src` resolves) both locally and on Vercel.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.agent import ask, cache_stats, clear_cache
from src.dashboard import SAMPLE_QUESTIONS, get_kpis
from src.database import get_schema_description
from src.seed_data import seed_database

load_dotenv()

app = FastAPI(title="Conversational Data Analyst API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # same-origin on Vercel; permissive for local dev
    allow_methods=["*"],
    allow_headers=["*"],
)

_seeded = False


def _ensure_seeded() -> None:
    global _seeded
    if not _seeded:
        seed_database()
        _seeded = True


class Turn(BaseModel):
    role: str
    content: str


class AskRequest(BaseModel):
    question: str
    history: list[Turn] = []
    use_cache: bool = True


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {"status": "ok"}


@app.get("/api/kpis")
def kpis() -> dict[str, str]:
    _ensure_seeded()
    return get_kpis()


@app.get("/api/schema")
def schema() -> dict[str, str]:
    return {"schema": get_schema_description()}


@app.get("/api/samples")
def samples() -> dict[str, list[str]]:
    return {"samples": SAMPLE_QUESTIONS}


@app.get("/api/cache")
def cache() -> dict[str, Any]:
    return cache_stats()


@app.post("/api/cache/clear")
def cache_clear() -> dict[str, str]:
    clear_cache()
    return {"status": "cleared"}


@app.post("/api/ask")
def ask_endpoint(req: AskRequest) -> dict[str, Any]:
    _ensure_seeded()
    history = [{"role": t.role, "content": t.content} for t in req.history]
    result = ask(req.question, history, use_cache=req.use_cache)
    return {
        "answer": result.answer,
        "sql": result.sql,
        "columns": result.columns,
        "rows": [list(r) for r in result.rows],
        "chart_type": result.chart_type,
        "chart_config": result.chart_config,
        "clarification": result.clarification,
        "blocked": result.blocked,
        "error": result.error,
        "timings": result.timings,
        "groundedness": result.groundedness,
        "groundedness_label": result.groundedness_label,
        "repair_attempts": result.repair_attempts,
        "cached": result.cached,
    }


@app.post("/api/eval")
def eval_endpoint() -> dict[str, Any]:
    _ensure_seeded()
    from src.evaluation import run_evaluation

    report = run_evaluation(delay_seconds=0.0)
    return {
        "pass_rate": report.pass_rate,
        "passed": report.passed,
        "total": report.total,
        "avg_latency_ms": report.avg_latency_ms,
        "avg_groundedness": report.avg_groundedness,
        "by_category": {k: list(v) for k, v in report.by_category().items()},
        "results": [
            {
                "question": r.question,
                "category": r.category,
                "passed": r.passed,
                "groundedness": r.groundedness,
                "latency_ms": r.latency_ms,
                "sql": r.sql,
                "answer": r.answer,
                "error": r.error,
            }
            for r in report.results
        ],
    }
