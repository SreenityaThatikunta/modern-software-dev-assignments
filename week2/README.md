# Week 2: Action Item Extractor

A small FastAPI application that turns meeting notes into actionable tasks. It
offers both a rule-based extractor and an LLM-powered extractor backed by a
local Ollama model. Notes and action-item completion state are stored in SQLite.

## Features

- Extract action items from bullets, checkboxes, keyword-prefixed lines, and
  simple imperative sentences.
- Extract action items with a local Ollama model using structured JSON output.
- Optionally save source notes and associate extracted action items with them.
- List saved notes and action items, and mark action items complete.
- Use the browser UI at the root route or the interactive API documentation at
  `/docs`.

## Requirements

- Python 3.10 or later
- Ollama only for the **Extract LLM** feature

## Setup and run

From the repository root, create and activate a standard virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install fastapi 'uvicorn[standard]' ollama python-dotenv pytest
```

For LLM extraction, install and start Ollama, then pull the default local model:

```bash
ollama pull llama3.2:3b
ollama serve
```

In a separate terminal with the virtual environment activated, start the app:

```bash
python -m uvicorn week2.app.main:app --reload
```

Open http://127.0.0.1:8000 for the app and http://127.0.0.1:8000/docs for the
interactive OpenAPI documentation.

### Configuration

The LLM extractor uses `llama3.2:3b` by default. Set `OLLAMA_MODEL` before
starting the server to use another model you have already pulled:

```bash
OLLAMA_MODEL=mistral:latest python -m uvicorn week2.app.main:app --reload
```

By default, the SQLite database is `week2/data/app.db`. Use
`ACTION_ITEMS_DB_PATH` to select a different path, which is useful for testing:

```bash
ACTION_ITEMS_DB_PATH=/tmp/action-items.db python -m uvicorn week2.app.main:app --reload
```

## Using the web app

1. Paste notes into the text area.
2. Keep **Save as note** selected to retain the input in SQLite.
3. Select **Extract** for the rule-based extractor or **Extract LLM** for the
   Ollama-powered extractor.
4. Select an action item checkbox to save its completion state.
5. Select **List Notes** to display all saved notes.

## API

All JSON requests use `Content-Type: application/json`. Blank `content` and
`text` fields return a `422 Unprocessable Content` validation response.

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/notes` | Save a note. Body: `{"content":"..."}`. |
| `GET` | `/notes` | List saved notes, newest first. |
| `GET` | `/notes/{note_id}` | Get one saved note; returns `404` if missing. |
| `POST` | `/action-items/extract` | Rule-based extraction. Body: `{"text":"...","save_note":true}`. |
| `POST` | `/action-items/extract/llm` | Ollama LLM extraction using the same request body. Returns `503` if Ollama or the configured model is unavailable. |
| `GET` | `/action-items` | List action items. Optional query parameter: `note_id`. |
| `POST` | `/action-items/{action_item_id}/done` | Update completion state. Body: `{"done":true}`. Returns `404` if missing. |

For example, extract with the LLM and save the source note:

```bash
curl -X POST http://127.0.0.1:8000/action-items/extract/llm \
  -H 'Content-Type: application/json' \
  -d '{"text":"- Prepare demo\n- Review pull request","save_note":true}'
```

## Project layout

```text
week2/
├── app/
│   ├── main.py                 # FastAPI application and lifespan setup
│   ├── db.py                   # SQLite persistence layer
│   ├── schemas.py              # API request and response schemas
│   ├── routers/                # Notes and action-item HTTP endpoints
│   └── services/extract.py     # Heuristic and Ollama extractors
├── frontend/index.html         # Static browser interface
├── tests/test_extract.py       # Extractor unit tests
└── data/app.db                 # Created automatically at runtime
```

## Tests

Run the Week 2 tests from the repository root:

```bash
.venv/bin/python -m pytest -q week2/tests
```

The LLM extractor tests mock the Ollama client, so the test suite does not need
Ollama to be running.
