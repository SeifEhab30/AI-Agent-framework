# Widgets (Todo) — Product Spec

Verified: 2026-08-12

## What it does
A minimal todo list. A widget has a title and a done flag.

## Behavior
- Create a widget with a non-empty title (whitespace-only titles are rejected).
- List all widgets.
- Toggle a widget's done state.

## Non-goals
No auth, no multi-user separation, no due dates, no persistence beyond local
SQLite. This is a demo domain for exercising the architecture, not a real
product yet.
