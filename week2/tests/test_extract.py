import json
from types import SimpleNamespace

from ..app.services import extract


def test_extract_bullets_and_checkboxes():
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract.extract_action_items(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items


def _mock_ollama_chat(monkeypatch, items):
    """Replace the local Ollama request with a deterministic structured reply."""
    calls = []

    def fake_chat(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(message=SimpleNamespace(content=json.dumps({"items": items})))

    monkeypatch.setattr(extract, "chat", fake_chat)
    return calls


def test_extract_action_items_llm_from_bullet_list(monkeypatch):
    calls = _mock_ollama_chat(monkeypatch, ["Set up the database", "Write API tests"])

    items = extract.extract_action_items_llm("- Set up the database\n- Write API tests")

    assert items == ["Set up the database", "Write API tests"]
    assert calls[0]["format"] == extract.ACTION_ITEMS_SCHEMA
    assert calls[0]["options"] == {"temperature": 0}
    assert "Set up the database" in calls[0]["messages"][0]["content"]


def test_extract_action_items_llm_from_keyword_prefixed_lines(monkeypatch):
    calls = _mock_ollama_chat(monkeypatch, ["Send the design document", "Review pull request"])
    text = "TODO: Send the design document\nAction: Review pull request"

    items = extract.extract_action_items_llm(text)

    assert items == ["Send the design document", "Review pull request"]
    assert text in calls[0]["messages"][0]["content"]


def test_extract_action_items_llm_skips_ollama_for_empty_input(monkeypatch):
    def fail_if_called(**kwargs):
        raise AssertionError("Ollama should not be called for empty input")

    monkeypatch.setattr(extract, "chat", fail_if_called)

    assert extract.extract_action_items_llm("   \n\t ") == []


def test_extract_action_items_llm_cleans_duplicate_model_items(monkeypatch):
    _mock_ollama_chat(monkeypatch, [" Write tests ", "write tests", "", "Deploy app"])

    assert extract.extract_action_items_llm("Next: ship the release") == [
        "Write tests",
        "Deploy app",
    ]
