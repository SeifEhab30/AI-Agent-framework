# Notes — Product Spec

Verified: 2026-08-26

## What it does
A minimal note. A note has a title and a body.

## Behavior
- Create a note with a non-empty title (blank or whitespace-only titles are rejected).
- List all notes.
- Update a note's body.
- Delete a note by id.
- Search notes by a case-insensitive substring match on title.

## Non-goals
No auth, no multi-user separation, no rich text, no relation to the
`widgets` domain. This domain exists to prove the layering/providers
pattern generalizes past one domain — see
[docs/exec-plans/active/milestones.md](../exec-plans/active/milestones.md) M2.

See also old notes draft for early exploration.
