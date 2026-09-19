"""Business logic for commit-first release context and launch communications."""

from __future__ import annotations

import re
from collections import Counter
from datetime import UTC, datetime, timedelta
from typing import Any

from .github_client import GitHubClient, parse_github_time
from .ollama_client import OllamaClient

_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,99}$")
_VALID_AUDIENCES = {"developers", "customers", "internal"}
_VALID_TONES = {"professional", "friendly", "technical"}


def validate_repository(owner: str, repo: str, days: int) -> None:
    if not _NAME_PATTERN.fullmatch(owner) or not _NAME_PATTERN.fullmatch(repo):
        raise ValueError("owner and repo must be valid GitHub repository names.")
    if not 1 <= days <= 90:
        raise ValueError("days must be between 1 and 90.")


def validate_release_notes(release_notes: str) -> str:
    cleaned = release_notes.strip()
    if len(cleaned) > 2_000:
        raise ValueError("release_notes must be 2,000 characters or fewer.")
    return cleaned


def release_context(owner: str, repo: str, days: int = 10, client: GitHubClient | None = None) -> dict[str, Any]:
    """Collect commit-first release activity plus optional PR and issue context."""

    validate_repository(owner, repo, days)
    client = client or GitHubClient.from_environment()
    since = datetime.now(UTC) - timedelta(days=days)
    repository = client.get(f"/repos/{owner}/{repo}")
    pull_requests, pull_requests_truncated = client.get_paginated(
        f"/repos/{owner}/{repo}/pulls",
        {"state": "closed", "sort": "updated", "direction": "desc"},
    )
    commits, commits_truncated = client.get_paginated(
        f"/repos/{owner}/{repo}/commits",
        {"since": since.isoformat()},
    )
    issues, issues_truncated = client.get_paginated(
        f"/repos/{owner}/{repo}/issues",
        {"state": "open", "sort": "updated", "direction": "desc"},
    )

    merged_prs = [
        pr
        for pr in pull_requests
        if pr.get("merged_at") and parse_github_time(pr["merged_at"]) >= since
    ]
    open_issues = [issue for issue in issues if "pull_request" not in issue]
    normalized_commits = [
        {
            "sha": commit["sha"][:7],
            "message": commit["commit"]["message"].splitlines()[0],
            "author": commit.get("author", {}).get("login")
            or commit["commit"]["author"]["name"],
            "url": commit.get("html_url", ""),
        }
        for commit in commits
    ]
    contributors = Counter(commit["author"] for commit in normalized_commits)

    return {
        "source": "github",
        "repository": {
            "full_name": repository["full_name"],
            "description": repository.get("description") or "No description provided.",
            "primary_language": repository.get("language") or "Not specified",
            "url": repository["html_url"],
        },
        "period": {"days": days, "since": since.date().isoformat()},
        "merged_pull_requests": [
            {
                "number": pr["number"],
                "title": pr["title"],
                "author": pr.get("user", {}).get("login", "unknown"),
                "url": pr["html_url"],
            }
            for pr in merged_prs
        ],
        "recent_commits": normalized_commits,
        "open_issues": [
            {"number": issue["number"], "title": issue["title"], "url": issue["html_url"]}
            for issue in open_issues[:10]
        ],
        "summary": {
            "merged_pull_request_count": len(merged_prs),
            "recent_commit_count": len(normalized_commits),
            "open_issue_count": len(open_issues),
            "contributors": [name for name, _ in contributors.most_common(5)],
        },
        "pagination": {
            "max_pages_per_endpoint": 10,
            "truncated_endpoints": [
                name
                for name, truncated in {
                    "pull_requests": pull_requests_truncated,
                    "commits": commits_truncated,
                    "issues": issues_truncated,
                }.items()
                if truncated
            ],
        },
    }


def launch_brief(context: dict[str, Any], audience: str = "developers") -> dict[str, Any]:
    """Turn release data into a deterministic, reviewable launch brief."""

    if audience not in _VALID_AUDIENCES:
        raise ValueError(f"audience must be one of: {', '.join(sorted(_VALID_AUDIENCES))}.")
    summary = context["summary"]
    highlights = [
        f"#{pr['number']} — {pr['title']}"
        for pr in context["merged_pull_requests"][:5]
    ]
    highlight_source = "pull_requests"
    if not highlights:
        highlights = [commit["message"] for commit in context["recent_commits"][:5]]
        highlight_source = "commits"
    if not highlights:
        highlights, highlight_source = ["No commits were recorded during this window."], "none"

    audience_note = {
        "developers": "Focus on implementation details, upgrade notes, and follow-up work.",
        "customers": "Focus on outcomes and benefits; avoid internal implementation detail.",
        "internal": "Focus on progress, ownership, risks, and the next cycle.",
    }[audience]
    pr_phrase = (
        f"{summary['merged_pull_request_count']} merged pull requests"
        if summary["merged_pull_request_count"]
        else "no merged pull requests"
    )
    return {
        "title": (
            f"{context['repository']['full_name']}: "
            f"{context['period']['days']}-day launch brief"
        ),
        "audience": audience,
        "overview": f"{summary['recent_commit_count']} commits and {pr_phrase} since {context['period']['since']}.",
        "highlights": highlights,
        "highlight_source": highlight_source,
        "contributors": summary["contributors"]
        or ["No commit authors were returned in this window."],
        "follow_ups": [
            f"#{issue['number']} — {issue['title']}"
            for issue in context["open_issues"][:5]
        ]
        or ["No open issues were returned."],
        "guidance": audience_note,
        "repository_url": context["repository"]["url"],
    }


def social_posts(brief: dict[str, Any], tone: str = "professional") -> dict[str, Any]:
    """Create deterministic editable drafts when Ollama is unavailable or disabled."""

    if tone not in _VALID_TONES:
        raise ValueError(f"tone must be one of: {', '.join(sorted(_VALID_TONES))}.")
    highlights = brief["highlights"][:3]
    repo, next_up = brief["title"].split(":", 1)[0], brief["follow_ups"][0]
    if brief["highlight_source"] == "none":
        x_body = f"A quiet shipping window for {repo}. We’re using the next cycle to focus on {next_up}."
        linkedin_intro = "A quiet shipping window can still create space to focus the next cycle."
        highlight_section = "No commits were recorded in this window."
    else:
        lead = highlights[0]
        x_body = {
            "professional": f"Shipping update from {repo}: {lead}. {brief['overview']}",
            "friendly": f"Fresh from the workshop ✨ {repo}: {lead}. {brief['overview']}",
            "technical": f"Commit-based release update for {repo}: {lead}. {brief['overview']}",
        }[tone]
        linkedin_intro = {
            "professional": (
                "A focused shipping cycle is one of the best ways to turn momentum "
                "into something people can use."
            ),
            "friendly": "A little behind-the-scenes progress report from our latest build cycle:",
            "technical": "Here is the short version of what changed in the latest commit window:",
        }[tone]
        highlight_section = "\n".join(f"• {item}" for item in highlights)
    x_post = _fit_x_post(x_body, brief["repository_url"])
    linkedin_post = (
        f"{linkedin_intro}\n\n{repo}\n{brief['overview']}\n\nWhat changed:\n"
        f"{highlight_section}\n\nNext up: {next_up}\n\n{brief['repository_url']}\n\n"
        "#BuildInPublic #SoftwareDevelopment"
    )
    return {
        "publishing_note": "These are template drafts only. Review facts, tone, and links before posting.",
        "generation_mode": "template",
        "x": {
            "draft": x_post,
            "character_count": len(x_post),
            "within_standard_limit": len(x_post) <= 280,
        },
        "linkedin": {"draft": linkedin_post, "character_count": len(linkedin_post)},
    }


def ollama_social_posts(
    context: dict[str, Any],
    brief: dict[str, Any],
    tone: str = "professional",
    release_notes: str = "",
    model: str | None = None,
    client: OllamaClient | None = None,
) -> dict[str, Any]:
    """Generate fact-grounded social drafts locally through Ollama."""

    if tone not in _VALID_TONES:
        raise ValueError(f"tone must be one of: {', '.join(sorted(_VALID_TONES))}.")
    client = client or OllamaClient.from_environment(model=model)
    generated = client.create_social_drafts(context, brief, tone, validate_release_notes(release_notes))
    x_draft = _fit_x_post(generated["x"], brief["repository_url"])
    linkedin_draft = generated["linkedin"].strip()
    return {
        "publishing_note": "These are Ollama-generated drafts only. Review every claim, tone, and link before posting.",
        "generation_mode": "ollama",
        "model": client.model,
        "facts_used": brief["highlights"],
        "x": {
            "draft": x_draft,
            "character_count": len(x_draft),
            "within_standard_limit": len(x_draft) <= 280,
        },
        "linkedin": {
            "draft": linkedin_draft,
            "character_count": len(linkedin_draft),
        },
    }


def _fit_x_post(body: str, url: str, limit: int = 280) -> str:
    """Keep the editable X draft usable even when a model returns long content."""

    available = limit - len(url) - 1
    body = body.strip()
    if len(body) > available:
        body = f"{body[: max(0, available - 1)].rstrip()}…"
    return f"{body} {url}"
