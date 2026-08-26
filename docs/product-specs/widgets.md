# Widgets — Product Spec

Verified: 2026-08-26

## What it does
A minimal dashboard widget: a labeled numeric value (e.g. a counter or
stat tile), distinct from the `todos` domain (which used to be called
`widgets` — see `docs/product-specs/todos.md` History section).

## Behavior
- Create a widget with a non-empty label and a starting value (defaults
  to 0 if omitted).
- List all widgets.
- Set a widget's value to a new number.
- Delete a widget by id.

## Non-goals
No auth, no multi-user separation, no charts/history of past values, no
relation to the other three domains. Fourth domain, added to prove the
layering/providers pattern holds at four domains and to give "widget" its
actual meaning in this app.

See also design notes for background.
