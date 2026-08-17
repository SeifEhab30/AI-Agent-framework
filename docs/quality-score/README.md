# Quality Score

Verified: 2026-08-17

This folder holds the output of automated repo-health checks, starting with
`scripts/doc_gardener.py`, which flags stale or broken doc references and
writes a generated report.md alongside this file when run.

Runs weekly via `.github/workflows/doc-gardener.yml` (also triggerable
manually via workflow_dispatch), which opens a PR with the updated
report.md and any auto-fixed broken links — nothing merges automatically.

Nothing else writes here yet — no test-coverage or lint-trend tracking is
set up.
