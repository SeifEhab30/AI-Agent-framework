# AI Agent — Todoapp

A small FastAPI + SQLite demo app used as a reference implementation for an
agent-driven engineering workflow: enforced layered architecture, structured
docs, doc staleness checks, and lint-enforced golden principles.

Start here: [MAP.md](MAP.md)

## Quickstart

```bash
pip install -r requirements.txt
uvicorn todoapp.app:app --reload
```

Runs widgets, notes, and bookmarks together under one app. Each domain is
also independently runnable (e.g. `uvicorn todoapp.widgets.ui:app`) for
isolated testing.
