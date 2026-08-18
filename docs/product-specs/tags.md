# Tags — Product Spec

Verified: 2026-08-18
Status: Ready for implementation

## What it does
A minimal tag: a short name attached to nothing in particular yet.

## Behavior
- Create a tag with a name.
- Tag names must be unique across all tags — creating a duplicate name
  is rejected.
- Duplicate tag names are allowed, since the same name can mean
  different things in different contexts.
- List all tags, in alphabetical order.
- List all tags, in creation order, since that's more useful for
  recent-first display.

## Non-goals
No auth, no multi-user separation, no relation to the other domains.
