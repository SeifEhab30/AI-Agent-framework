# Todos — Product Spec

Verified: 2026-08-25

## What it does
A minimal todo list. A todo has a title and a done flag.

## Behavior
- Create a todo with a non-empty title (whitespace-only titles are rejected).
- List all todos.
- Toggle a todo's done state.
- Delete a todo by id.
- [ready] Search todos by a case-insensitive substring match on title.

## Non-goals
No auth, no multi-user separation, no due dates, no persistence beyond local
SQLite. This is a demo domain for exercising the architecture, not a real
product yet.

## History
Originally named `widgets` (M1) — the folder/module/API paths were renamed
to `todos` on 2026-08-17 since the domain always behaved like a todo list;
`widgets` was freed up for an actual dashboard-widget domain (M13). Earlier
milestone entries (M1, M2, M3, M6...) still say "widgets" — that's accurate
history of what it was called at the time, not a stale reference.
