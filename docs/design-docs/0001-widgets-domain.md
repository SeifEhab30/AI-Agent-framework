# 0001 — Widgets Domain

Verified: 2026-08-26

## Status
Accepted

## Context
We need one reference domain to prove the layered architecture, provider
pattern, and lint enforcement end to end, without real business complexity
getting in the way.

## Decision
Build a trivial "widgets" domain — a todo-list-like resource (id, title,
done, created_at) — as the single reference implementation of the six-layer
convention. See [docs/architecture/layering.md](../architecture/layering.md)
for the layering rule and [docs/product-specs/todos.md](../product-specs/todos.md)
for behavior (renamed `widgets` → `todos` at M13, along with a genuine new
`widgets` domain being added separately — see that file's own History
section; this design doc's own title still says "Widgets" as the accurate
historical name at the time it was written, per house style against
silently rewriting history).

## Consequences
Future domains copy this folder's structure rather than inventing their own.

See also old notes for early exploration.
