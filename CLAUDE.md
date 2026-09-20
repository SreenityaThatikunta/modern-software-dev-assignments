# Repository agent guide

This repository contains independent weekly assignments. Keep changes scoped to the
requested week; for this assignment, work only in `week4/` and its automation files.

## Week 4 workflow

- Do not use Conda. From `week4/`, create the environment with `make setup` and use
  `make test`, `make format`, and `make lint`.
- The FastAPI entry point is `backend/app/main.py`; API routers are under
  `backend/app/routers/`; tests live in `backend/tests/`.
- Run a focused test before implementation where practical. Before declaring a task
  complete, run the full test suite and lint.
- Keep database access in SQLAlchemy expressions; do not build SQL with user input.
- Preserve API errors: use 404 for missing resources and let Pydantic report invalid
  request bodies as 422.
- If routes change, update `week4/docs/API.md` in the same change.
