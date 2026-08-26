# Reminders — Product Spec

Verified: 2026-08-26

## What it does
A minimal reminder. A reminder has a message and a due_at timestamp.

## Behavior
- Create a reminder with a non-empty message and a due_at that is in the future (past or present due_at is rejected).
- List all reminders.
- Mark a reminder done by id.
- Delete a reminder by id.

## Non-goals
No auth, no multi-user separation, no recurrence, no notifications, no
relation to the other four domains. Fifth domain, the first built
entirely by the Builder Routine rather than by hand — see
[docs/exec-plans/active/milestones.md](../exec-plans/active/milestones.md) M14.
