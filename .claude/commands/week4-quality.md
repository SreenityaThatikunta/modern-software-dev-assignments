---
description: Run the Week 4 quality gate, optionally against a focused test path.
argument-hint: "[pytest path or -k expression]"
---

From the repository root, inspect the working tree without changing unrelated files.
Then run these commands from `week4/` using the project virtual environment:

```bash
make format
make lint
PYTHONPATH=. .venv/bin/python -m pytest -q backend/tests $ARGUMENTS
```

Report the exact commands run, number of passing tests, and any changed files from
formatting. If a command fails, stop at the first failure, explain the smallest likely
cause, and do not make broad or destructive changes. Never use Conda.
