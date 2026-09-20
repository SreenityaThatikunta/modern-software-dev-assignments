.PHONY: setup hooks run test format lint seed docs

PYTHON ?= python3
VENV ?= .venv

setup:
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/python -m pip install --upgrade pip
	$(VENV)/bin/python -m pip install -r requirements.txt

hooks:
	$(VENV)/bin/python -m pre_commit install --config pre-commit-config.yaml

run:
	PYTHONPATH=. $(VENV)/bin/python -m uvicorn backend.app.main:app --reload --host $${HOST:-127.0.0.1} --port $${PORT:-8000}

test:
	PYTHONPATH=. $(VENV)/bin/python -m pytest -q backend/tests

format:
	$(VENV)/bin/python -m black .
	$(VENV)/bin/python -m ruff check . --fix

lint:
	$(VENV)/bin/python -m ruff check .

seed:
	PYTHONPATH=. $(VENV)/bin/python -c "from backend.app.db import apply_seed_if_needed; apply_seed_if_needed()"

docs:
	@echo "API reference: docs/API.md"
