# Bookmarks — Product Spec

Verified: 2026-08-18

## What it does
A minimal bookmark. A bookmark has a URL and a title.

## Behavior
- Create a bookmark with a non-empty URL and title.
- List all bookmarks.
- Rename a bookmark's title.
- [ready] Search bookmarks by a case-insensitive substring match on title.

## Non-goals
No auth, no multi-user separation, no folders/tags, no relation to the
`widgets` or `notes` domains. This is the third domain used to confirm the
layering/providers pattern holds across multiple independent domains — see
[docs/exec-plans/active/milestones.md](../exec-plans/active/milestones.md) M3.

See also old bookmarks prototype for early exploration.
