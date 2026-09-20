# Week 4 API reference

The application serves its browser UI at `/` and interactive OpenAPI documentation at
`/docs`. JSON request bodies use `application/json`.

## Notes

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/notes/` | List notes. |
| `POST` | `/notes/` | Create a note. |
| `GET` | `/notes/{id}` | Read one note. |
| `PUT` | `/notes/{id}` | Replace a note's title and content. |
| `DELETE` | `/notes/{id}` | Delete a note (`204 No Content`). |
| `GET` | `/notes/search?q=term` | Case-insensitive title/content search. An absent or blank `q` lists all notes. |

Create and update bodies are `{ "title": "...", "content": "..." }`. `title` is
1–200 characters and `content` is 1–10,000 characters. A successful note response is
`{ "id": 1, "title": "...", "content": "..." }`.

Missing note IDs return `404` with `{"detail":"Note not found"}`. Invalid request
bodies return FastAPI/Pydantic's `422` validation response.

## Action items

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/action-items/` | List action items. |
| `POST` | `/action-items/` | Create an open item. |
| `PUT` | `/action-items/{id}/complete` | Mark an item complete. |

Creation accepts `{ "description": "..." }`, where the description is 1–2,000
characters. Item responses include `id`, `description`, and `completed`. A missing ID
returns `404`; an invalid body returns `422`.

## Extraction helper

`backend.app.services.extract` provides `extract_action_items(text)` for `TODO:` and
exclamation-mark action lines, plus `extract_tags(text)`. Tags match `#tag` syntax,
are lower-cased, de-duplicated, and returned without the `#`.
