# Ship Cycle MCP

Ship Cycle MCP is a local Model Context Protocol (MCP) server that turns recent GitHub or local Git repository activity into a launch brief and editable social-post drafts. It is designed for a repeatable build-and-ship cycle, such as a 10-day buildathon iteration.

The server is read-only: it never posts to social media and never changes GitHub data.

## Features

- `get_release_context`: summarizes commits first, plus merged pull requests, contributors, and open issues.
- `get_local_release_context`: reads local Git history, including commits that have not been pushed.
- `create_launch_brief`: formats that activity into a launch brief for developers, customers, or internal stakeholders.
- `draft_social_posts`: creates reviewable X and LinkedIn drafts from commit context, using a local Ollama model when available.

## Requirements

- Python 3.12 or newer
- An MCP-aware client, such as the MCP Inspector, Claude Desktop, or an AI IDE
- Optional: a GitHub personal access token for higher API limits or private repositories

## Setup

From this `week3` directory:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

For better GitHub rate limits, copy `.env.example` into your preferred environment configuration and export the token before starting the server:

```bash
export GITHUB_TOKEN="your-token"
```

### Optional: content-aware drafts with Ollama

Start Ollama and pull a model once (for example, `ollama pull llama3.2:3b`). Then set:

```bash
export OLLAMA_MODEL="llama3.2:3b"
```

The server sends commit messages and optional release notes to `http://127.0.0.1:11434/api/chat` on your machine. It does not send this context to a cloud model. If Ollama is unavailable, `draft_social_posts` safely returns a template-based fallback and explains why.

## Run

```bash
python -m server.main
```

The server uses STDIO, so standard output is reserved for MCP protocol messages. Logs are written to standard error.

### Example Claude Desktop configuration

Add this entry to your MCP configuration file. Replace `/absolute/path/to/week3` with this directory's real absolute path.

```json
{
  "mcpServers": {
    "ship-cycle": {
      "command": "/absolute/path/to/week3/.venv/bin/python",
      "args": ["-m", "server.main"],
      "cwd": "/absolute/path/to/week3"
    }
  }
}
```

If you need authenticated GitHub access, add an `env` object containing your real `GITHUB_TOKEN`; do not copy a placeholder token into the configuration.

## Tool reference

### `get_release_context`

Inputs: `owner` (string), `repo` (string), `days` (integer, default `10`, between `1` and `90`).

Example request: `Prepare the last 10 days of activity for owner "microsoft" and repository "vscode".`

Returns repository details, recent commits, merged PRs in the selected window, contributors, and up to ten open issues. Commit activity is the primary source of release highlights, so pull requests are optional.

Example response (abbreviated):

```json
{
  "source": "github",
  "repository": {"full_name": "microsoft/vscode"},
  "summary": {"recent_commit_count": 42, "contributors": ["octocat"]},
  "pagination": {"max_pages_per_endpoint": 10, "truncated_endpoints": []}
}
```

### `get_local_release_context`

Inputs: `repo_path` (absolute or relative local path) and `days` (integer, default `10`, between `1` and `90`).

Example request: `Get local release context for "/Users/me/projects/my-app" over the last 10 days.`

This read-only tool runs `git log` and includes commits that have not been pushed. It does not call GitHub and does not modify the repository.

Example response (abbreviated):

```json
{
  "source": "local_git",
  "repository": {"full_name": "my-app", "path": "/Users/me/projects/my-app"},
  "recent_commits": [{"sha": "a1b2c3d", "message": "Add offline sync", "author": "Ava"}],
  "summary": {"recent_commit_count": 1, "contributors": ["Ava"]}
}
```

### `create_launch_brief`

Inputs: `owner`, `repo`, `days`, and `audience` (`developers`, `customers`, or `internal`; default `developers`).

Example request: `Create a customer-facing launch brief for octocat/Hello-World.`

Returns an overview, highlights, contributors, follow-ups, and audience-specific editorial guidance.

Example response (abbreviated):

```json
{
  "title": "octocat/Hello-World: 10-day launch brief",
  "audience": "customers",
  "highlights": ["Improve onboarding"],
  "guidance": "Focus on outcomes and benefits; avoid internal implementation detail."
}
```

### `draft_social_posts`

Inputs: `owner`, `repo`, `days`, `tone` (`professional`, `friendly`, or `technical`; default `professional`), optional `release_notes`, optional `model`, and `use_ollama` (default `true`).

Example request: `Draft friendly X and LinkedIn updates for the last 10 days of owner/repo. The release notes are: "Simplified onboarding for new users."`

Returns editable X and LinkedIn drafts, an X character count, the generation mode, and a reminder to review before publishing. Set `use_ollama` to `false` to force the deterministic template fallback.

Ollama response (abbreviated):

```json
{
  "generation_mode": "ollama",
  "model": "llama3.2:3b",
  "x": {"draft": "Shipping update …", "within_standard_limit": true},
  "linkedin": {"draft": "A focused shipping cycle …"}
}
```

Fallback response when Ollama is unavailable or returns invalid JSON (abbreviated):

```json
{
  "generation_mode": "template_fallback",
  "generation_note": "Could not reach Ollama. Start Ollama locally, then retry; template drafts are still available.",
  "x": {"draft": "Shipping update …", "within_standard_limit": true},
  "linkedin": {"draft": "A focused shipping cycle …"}
}
```

## Reliability notes

- Requests time out after 10 seconds.
- Invalid repository names and invalid time windows return clear messages.
- HTTP, missing-repository, network, and GitHub rate-limit failures are translated into user-facing errors.
- Anonymous GitHub API calls are rate limited. Set `GITHUB_TOKEN` when using the server regularly.
- GitHub list endpoints are paginated up to ten pages (1,000 records) each; `pagination.truncated_endpoints` identifies any endpoint that reached that cap.
- Ollama failures (not running, missing model, or invalid model output) return a template fallback instead of failing the whole drafting request.
- Commit messages and release notes are treated as untrusted reference data in the Ollama prompt; the model is instructed not to follow instructions contained in them.

## Validation

Run the unit tests with:

```bash
pytest
```

## Future iterations

- Add a remote HTTP transport and deployment.
- Add an explicitly approved publishing integration for social platforms.
- Connect the workflow to a scheduler for a recurring 10-day shipping cycle.
