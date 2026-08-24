# Tags — Product Spec

Verified: 2026-08-24

## What it does
A minimal tag: a short name attached to nothing in particular yet.

## Behavior
- Create a tag with a name.
- Duplicate tag names are allowed, since the same name can mean
  different things in different contexts.
- List all tags, in creation order, since that's more useful for
  recent-first display.
- [ready] Search tags by a case-insensitive substring match on name.

## Non-goals
No auth, no multi-user separation, no relation to the other domains.
