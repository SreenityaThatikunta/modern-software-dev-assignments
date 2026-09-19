"""Small, dependency-free GitHub REST API client."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class GitHubAPIError(RuntimeError):
    """A safe error message intended for MCP clients."""


@dataclass(frozen=True)
class GitHubClient:
    """Fetch public GitHub data with optional token authentication."""

    token: str | None = None
    timeout_seconds: float = 10.0

    @classmethod
    def from_environment(cls) -> "GitHubClient":
        return cls(token=os.getenv("GITHUB_TOKEN") or None)

    def get(self, path: str, query: dict[str, str | int] | None = None) -> Any:
        url = f"https://api.github.com{path}"
        if query:
            url = f"{url}?{urlencode(query)}"

        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "ship-cycle-mcp",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        request = Request(url, headers=headers)
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            if error.code == 401:
                raise GitHubAPIError("GitHub rejected GITHUB_TOKEN. Check that it is valid.") from error
            if error.code == 403:
                remaining = error.headers.get("X-RateLimit-Remaining")
                if remaining == "0":
                    raise GitHubAPIError(
                        "GitHub API rate limit reached. Set GITHUB_TOKEN and retry later."
                    ) from error
                raise GitHubAPIError("GitHub denied this request. Check repository access.") from error
            if error.code == 404:
                raise GitHubAPIError("Repository not found. Check owner, repo, and access.") from error
            raise GitHubAPIError(f"GitHub returned HTTP {error.code}. Please try again.") from error
        except URLError as error:
            raise GitHubAPIError("Could not reach GitHub. Check your network and retry.") from error
        except TimeoutError as error:
            raise GitHubAPIError("GitHub request timed out. Please retry.") from error

    def get_paginated(
        self,
        path: str,
        query: dict[str, str | int] | None = None,
        max_pages: int = 10,
    ) -> tuple[list[dict[str, Any]], bool]:
        """Fetch GitHub list endpoints page by page, with a bounded API budget."""

        query = dict(query or {})
        query["per_page"] = 100
        records: list[dict[str, Any]] = []
        for page in range(1, max_pages + 1):
            page_query = {**query, "page": page}
            page_records = self.get(path, page_query)
            if not isinstance(page_records, list):
                raise GitHubAPIError("GitHub returned an unexpected list response. Please retry.")
            records.extend(page_records)
            if len(page_records) < query["per_page"]:
                return records, False
        return records, True


def parse_github_time(value: str) -> datetime:
    """Parse GitHub's ISO timestamp format into a UTC datetime."""

    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)
