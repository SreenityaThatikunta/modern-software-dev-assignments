"""MCP entry point for Ship Cycle MCP."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

# ``mcp dev server/main.py:mcp`` imports this file directly rather than as the
# ``server`` package.  Establish the package context so its relative imports
# work in both the MCP Inspector and normal ``python -m server.main`` usage.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    __package__ = "server"

from mcp.server.fastmcp import FastMCP

from .github_client import GitHubAPIError
from .local_git import LocalGitError, local_release_context
from .ollama_client import OllamaError
from .service import launch_brief, ollama_social_posts, release_context, social_posts

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format="%(levelname)s %(message)s")

mcp = FastMCP(
    "Ship Cycle MCP",
    instructions=(
        "Use these tools to turn recent public GitHub activity into a launch brief and editable social drafts. "
        "The server never publishes content or modifies a repository."
    ),
)


def _error_payload(
    error: ValueError | GitHubAPIError | LocalGitError | OllamaError,
) -> dict[str, str]:
    logging.warning("Tool request failed: %s", error)
    return {"error": str(error)}


@mcp.tool()
def get_release_context(owner: str, repo: str, days: int = 10) -> dict:
    """Fetch GitHub release activity: merged PRs, commits, contributors, and open issues."""

    try:
        return release_context(owner, repo, days)
    except (ValueError, GitHubAPIError) as error:
        return _error_payload(error)


@mcp.tool()
def get_local_release_context(repo_path: str, days: int = 10) -> dict:
    """Read recent local Git commits, including work that has not been pushed."""

    try:
        return local_release_context(repo_path, days)
    except (ValueError, LocalGitError) as error:
        return _error_payload(error)


@mcp.tool()
def create_launch_brief(owner: str, repo: str, days: int = 10, audience: str = "developers") -> dict:
    """Create a structured launch brief from recent GitHub activity."""

    try:
        return launch_brief(release_context(owner, repo, days), audience)
    except (ValueError, GitHubAPIError) as error:
        return _error_payload(error)


@mcp.tool()
def draft_social_posts(
    owner: str,
    repo: str,
    days: int = 10,
    tone: str = "professional",
    release_notes: str = "",
    use_ollama: bool = True,
    model: str = "",
) -> dict:
    """Create commit-grounded X and LinkedIn drafts, using local Ollama when available."""

    try:
        context = release_context(owner, repo, days)
        brief = launch_brief(context)
        if not use_ollama:
            return social_posts(brief, tone)
        try:
            return ollama_social_posts(context, brief, tone, release_notes, model or None)
        except OllamaError as error:
            fallback = social_posts(brief, tone)
            fallback["generation_mode"] = "template_fallback"
            fallback["generation_note"] = str(error)
            return fallback
    except (ValueError, GitHubAPIError, OllamaError) as error:
        return _error_payload(error)


def main() -> None:
    """Start the local STDIO MCP server."""

    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
