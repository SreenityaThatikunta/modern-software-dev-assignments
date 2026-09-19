"""Read recent history from a local Git repository without changing it."""

from __future__ import annotations

import subprocess
from collections import Counter
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any


class LocalGitError(RuntimeError):
    """A safe error message intended for MCP clients."""


def local_release_context(repo_path: str, days: int = 10) -> dict[str, Any]:
    """Collect commit activity, including commits that have not been pushed."""

    if not 1 <= days <= 90:
        raise ValueError("days must be between 1 and 90.")

    path = Path(repo_path).expanduser().resolve()
    if not path.is_dir():
        raise ValueError("repo_path must be an existing directory.")

    since = datetime.now(UTC) - timedelta(days=days)
    try:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(path),
                "log",
                f"--since={since.isoformat()}",
                "--format=%H%x1f%an%x1f%aI%x1f%s%x1e",
            ],
            capture_output=True,
            check=True,
            text=True,
            timeout=10,
        )
    except FileNotFoundError as error:
        raise LocalGitError("Git is not installed or is not available on PATH.") from error
    except subprocess.TimeoutExpired as error:
        raise LocalGitError("Reading local Git history timed out. Please retry.") from error
    except subprocess.CalledProcessError as error:
        raise LocalGitError("repo_path is not a readable Git repository.") from error

    commits = _parse_commits(result.stdout)
    contributors = Counter(commit["author"] for commit in commits)
    return {
        "source": "local_git",
        "repository": {
            "full_name": path.name,
            "description": "Local Git repository; includes unpushed commits.",
            "primary_language": "Not determined locally",
            "path": str(path),
        },
        "period": {"days": days, "since": since.date().isoformat()},
        "recent_commits": commits,
        "summary": {
            "recent_commit_count": len(commits),
            "contributors": [name for name, _ in contributors.most_common(5)],
        },
    }


def _parse_commits(output: str) -> list[dict[str, str]]:
    commits = []
    for record in output.split("\x1e"):
        if not record.strip():
            continue
        fields = record.rstrip("\n").split("\x1f")
        if len(fields) != 4:
            continue
        sha, author, committed_at, message = fields
        commits.append(
            {
                "sha": sha[:7],
                "message": message,
                "author": author,
                "committed_at": committed_at,
            }
        )
    return commits
