import json
from email.message import Message
from io import BytesIO
from unittest.mock import Mock
from urllib.error import HTTPError

import pytest

from server import main
from server.github_client import GitHubAPIError, GitHubClient
from server.local_git import local_release_context
from server.ollama_client import OllamaClient, OllamaError
from server.service import (
    launch_brief,
    ollama_social_posts,
    release_context,
    social_posts,
    validate_repository,
)


def test_validate_repository_rejects_invalid_values():
    with pytest.raises(ValueError, match="valid GitHub"):
        validate_repository("bad/name", "repo", 10)
    with pytest.raises(ValueError, match="between 1 and 90"):
        validate_repository("owner", "repo", 0)


def test_release_context_filters_and_summarizes_data():
    client = Mock(spec=GitHubClient)
    client.get.return_value = {
        "full_name": "octo/example",
        "description": "Demo",
        "language": "Python",
        "html_url": "https://github.com/octo/example",
    }
    client.get_paginated.side_effect = [
        (
            [
                {
                    "number": 4,
                    "title": "Ship feature",
                    "merged_at": "2099-01-02T00:00:00Z",
                    "user": {"login": "ava"},
                    "html_url": "https://example/pr/4",
                }
            ],
            False,
        ),
        (
            [
                {
                    "sha": "abcdef012345",
                    "commit": {
                        "message": "Ship feature\nMore detail",
                        "author": {"name": "Ava"},
                    },
                    "author": {"login": "ava"},
                }
            ],
            False,
        ),
        (
            [
                {"number": 7, "title": "Follow up", "html_url": "https://example/issues/7"},
                {"number": 8, "title": "Closed PR", "pull_request": {}},
            ],
            False,
        ),
    ]

    context = release_context("octo", "example", client=client)

    assert context["summary"] == {"merged_pull_request_count": 1, "recent_commit_count": 1, "open_issue_count": 1, "contributors": ["ava"]}
    assert context["recent_commits"][0]["sha"] == "abcdef0"
    assert context["pagination"]["truncated_endpoints"] == []


def test_social_posts_are_drafts_and_measure_x_length():
    context = {
        "repository": {"full_name": "octo/example", "url": "https://github.com/octo/example"},
        "period": {"days": 10, "since": "2026-01-01"},
        "merged_pull_requests": [{"number": 1, "title": "Useful feature"}],
        "open_issues": [{"number": 2, "title": "Polish"}],
        "summary": {"merged_pull_request_count": 1, "recent_commit_count": 2, "open_issue_count": 1, "contributors": ["ava"]},
    }
    drafts = social_posts(launch_brief(context))

    assert "drafts only" in drafts["publishing_note"]
    assert drafts["x"]["character_count"] == len(drafts["x"]["draft"])
    assert "Shipping update" in drafts["x"]["draft"]
    assert "What changed:" in drafts["linkedin"]["draft"]
    assert drafts["x"]["within_standard_limit"] is True


def test_social_posts_make_a_quiet_window_honest_and_actionable():
    context = {
        "repository": {"full_name": "octo/example", "url": "https://github.com/octo/example"},
        "period": {"days": 10, "since": "2026-01-01"},
        "merged_pull_requests": [],
        "open_issues": [{"number": 2, "title": "Polish"}],
        "recent_commits": [],
        "summary": {"merged_pull_request_count": 0, "recent_commit_count": 0, "open_issue_count": 1, "contributors": []},
    }

    drafts = social_posts(launch_brief(context), tone="friendly")

    assert "quiet shipping window" in drafts["x"]["draft"]
    assert "Next up" in drafts["linkedin"]["draft"]


def test_commit_only_context_becomes_the_launch_highlights():
    context = {
        "repository": {"full_name": "octo/example", "url": "https://github.com/octo/example"},
        "period": {"days": 10, "since": "2026-01-01"},
        "merged_pull_requests": [],
        "recent_commits": [{"message": "Add CSV export", "author": "ava"}],
        "open_issues": [],
        "summary": {"merged_pull_request_count": 0, "recent_commit_count": 1, "open_issue_count": 0, "contributors": ["ava"]},
    }

    brief = launch_brief(context)

    assert brief["highlight_source"] == "commits"
    assert brief["highlights"] == ["Add CSV export"]


def test_ollama_drafts_receive_commits_and_release_notes():
    context = {
        "repository": {"full_name": "octo/example", "description": "Demo", "url": "https://github.com/octo/example"},
        "period": {"days": 10, "since": "2026-01-01"},
        "merged_pull_requests": [],
        "recent_commits": [{"message": "Add CSV export", "author": "ava"}],
        "open_issues": [],
        "summary": {"merged_pull_request_count": 0, "recent_commit_count": 1, "open_issue_count": 0, "contributors": ["ava"]},
    }
    client = Mock(spec=OllamaClient, model="test-model")
    client.create_social_drafts.return_value = {"x": "CSV export is here.", "linkedin": "We added CSV export for the project."}

    drafts = ollama_social_posts(context, launch_brief(context), release_notes="Help people take their data with them.", client=client)

    assert drafts["generation_mode"] == "ollama"
    assert "CSV export" in drafts["x"]["draft"]
    client.create_social_drafts.assert_called_once()


def test_ollama_unavailable_uses_template_fallback(monkeypatch):
    context = _context()
    monkeypatch.setattr(main, "release_context", lambda *_: context)
    monkeypatch.setattr(
        main,
        "ollama_social_posts",
        Mock(side_effect=OllamaError("Could not reach Ollama.")),
    )

    drafts = main.draft_social_posts("octo", "example")

    assert drafts["generation_mode"] == "template_fallback"
    assert drafts["generation_note"] == "Could not reach Ollama."


def test_ollama_client_rejects_malformed_model_json(monkeypatch):
    class Response:
        def read(self):
            return json.dumps({"message": {"content": "not json"}}).encode()

        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

    monkeypatch.setattr("server.ollama_client.urlopen", lambda *_args, **_kwargs: Response())
    client = OllamaClient(model="test-model")

    with pytest.raises(OllamaError, match="invalid draft format"):
        client.create_social_drafts(_context(), launch_brief(_context()), "professional", "")


def test_github_rate_limit_has_actionable_error(monkeypatch):
    headers = Message()
    headers["X-RateLimit-Remaining"] = "0"
    error = HTTPError("https://api.github.com", 403, "Forbidden", headers, BytesIO())
    monkeypatch.setattr("server.github_client.urlopen", Mock(side_effect=error))

    with pytest.raises(GitHubAPIError, match="rate limit"):
        GitHubClient().get("/repos/octo/example")


def test_commit_only_context_counts_multiple_authors():
    client = Mock(spec=GitHubClient)
    client.get.return_value = {
        "full_name": "octo/example",
        "description": "Demo",
        "language": "Python",
        "html_url": "https://github.com/octo/example",
    }
    client.get_paginated.side_effect = [
        ([], False),
        (
            [
                _github_commit("Add CSV export", "ava"),
                _github_commit("Document exports", "ben"),
            ],
            False,
        ),
        ([], False),
    ]

    context = release_context("octo", "example", client=client)

    assert context["summary"]["contributors"] == ["ava", "ben"]
    assert launch_brief(context)["highlight_source"] == "commits"


def test_local_release_context_reads_unpushed_commits(tmp_path):
    from subprocess import run

    run(["git", "init", str(tmp_path)], check=True, capture_output=True)
    run(["git", "-C", str(tmp_path), "config", "user.name", "Ava"], check=True)
    run(["git", "-C", str(tmp_path), "config", "user.email", "ava@example.com"], check=True)
    (tmp_path / "release.txt").write_text("local-only work")
    run(["git", "-C", str(tmp_path), "add", "release.txt"], check=True)
    run(["git", "-C", str(tmp_path), "commit", "-m", "Add local-only release note"], check=True)

    context = local_release_context(str(tmp_path))

    assert context["source"] == "local_git"
    assert context["summary"]["recent_commit_count"] == 1
    assert context["recent_commits"][0]["message"] == "Add local-only release note"


def _context():
    return {
        "repository": {
            "full_name": "octo/example",
            "description": "Demo",
            "url": "https://github.com/octo/example",
        },
        "period": {"days": 10, "since": "2026-01-01"},
        "merged_pull_requests": [],
        "recent_commits": [{"message": "Add CSV export", "author": "ava"}],
        "open_issues": [],
        "summary": {
            "merged_pull_request_count": 0,
            "recent_commit_count": 1,
            "open_issue_count": 0,
            "contributors": ["ava"],
        },
    }


def _github_commit(message, author):
    return {
        "sha": f"{author}123456789",
        "commit": {"message": message, "author": {"name": author.title()}},
        "author": {"login": author},
    }
