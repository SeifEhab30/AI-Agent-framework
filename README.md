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

Runs todos, notes, bookmarks, and widgets together under one app. Each
domain is also independently runnable (e.g. `uvicorn todoapp.todos.ui:app`)
for isolated testing.

## Frontend

```bash
cd frontend
npm install
npm run dev
```

React + Vite, talks to the backend at `http://localhost:8000` (CORS is
enabled for `http://localhost:5173`, the Vite dev server's default port).
Run the backend first.
