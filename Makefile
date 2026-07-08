.PHONY: install test test-offline lint build dev-backend dev-frontend dev

install:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt -r api/requirements.txt
	npm install

test:
	.venv/bin/python -m pytest tests/test_core.py tests/test_features.py -v

test-offline:
	.venv/bin/python tests/run_tests.py --offline

lint:
	npm run lint

build:
	npm run build

dev-backend:
	.venv/bin/uvicorn api.index:app --reload --port 8000

dev-frontend:
	BACKEND_ORIGIN=http://localhost:8000 npm run dev
