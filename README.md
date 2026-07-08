# InsightAgent

Ask questions about retail data in plain English. InsightAgent turns them into SQL, runs read-only queries, and returns answers with charts and optional forecasts.

**Stack:** Next.js · FastAPI · Google Gemini · SQLite

## What it does

- Natural language → SQL over a 5-table retail database (categories, products, customers, orders, order_items)
- Natural-language answers grounded in query results, with a numeric claim checker
- Auto-selected charts (bar, line, pie, table)
- Time-series forecasting (damped Holt's trend) when you ask to predict or forecast
- Guardrails: read-only SQL, table whitelist, prompt-injection heuristics
- Self-correcting SQL when a query fails at execution time
- Response cache, per-stage latency metrics, and an in-app evaluation tab

## Quick start

```bash
git clone https://github.com/1e9abhi1e10/InsightAgent.git
cd InsightAgent

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r api/requirements.txt

cp .env.example .env
# Add GEMINI_API_KEY from https://aistudio.google.com/apikey

# Terminal 1 — API
uvicorn api.index:app --reload --port 8000

# Terminal 2 — UI
npm install
BACKEND_ORIGIN=http://localhost:8000 npm run dev
```

Open http://localhost:3000

**Streamlit UI (optional):** `streamlit run app.py` → http://localhost:8501

## Environment

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Google Gemini API key |
| `GEMINI_MODEL` | No | Default: `gemini-flash-lite-latest` |
| `BACKEND_ORIGIN` | Local only | e.g. `http://localhost:8000` for Next.js dev proxy |

## API

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/kpis` | Dashboard KPIs |
| GET | `/api/samples` | Suggested questions |
| POST | `/api/ask` | `{question, history}` → answer, SQL, chart, metrics |
| POST | `/api/eval` | Run evaluation harness |

## Deploy (Vercel)

1. Import the GitHub repo in Vercel
2. Set `GEMINI_API_KEY` (do not set `BACKEND_ORIGIN`)
3. Deploy — `vercel.json` routes `/api/*` to the Python function and bundles `src/**`

SQLite is seeded into `/tmp` on cold start (ephemeral, fine for the synthetic dataset).

## Tests

```bash
make test                    # unit tests (no API)
python3 tests/run_tests.py --offline
python3 -m pytest tests/test_agent_integration.py -v   # needs GEMINI_API_KEY
python3 scripts/smoke_test.py
python3 scripts/run_eval.py
npm run lint && npm run build
```

## Example questions

- What was total revenue by region?
- Show monthly revenue trend in 2024
- Forecast revenue for the next 3 months
- Top 5 products by units sold
- How many orders were cancelled?

## Project layout

```
InsightAgent/
├── api/           FastAPI backend (Vercel serverless)
├── app/           Next.js pages
├── components/    React UI
├── src/           Agent, guardrails, forecast, eval, seed data
├── scripts/       smoke test, eval CLI
├── tests/
└── app.py         Streamlit UI (optional)
```

## Data

Synthetic retail data is generated on first run (~250 orders, 40 customers, 31 products, 8 categories). To reseed:

```bash
python3 -c "from src.seed_data import seed_database; seed_database(force=True)"
```

Edit lists in `src/seed_data.py` to add categories, products, or customers. The chat agent is read-only — data changes go through seeding or direct DB admin, not through the UI.

## License

MIT
