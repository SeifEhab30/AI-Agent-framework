# 0001 — Widgets Domain

Verified: 2026-08-12

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
for the layering rule and [docs/product-specs/widgets-todo.md](../product-specs/widgets-todo.md)
for behavior.

## Consequences
Future domains copy this folder's structure rather than inventing their own.
