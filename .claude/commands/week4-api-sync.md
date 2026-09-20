---
description: Verify Week 4 API documentation against the FastAPI routes and tests.
argument-hint: "[route or feature to review]"
---

Review `week4/backend/app/main.py`, the router files, schemas, and relevant tests.
Compare them to `week4/docs/API.md`. Update the API document only when a documented
route, request payload, response, validation rule, or error behavior differs from the
source. Ensure the document includes any route mentioned in `$ARGUMENTS`.

Then run from `week4/`:

```bash
make test
make lint
```

Return a concise route-delta summary, files changed, and verification results. Do not
invent endpoints; do not use Conda; do not start a persistent server unless asked.
