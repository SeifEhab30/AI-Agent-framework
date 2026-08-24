"""Mechanically audits the Dispatcher Routine's one enforceable trace: its
GitHub Actions fire calls.

The Dispatcher never edits, commits, or pushes -- its live trigger's own
`allowed_tools` config has no Edit/Write/NotebookEdit at all, a stronger
guarantee than any script could give after the fact (a capability
restriction, not a check that runs after the damage is done). That
leaves nothing for a check_builder_scope.py-style diff check to look
at: Builder's violations show up as a git diff because it commits files;
the Dispatcher's only action is a tool call, and a tool call leaves no
diff to inspect.

What IS checkable mechanically is routine-fire.yml's own GitHub Actions
run history -- every workflow_dispatch is logged with a timestamp, and
(after this script's companion one-line addition to routine-fire.yml,
which now echoes `firing target=$TARGET`) the target it fired.

Within an explicit time window (--since/--until, always caller-supplied
-- this script does not and cannot infer a Dispatcher session's actual
start/end boundary from run history alone, since GitHub's run objects
carry no session-correlation id):
- every routine-fire.yml dispatch's target must be 'maintenance' or
  'builder'
- no target may appear more than once (the FORBIDDEN ACTIONS rule
  against firing an agent twice in one run, checked here as a
  same-window proxy, since actual session boundaries aren't visible
  from run history)
- any OTHER workflow dispatched in the same window is reported for
  human review, not auto-failed -- GitHub's run history doesn't
  reliably distinguish the Dispatcher's own MCP-driven dispatch from a
  human's manual `gh workflow run` under the same account, so
  attribution stays a human call, not a mechanical one

Known accepted gap, not covered here (same "documented, not hidden"
treatment check_builder_scope.py gives its own uncheckable case): whether
the Dispatcher attempted to call api.anthropic.com directly, or tried to
discover a trigger id/token. That only appears in the session's own
transcript, which no repo-local script can reach -- catching it needs a
human (or a future audit routine with session-log access) reading the
run log via RemoteTrigger, not this script.

Usage:
  python scripts/check_dispatcher_scope.py --since 2026-08-24T09:00:00Z
  python scripts/check_dispatcher_scope.py --since <iso8601> --until <iso8601>
"""

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime

# gh run list's --json output identifies a workflow by its display `name:`
# field (routine-fire.yml's own `name: Routine Fire Relay`), not its file
# path -- there's no file-path field available in the run list JSON.
FIRE_WORKFLOW = "Routine Fire Relay"
VALID_TARGETS = {"maintenance", "builder"}
TARGET_LINE_PATTERN = re.compile(r"firing target=(\S+)")


@dataclass
class Run:
    run_id: int
    workflow_name: str
    created_at: datetime
    event: str


def parse_ts(raw: str) -> datetime:
    return datetime.fromisoformat(raw.replace("Z", "+00:00"))


def _gh(*args: str) -> str:
    result = subprocess.run(
        ["gh", *args],
        capture_output=True,
        text=True,
        timeout=60,
        check=True,
    )
    return result.stdout


def list_workflow_dispatches(since: datetime, until: datetime) -> list[Run]:
    """All workflow_dispatch-triggered runs (any workflow) in [since, until]."""
    raw = _gh(
        "run",
        "list",
        "--json",
        "databaseId,workflowName,createdAt,event",
        "--limit",
        "200",
    )
    runs = []
    for entry in json.loads(raw):
        if entry.get("event") != "workflow_dispatch":
            continue
        created = parse_ts(entry["createdAt"])
        if since <= created <= until:
            runs.append(
                Run(
                    run_id=entry["databaseId"],
                    workflow_name=entry["workflowName"],
                    created_at=created,
                    event=entry["event"],
                )
            )
    return runs


def fire_target(run_id: int) -> str | None:
    """The target routine-fire.yml fired, parsed from its own echoed log line."""
    try:
        log = _gh("run", "view", str(run_id), "--log")
    except subprocess.CalledProcessError:
        return None
    match = TARGET_LINE_PATTERN.search(log)
    return match.group(1) if match else None


def check_window(since: datetime, until: datetime) -> list[str]:
    issues: list[str] = []
    dispatches = list_workflow_dispatches(since, until)

    fire_runs = [r for r in dispatches if r.workflow_name == FIRE_WORKFLOW]
    other_runs = [r for r in dispatches if r.workflow_name != FIRE_WORKFLOW]

    for run in other_runs:
        issues.append(
            f"informational: workflow '{run.workflow_name}' (run {run.run_id}) was "
            f"dispatched at {run.created_at.isoformat()}, inside the audited window -- "
            f"not attributable to the Dispatcher or ruled out as human-triggered, "
            f"flagging for review"
        )

    seen_targets: dict[str, int] = {}
    for run in fire_runs:
        target = fire_target(run.run_id)
        if target is None:
            issues.append(
                f"run {run.run_id}: could not determine fired target from its log "
                f"-- routine-fire.yml may predate the 'firing target=' echo"
            )
            continue
        if target not in VALID_TARGETS:
            issues.append(
                f"run {run.run_id}: fired target '{target}' is not one of "
                f"{sorted(VALID_TARGETS)}"
            )
        if target in seen_targets:
            issues.append(
                f"run {run.run_id}: target '{target}' already fired by run "
                f"{seen_targets[target]} earlier in this window -- "
                f"an agent must not be fired twice in one run"
            )
        else:
            seen_targets[target] = run.run_id

    return issues


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--since", required=True, help="ISO 8601 timestamp, window start")
    parser.add_argument(
        "--until", default=None, help="ISO 8601 timestamp, window end (default: now)"
    )
    args = parser.parse_args()

    since = parse_ts(args.since)
    until = parse_ts(args.until) if args.until else datetime.now(since.tzinfo)

    issues = check_window(since, until)

    if not issues:
        print("check_dispatcher_scope: no violations found.")
        return 0

    print(f"check_dispatcher_scope: {len(issues)} finding(s):\n")
    for issue in issues:
        print(f"  {issue}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
