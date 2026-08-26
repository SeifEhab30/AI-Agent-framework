"""Mechanically audits any open PR before the merge-gate agent may merge it --
not restricted to Builder's own `agentic-build/*` branches (widened
2026-08-26; branch/author no longer gate eligibility, only diff shape and
the traceability convention do). A PR that doesn't follow the traceability-
table convention (see check 3) still won't pass -- that convention, not
branch naming, is what actually distinguishes an eligible PR now.

Reads everything through `gh` and `git show <ref>:<path>` against the PR's
own head commit -- never runs `gh pr checkout` or any local clone/install.
There is nothing to clean up because nothing is ever written to disk: no
scratch checkout, no temp test run, no junk folder left behind in the repo
or anywhere else. `git fetch origin pull/<n>/head` only updates FETCH_HEAD
(a ref), not the working tree.

Checks, in order:
0. Critical-path gate: the diff touches no CI/workflow config, no gate
   script (this one included -- a PR can't certify itself), no agent
   prompt, and no dependency/build config. Any hit here is rejected
   immediately, before CI/branch/traceability are even looked at -- this
   repo's analog to an auth/security carve-out, since it has no actual
   auth domain of its own. See CRITICAL_PATH_PREFIXES.
1. Every CI check on the PR has concluded SUCCESS. This script does not
   re-run ruff/pytest/lint-imports/check_golden_rules.py/
   check_builder_scope.py itself -- CI already re-executes all of those
   fresh, independent of anything the PR's own description claims, and
   redoing that here would just pay twice for an answer already given.
2. The diff shape matches frontend_only, frontend_update, or
   existing_domain (exactly one backend domain touched, no frontend
   touched) -- regardless of branch or author. new_domain (touches both
   backend and frontend at once -- the biggest blast radius) is still not
   auto-mergeable, same "prove narrow, then widen" discipline as every
   other capability this repo has added -- frontend_only was proven live
   first (PR #82), then widened to the other two modes, then (2026-08-26)
   to any branch/author for those same three modes.
3. Traceability table structural check: the PR body's table lists every
   spec requirement for the target domain (not just what changed this
   run), one row per requirement plus three fixed frontend rows whenever
   the domain has a frontend, each marked Modified (a genuinely new test
   in this diff) or Not modified (an existing test, from an earlier PR,
   still covering it). Row count must match the domain's actual
   requirement count; each Modified row's test must be newly added in the
   diff; each Not modified row's test must actually exist in the repo at
   this PR's head commit. A lower bound only, same caveat
   check_builder_scope.py's own check_traceability documents -- proves
   the row isn't fabricated, not that the test actually covers what the
   requirement claims.

Once every mechanical check above passes, one further step runs: a
single-shot, read-only semantic review (via scripts/run-agent.sh -- see
that file for why it's the only place a specific agent CLI is named)
asking whether each named test genuinely proves its paired spec bullet,
not merely that it exists. That's a judgment CI's mechanical suite is
structurally unable to make; this script can only clear the mechanical
floor, so it hands that one question to a model rather than skipping it.
Pass --mechanical-only to stop before this step (e.g. for local testing
without agent-CLI credentials available).

No `gh` CLI in your environment? Don't hand-replicate this script's logic
from memory -- fetch the same inputs some other way (e.g. GitHub MCP
tools) and run the real check via --from-json instead. See that flag's
help text for the exact JSON shape, and merge-gate-prompt.md for the
step-by-step.

Usage:
  python scripts/check_merge_gate.py --pr 73
  python scripts/check_merge_gate.py --pr 73 --mechanical-only
  python scripts/check_merge_gate.py --from-json data.json --mechanical-only
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

FRONTEND_ROW_COUNT = 3  # initial render, create-success, create-validation-error

# Path-based "critical" gate: this repo has no auth/security domain of its
# own, so the closest analog is the machinery that decides what code is
# trustworthy in the first place -- CI/workflow config (secrets live here),
# the mechanical gate scripts (this file included -- a PR can't certify
# itself), the agent prompts (define what an agent is even allowed to do),
# and dependency/build config (supply-chain surface). A PR touching any of
# these is never auto-mergeable, regardless of branch prefix or diff shape
# -- always left for a human, no exception. Prefix-matched against every
# changed path.
CRITICAL_PATH_PREFIXES = (
    ".github/workflows/",
    "scripts/check_merge_gate.py",
    "scripts/check_builder_scope.py",
    "scripts/check_dispatcher_scope.py",
    "scripts/check_golden_rules.py",
    "scripts/doc_gardener.py",
    "scripts/run-agent.sh",
    "docs/references/",
    "pyproject.toml",
    "requirements.in",
    "requirements.txt",
    ".pre-commit-config.yaml",
    ".env.example",
    "frontend/package.json",
    "frontend/package-lock.json",
    "frontend/vite.config.js",
    ".claude/",
)
# This pattern's format contract is defined in prose in builder-prompt.md's
# "Test column format" paragraph -- that's the source of truth for what a
# valid row looks like (bare test name, comma-separated for multiple tests,
# no filename prefix). If that paragraph ever changes, this pattern must
# change with it, and vice versa -- nothing else keeps the two in sync.
TABLE_ROW_PATTERN = re.compile(
    r"^\|\s*(.+?)\s*\|\s*(Modified|Not modified)\s*\|\s*(.+?)\s*\|\s*$",
    re.MULTILINE | re.IGNORECASE,
)
SPEC_BULLET_PATTERN = re.compile(r"^- (?:\[ready\]\s*)?(.+)$", re.MULTILINE)
REVIEW_PROMPT_TEMPLATE = (
    Path(__file__).resolve().parent.parent / "docs" / "references" / "merge-gate-review-prompt.md"
)
RUN_AGENT = Path(__file__).resolve().parent / "run-agent.sh"


def _gh(*args: str) -> str:
    result = subprocess.run(["gh", *args], capture_output=True, text=True, timeout=60, check=True)
    return result.stdout


def _git(*args: str) -> str:
    result = subprocess.run(["git", *args], capture_output=True, text=True, timeout=60, check=True)
    return result.stdout


def pr_view(pr: int) -> dict:
    raw = _gh(
        "pr",
        "view",
        str(pr),
        "--json",
        "headRefName,baseRefName,body,files,statusCheckRollup,headRefOid",
    )
    return json.loads(raw)


def check_ci_green(info: dict) -> list[str]:
    rollup = info.get("statusCheckRollup") or []
    if not rollup:
        return ["no CI check runs found on this PR yet -- not eligible until CI has run"]
    issues = []
    for check in rollup:
        conclusion = check.get("conclusion")
        name = check.get("name", "<unnamed check>")
        if conclusion != "SUCCESS":
            issues.append(f"required check '{name}' concluded '{conclusion}', not SUCCESS")
    return issues


def check_critical_paths(info: dict) -> list[str]:
    """Never auto-mergeable, no matter what else about the PR is clean --
    checked first, ahead of even CI/branch/traceability, so a critical-path
    PR is rejected for the right reason even if it happens to also fail
    something else."""
    paths = [f["path"] for f in info.get("files", [])]
    hits = sorted(
        p for p in paths if any(p.startswith(prefix) for prefix in CRITICAL_PATH_PREFIXES)
    )
    if hits:
        return [
            f"touches critical path(s) {hits} -- CI/workflow config, gate scripts, "
            f"agent prompts, and dependency/build config are never auto-merged, "
            f"always left for human review"
        ]
    return []


def check_diff_mode(info: dict) -> list[str]:
    """Accepts two diff shapes, from any branch or author -- branch prefix no
    longer gates eligibility (widened 2026-08-26): frontend_only/
    frontend_update (no backend domain touched, a frontend component
    touched -- the two aren't distinguished here, same traceability logic
    covers both) and existing_domain (exactly one backend domain touched, no
    frontend touched). Rejects new_domain (touches both -- the biggest blast
    radius, not auto-mergeable) and anything touching neither."""
    paths = [f["path"] for f in info.get("files", [])]
    backend_domains = {
        p.split("/")[2]
        for p in paths
        if p.startswith("src/todoapp/") and p != "src/todoapp/app.py" and len(p.split("/")) >= 3
    }
    touches_frontend = any(p.startswith("frontend/src/components/") for p in paths)

    if backend_domains and touches_frontend:
        return [
            "diff touches both a backend domain and a frontend component -- "
            "looks like new_domain (or a mixed build), outside current "
            "auto-merge eligibility"
        ]
    if not backend_domains and not touches_frontend:
        return [
            "diff touches neither src/todoapp/<domain>/ nor a frontend component "
            "-- doesn't match any recognized eligible diff shape"
        ]
    if len(backend_domains) > 1:
        return [
            f"diff touches more than one backend domain: {sorted(backend_domains)} "
            f"-- outside Builder's own single-domain-per-run scope, should never happen"
        ]
    return []


def spec_path_for(info: dict) -> str | None:
    for f in info.get("files", []):
        path = f["path"]
        if path.startswith("docs/product-specs/") and path.endswith(".md"):
            return path
    return None


def spec_text_at(pr: int, path: str) -> str:
    """Reads a file's content at the PR's head commit without checking anything
    out -- fetches only the ref (FETCH_HEAD), never touches the working tree."""
    _git("fetch", "origin", f"pull/{pr}/head")
    return _git("show", f"FETCH_HEAD:{path}")


def extract_test_body(diff: str, name: str) -> str:
    """The added (`+`-prefixed) lines of one test's diff hunk, stripped of the
    leading `+`. Works for a Python `def <name>(` line or, for a frontend JS
    test, any added line containing <name> as a literal substring (e.g. a
    test('...', ...) title) -- collects from that marker line until the next
    added `def` line or a hunk boundary."""
    lines = diff.splitlines()
    body_lines: list[str] = []
    collecting = False
    for line in lines:
        is_marker = line.startswith("+") and (f"def {name}(" in line or name in line)
        if is_marker and not collecting:
            collecting = True
            body_lines.append(line[1:])
            continue
        if collecting:
            if line.startswith("@@") or (line.startswith("+def ") and name not in line):
                break
            if line.startswith("+"):
                body_lines.append(line[1:])
    return "\n".join(body_lines)


def head_file_text(path: str) -> str:
    """File content at the PR's head commit (FETCH_HEAD must already be set --
    see spec_text_at), or "" if the path doesn't exist there."""
    result = subprocess.run(
        ["git", "show", f"FETCH_HEAD:{path}"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout if result.returncode == 0 else ""


def frontend_component_exists(pr: int, domain: str) -> bool:
    """Whether this domain has a frontend at the PR's head commit -- already
    built (frontend_only/new_domain runs), already existed
    (frontend_update/existing_domain), or genuinely none yet. Determines
    whether the traceability table should carry the three fixed frontend
    rows."""
    _git("fetch", "origin", f"pull/{pr}/head")
    result = subprocess.run(
        ["git", "cat-file", "-e", f"FETCH_HEAD:frontend/src/components/{domain.capitalize()}.jsx"],
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def check_traceability(pr: int, info: dict) -> tuple[list[str], list[dict]]:
    """Fetches everything check_traceability_pure needs via gh/git, then
    delegates to it. See that function for the actual check logic -- kept
    separate so an environment without `gh` (see --from-json / run-agent.sh
    docstring, and merge-gate-prompt.md) can fetch the same inputs some
    other way (e.g. GitHub MCP tools) and call the pure function directly,
    instead of an agent re-deriving this logic from memory each run."""
    spec_path = spec_path_for(info)
    if spec_path is None:
        return (
            ["no docs/product-specs/*.md file in this diff -- can't locate the target spec"],
            [],
        )
    domain = spec_path.rsplit("/", 1)[-1].removesuffix(".md")

    try:
        spec_text = spec_text_at(pr, spec_path)
    except subprocess.CalledProcessError:
        return ([f"could not read {spec_path} at PR head commit"], [])

    frontend_exists = frontend_component_exists(pr, domain)
    diff = _gh("pr", "diff", str(pr))
    existing_test_text = head_file_text(f"tests/{domain}/test_service.py") + head_file_text(
        f"frontend/src/components/{domain.capitalize()}.test.jsx"
    )
    body = info.get("body") or ""

    return check_traceability_pure(spec_text, frontend_exists, body, diff, existing_test_text)


def check_traceability_pure(
    spec_text: str,
    frontend_exists: bool,
    pr_body: str,
    diff: str,
    existing_test_text: str,
) -> tuple[list[str], list[dict]]:
    """The actual traceability check, with no I/O of its own -- takes
    already-fetched strings so it can be called identically whether they
    came from `gh`/`git show` (check_traceability) or from GitHub MCP tools
    (--from-json). Returns (issues, rows).

    Table convention (builder-prompt.md): one row per spec requirement for
    the target domain, ALWAYS -- not just what changed this run -- plus
    three fixed frontend rows whenever the domain has a frontend. Each row
    is Modified (a genuinely new test, this diff) or Not modified (an
    existing test, from an earlier PR, unchanged). This is what makes the
    table meaningful for frontend_only/frontend_update runs: most or all
    backend rows there are legitimately Not modified, which is a complete
    accurate table, not a red flag.

    `rows` returned is only the Modified ones -- what the semantic review
    step needs to judge. Not modified rows are already covered by CI
    passing on tests that already existed; nothing new to judge there."""
    requirement_count = len(SPEC_BULLET_PATTERN.findall(spec_text))
    frontend_rows_expected = FRONTEND_ROW_COUNT if frontend_exists else 0
    expected_total = requirement_count + frontend_rows_expected

    table_rows = TABLE_ROW_PATTERN.findall(pr_body)  # (requirement, status, test)

    issues = []
    if len(table_rows) != expected_total:
        issues.append(
            f"expected {expected_total} traceability row(s) "
            f"({requirement_count} spec requirement(s) + {frontend_rows_expected} "
            f"frontend case(s)) but PR body has {len(table_rows)}"
        )

    added_lines = "\n".join(line for line in diff.splitlines() if line.startswith("+"))

    rows = []
    for requirement, status, test_ref in table_rows:
        # builder-prompt.md's Test column format: one or more bare names,
        # comma-separated when a requirement needs more than one test --
        # split and match each individually rather than the whole cell as
        # one literal string.
        names = [n.strip("`'\" ") for n in test_ref.split(",")]
        modified = status.strip().lower() == "modified"
        for name in names:
            if not name:
                continue
            haystack = added_lines if modified else existing_test_text
            if name not in haystack:
                where = (
                    "no added line in the diff contains it"
                    if modified
                    else ("it doesn't appear in the existing test files at this PR's head commit")
                )
                issues.append(
                    f"traceability table marks '{requirement}' "
                    f"{'Modified' if modified else 'Not modified'}, naming '{name}', but {where}"
                )
                continue
            if modified:
                rows.append(
                    {
                        "bullet": requirement,
                        "function": name,
                        "body": extract_test_body(diff, name),
                    }
                )

    return issues, rows


def run_semantic_review(rows: list[dict]) -> list[str]:
    """The one judgment call this script can't make mechanically: does each
    named test genuinely prove its paired bullet. Delegates to
    scripts/run-agent.sh (the only place a specific agent CLI is named) with
    a single-shot, read-only prompt -- see merge-gate-review-prompt.md."""
    template = REVIEW_PROMPT_TEMPLATE.read_text(encoding="utf-8")
    rows_text = "\n\n".join(
        f"### Row\nSpec bullet: {r['bullet']}\n"
        f"Test function ({r['function']}):\n```\n{r['body']}\n```"
        for r in rows
    )
    prompt = template.replace("{{ROWS}}", rows_text)

    try:
        result = subprocess.run(
            [str(RUN_AGENT)],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=180,
            check=True,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        return [f"semantic review call failed, treating as not eligible: {exc}"]

    try:
        verdict = json.loads(result.stdout.strip())
    except json.JSONDecodeError:
        return [
            f"semantic review returned non-JSON output, treating as not eligible: {result.stdout!r}"
        ]

    if verdict.get("eligible"):
        return []
    issues = []
    for row in verdict.get("failing_rows", []):
        label = "FAILS" if row.get("verdict") == "fails" else "UNCERTAIN, needs human judgment"
        issues.append(f"semantic review [{label}]: '{row.get('bullet')}' -- {row.get('reason')}")
    return issues or ["semantic review returned eligible=false with no failing_rows detail"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pr", type=int, help="PR number -- fetches via gh/git")
    parser.add_argument(
        "--from-json",
        type=Path,
        help=(
            "Run against pre-fetched data instead of calling gh/git -- for an "
            "environment without the gh CLI (see merge-gate-prompt.md). JSON "
            "shape: {info: {headRefName, baseRefName, body, files, "
            "statusCheckRollup}, spec_text, frontend_exists, diff, "
            "existing_test_text} -- same fields gh/git would have fetched, "
            "gathered instead via GitHub MCP tools."
        ),
    )
    parser.add_argument(
        "--mechanical-only",
        action="store_true",
        help="Stop after the mechanical checks -- skip the semantic review call",
    )
    args = parser.parse_args()

    if args.from_json:
        data = json.loads(args.from_json.read_text(encoding="utf-8"))
        info = data["info"]
        trace_issues, rows = check_traceability_pure(
            data["spec_text"],
            data["frontend_exists"],
            info.get("body") or "",
            data["diff"],
            data["existing_test_text"],
        )
    else:
        if not args.pr:
            parser.error("--pr is required unless --from-json is given")
        info = pr_view(args.pr)
        trace_issues, rows = check_traceability(args.pr, info)

    issues: list[str] = []
    issues.extend(check_critical_paths(info))
    issues.extend(check_ci_green(info))
    issues.extend(check_diff_mode(info))
    issues.extend(trace_issues)

    if issues:
        print(f"check_merge_gate: {len(issues)} finding(s), not eligible for auto-merge:\n")
        for issue in issues:
            print(f"  {issue}")
        return 1

    if args.mechanical_only:
        print(
            "check_merge_gate: mechanical checks clean, skipped semantic review "
            "(--mechanical-only)."
        )
        return 0

    if not rows:
        print(
            "check_merge_gate: mechanical checks clean but no 'Modified' "
            "traceability rows -- nothing new to review this run."
        )
        return 1

    semantic_issues = run_semantic_review(rows)
    if semantic_issues:
        print(
            f"check_merge_gate: {len(semantic_issues)} finding(s), not eligible for auto-merge:\n"
        )
        for issue in semantic_issues:
            print(f"  {issue}")
        return 1

    print("check_merge_gate: no violations found, mechanical and semantic checks both clean.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
