# Assignments for CS146S: The Modern Software Developer

This is an independent, educational repository for working through assignments inspired by [CS146S: The Modern Software Developer](https://themodernsoftware.dev), taught at Stanford University in Fall 2025.

It is a personal learning project and is not an official Stanford University or CS146S repository. It is not affiliated with or endorsed by Stanford University or the course staff.

## Weekly Progress

### Week 1 — Prompting Techniques

Built a Python prompting playground that explores practical ways to work with coding-oriented language models:

- Chain-of-thought prompting
- Few-shot prompting
- Retrieval-augmented generation over API documentation
- Self-consistency prompting
- Reflexion-style improvement loops
- Tool calling

See [Week 1](./week1/).

### Week 2 — Action Item Extractor

Built a FastAPI application that turns meeting notes into actionable tasks:

- Rule-based extraction for bullets, checkboxes, keywords, and simple imperative sentences
- Local Ollama-powered extraction with structured JSON output
- SQLite persistence for notes and action-item completion state
- Browser interface and documented API endpoints
- Unit tests for extraction behavior

See [Week 2](./week2/).

### Week 3 — Ship Cycle MCP

Built a local Model Context Protocol server for turning development activity into release communications:

- GitHub activity collection with pagination, validation, rate-limit handling, and error reporting
- Local Git history support, including unpushed commits
- Commit-first launch briefs for developer, customer, or internal audiences
- Local Ollama-generated X and LinkedIn drafts, with a deterministic fallback when Ollama is unavailable
- Tests for GitHub, local Git, Ollama, and fallback behavior

See [Week 3](./week3/).

### Week 4 — Coding-Agent Automations

Built a venv-based FastAPI workflow with reusable coding-agent automations:

- `/week4-quality` to format, lint, and test a focused change
- `/week4-api-sync` to prevent API-documentation drift
- Full note search, edit, delete, validation, tag extraction, and browser controls
- API reference, pre-commit hook, and regression tests

See [Week 4](./week4/).

### Weeks 5–8 — Upcoming Work

The repository includes the assignment materials and starter projects for later weeks. These assignments are not yet documented as completed:

| Week | Focus |
| --- | --- |
| 5 | Modern terminal and multi-agent workflows |
| 6 | AI testing and security |
| 7 | Software support, reviews, and API improvements |
| 8 | Automated UI and app building |
