# Labels — Product Spec

Verified: 2026-08-18
Status: Ready for implementation

## What it does
A minimal label: a name and a color, for tagging things elsewhere in the
app later (no relation wired up yet — this domain only manages labels
themselves).

## Behavior
- Create a label with a non-empty name and a color in `#RRGGBB` hex
  format (reject anything else).
- List all labels.
- Delete a label by id.

## Non-goals
No auth, no multi-user separation, no attaching labels to other domains'
records yet, no relation to the other five domains. Sixth domain, a
clean unambiguous spec for exercising the Builder Routine's new-domain
path a second time.

See also [color palette notes](docs/design-docs/0003-labels-color-palette.md) for background.
