# Week 4 Write-up — The Autonomous Coding Agent IRL

## Submission details

Name: **TODO — add before submitting**

SUNet ID: **TODO — add before submitting**

Citations: [Claude Code best practices](https://www.anthropic.com/engineering/claude-code-best-practices) and [Claude Code sub-agents overview](https://docs.anthropic.com/en/docs/claude-code/sub-agents).

This assignment took me about **TODO — record your time before submitting** hours to do.

## Automation #1 — `/week4-quality`

### Design inspiration

The automation follows the small, repeatable feedback-loop approach recommended in the
Claude Code best-practices guide. It makes the project’s formatter, linter, and tests
one predictable quality gate rather than a sequence that has to be recalled manually.

### Design, operation, and safety

The custom slash command is `.claude/commands/week4-quality.md`. It accepts an
optional pytest path or expression through `$ARGUMENTS`, runs Black, Ruff, and the
relevant tests, then reports commands, passing tests, formatter changes, and the first
failure. Run `/week4-quality` from the repository root (for example,
`/week4-quality backend/tests/test_notes.py`) after creating the environment once:

```bash
cd week4
make setup
```

It uses only `.venv`, never Conda. Formatting is the only intentional file mutation;
changes remain visible in `git diff`. The command stops on its first failure and never
deletes data or modifies other weeks.

### Before, after, and application use

Before, a developer had to remember virtual-environment activation, formatting,
linting, and testing. After, one focused command invokes all three checks through
`.venv/bin/python`. I used it while adding case-insensitive note search, full note
replacement/deletion, request validation, and tag extraction tests.

## Automation #2 — `/week4-api-sync`

### Design inspiration

The sub-agents overview recommends narrow, well-defined responsibilities. This
documentation-review automation compares routes, schemas, and tests against one API
reference instead of relying on a general coding session to remember documentation
drift.

### Design, operation, and safety

The command is `.claude/commands/week4-api-sync.md`. It accepts an optional route or
feature, reads the FastAPI source and tests, compares them with `week4/docs/API.md`,
updates documented drift only, and then runs test and lint targets. From the repository
root, run `/week4-api-sync` or `/week4-api-sync notes search`. It expects the
environment produced by `cd week4 && make setup`.

Expected output is either no drift or a route-delta summary followed by passing checks.
It does not invent routes, start a persistent server, alter the database, or use Conda.
The only possible changes are reviewable documentation edits.

### Before, after, and application use

Before, the app had no API reference and route changes could leave users with stale
instructions. After, `docs/API.md` documents all Week 4 endpoints, payload limits, and
`404`/`422` behavior. I used it after adding `PUT /notes/{id}`, `DELETE /notes/{id}`,
and canonical `GET /notes/search?q=...`.

## Additional repository guidance

`CLAUDE.md` records Week 4 entry points, the `venv` commands, SQLAlchemy safety rules,
test order, and the API documentation gate, giving future agent sessions the same
project-specific context.
