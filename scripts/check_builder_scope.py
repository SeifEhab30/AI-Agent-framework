"""Mechanically enforces the Builder Routine's scope guard.

A prompt-only scope guard is a policy the Builder is asked to follow, not
a rule it physically can't break -- this repo doesn't trust conventions
alone anywhere else (that's why golden rules exist), so the Builder's
much larger authority (six-layer domain creation) gets the same
treatment: a diff-based gate that runs as part of its own validation
suite and in CI on any agentic-build/* branch (which needs a full,
non-shallow fetch of origin/master to diff against -- fetch-depth: 0,
same requirement doc_gardener.py already has for its own git-based
checks).

Compares the current branch against a base ref (default origin/master)
and fails if the diff touches anything the Builder's scope guard
(docs/references/builder-prompt.md) forbids universally, regardless of
which domain is this run's target:

- Maintenance-agent and tooling files that are off-limits to the Builder.
- frontend/, .github/workflows/*, CI config.
- More than one domain directory touched in the same diff (app.py/
  pyproject.toml/MAP.md registration edits are exempt -- mechanical, not
  business logic).
- Any *existing* import-linter contract modified -- checked structurally
  via tomllib (multiset/dict-equality, not line-position diffing, so
  reordering or formatting can't false-positive). The independence
  contract is a deliberate, narrow exception: its `modules` list is
  allowed to grow (the Builder must add its new domain to it), but only
  as a superset -- nothing may be removed, and no other field may change.
- Traceability: the target spec's ready-marked requirements must each be
  backed by a genuinely new test function (name diffed against base, not
  just present in the file) -- a lower bound only. This doesn't prove
  semantic coverage (a human still verifies the table makes sense), but
  it kills a self-reported table that overclaims how many requirements
  are actually tested.

Known accepted gap for v1, not mechanically checked: whether an
existing-domain run touched only the files *strictly necessary* for its
one target behavior ("smallest coherent set" in builder-prompt.md).
There's no honest way to check "necessity" without natural-language
understanding of the change -- this stays a human-review item, backed by
the PR's required per-file justification and the negative-capability
checklist in docs/exec-plans/active/milestones.md's M15 entry.

Usage: python scripts/check_builder_scope.py [--base <ref>]
"""

import argparse
import ast
import re
import subprocess
import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src" / "todoapp"

FORBIDDEN_PATHS = (
    "docs/quality-score/findings-log.md",
    "docs/references/routine-prompt.md",
    "docs/references/builder-prompt.md",
    "scripts/check_golden_rules.py",
    "scripts/doc_gardener.py",
    "scripts/check_builder_scope.py",
    "frontend/src/App.css",
    "frontend/src/index.css",
    "frontend/vite.config.js",
    "frontend/package.json",
    "frontend/package-lock.json",
    "frontend/.oxlintrc.json",
    ".github/workflows/",
)

FRONTEND_COMPONENTS_DIR = "frontend/src/components/"
FRONTEND_API_PATH = "frontend/src/api.js"

# app.py/pyproject.toml/MAP.md/App.jsx/api.js are mechanical registration
# edits and are evaluated by their own dedicated checks below, not by the
# domain-count check.
REGISTRATION_PATHS = (
    "src/todoapp/app.py",
    "pyproject.toml",
    "MAP.md",
    "frontend/src/App.jsx",
    FRONTEND_API_PATH,
)

STATUS_READY_PATTERN = re.compile(r"^Status:\s*Ready for implementation\s*$", re.MULTILINE)
READY_BULLET_PATTERN = re.compile(r"^-\s*\[ready\]", re.MULTILINE)
BEHAVIOR_SECTION_PATTERN = re.compile(r"^## Behavior\s*$(.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL)
BEHAVIOR_BULLET_PATTERN = re.compile(r"^-\s+\S", re.MULTILINE)


def changed_files(base: str) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def check_forbidden_paths(files: list[str]) -> list[str]:
    issues = []
    for f in files:
        for forbidden in FORBIDDEN_PATHS:
            if f == forbidden or f.startswith(forbidden):
                issues.append(f"{f}: forbidden path -- outside the Builder's scope guard")
    return issues


def target_domain(files: list[str]) -> str | None:
    """The single domain this diff touches, or None if none/ambiguous."""
    domains = set()
    for f in files:
        if f in REGISTRATION_PATHS:
            continue
        parts = Path(f).parts
        if len(parts) >= 3 and parts[0] == "src" and parts[1] == "todoapp":
            domains.add(parts[2])
        elif len(parts) >= 2 and parts[0] == "tests":
            domains.add(parts[1])
    return next(iter(domains)) if len(domains) == 1 else None


def check_domain_count(files: list[str]) -> list[str]:
    domains = set()
    for f in files:
        if f in REGISTRATION_PATHS:
            continue
        parts = Path(f).parts
        if len(parts) >= 3 and parts[0] == "src" and parts[1] == "todoapp":
            domains.add(parts[2])
        elif len(parts) >= 2 and parts[0] == "tests":
            domains.add(parts[1])
    if len(domains) > 1:
        return [
            f"more than one domain touched in a single run: {sorted(domains)} "
            f"-- the Builder may only work on one domain per run"
        ]
    return []


def load_pyproject_contracts(ref: str) -> list[dict]:
    """Parse pyproject.toml's import-linter contracts at a given git ref."""
    result = subprocess.run(
        ["git", "show", f"{ref}:pyproject.toml"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    data = tomllib.loads(result.stdout)
    return data.get("tool", {}).get("importlinter", {}).get("contracts", [])


def check_contracts_only_appended(base: str) -> list[str]:
    """Every contract present at base must be structurally unchanged on HEAD,
    except the independence contract, whose `modules` list may only grow.
    The Builder may otherwise only append whole new contracts, never edit one."""
    try:
        base_contracts = load_pyproject_contracts(base)
        head_contracts = load_pyproject_contracts("HEAD")
    except subprocess.CalledProcessError:
        return ["could not read pyproject.toml at base or HEAD -- cannot verify contracts"]

    issues = []
    for contract in base_contracts:
        if contract in head_contracts:
            continue
        if contract.get("type") == "independence":
            head_match = next((c for c in head_contracts if c.get("type") == "independence"), None)
            if head_match is None:
                issues.append(
                    "pyproject.toml: the independence contract was removed -- "
                    "the Builder may only add its domain to it, never remove it"
                )
                continue
            base_modules = set(contract.get("modules", []))
            head_modules = set(head_match.get("modules", []))
            non_module_base = {k: v for k, v in contract.items() if k != "modules"}
            non_module_head = {k: v for k, v in head_match.items() if k != "modules"}
            if non_module_base != non_module_head:
                issues.append(
                    "pyproject.toml: independence contract fields other than "
                    "'modules' were changed -- only its module list may grow"
                )
            if not base_modules <= head_modules:
                issues.append(
                    "pyproject.toml: independence contract's module list lost "
                    "an existing entry -- it may only grow, never shrink"
                )
            continue
        name = contract.get("name", "<unnamed>")
        issues.append(
            f"pyproject.toml: existing contract '{name}' was modified or removed "
            f"-- the Builder may only append new contracts, never edit existing ones"
        )
    return issues


def domain_exists_at(ref: str, domain: str) -> bool:
    result = subprocess.run(
        ["git", "cat-file", "-e", f"{ref}:src/todoapp/{domain}/service.py"],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def read_spec_at(ref: str, domain: str) -> str | None:
    """Reads a domain's spec as it stood at `ref`, not the working tree --
    the Builder is now allowed to strip the readiness marker it just
    fulfilled as part of its own PR, so authorization must be judged
    against the pre-Builder state, never the post-edit one."""
    result = subprocess.run(
        ["git", "show", f"{ref}:docs/product-specs/{domain}.md"],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout.decode("utf-8")


def check_target_authorized(base: str, domain: str) -> list[str]:
    """The touched domain's spec must actually carry the readiness marker --
    binds the discovery gate (builder-prompt.md's Status/[ready] convention)
    to the diff mechanically, instead of trusting the Builder's own claim
    that it picked an authorized target."""
    text = read_spec_at(base, domain)
    if text is None:
        return [
            f"{domain}: no product spec found at {base}:docs/product-specs/{domain}.md "
            f"-- not an authorized target"
        ]

    is_new = not domain_exists_at(base, domain)

    if is_new:
        if not STATUS_READY_PATTERN.search(text):
            return [
                f"{domain}: new domain has no 'Status: Ready for implementation' "
                f"line in its spec -- not an authorized build target"
            ]
        return []

    if not READY_BULLET_PATTERN.search(text):
        return [
            f"{domain}: existing domain's spec has no '[ready]'-tagged bullet -- "
            f"not an authorized build target for this run"
        ]
    return []


def frontend_touched_domains(files: list[str]) -> set[str]:
    """Domain names (lowercased) implied by touched frontend component/test
    files, e.g. frontend/src/components/Labels.jsx -> {'labels'}."""
    domains = set()
    for f in files:
        if not f.startswith(FRONTEND_COMPONENTS_DIR):
            continue
        name = f[len(FRONTEND_COMPONENTS_DIR) :]
        for suffix in (".test.jsx", ".jsx"):
            if name.endswith(suffix):
                domains.add(name[: -len(suffix)].lower())
                break
    return domains


def check_frontend_scope(files: list[str], domain: str | None, is_new: bool) -> list[str]:
    """New-domain builds must add a complete frontend set (component, test,
    api.js export); existing-domain builds must never touch frontend/ at all
    -- see builder-prompt.md TARGET STATE for the v1 split."""
    fe_domains = frontend_touched_domains(files)
    api_touched = FRONTEND_API_PATH in files

    if domain is None:
        if fe_domains or api_touched:
            return ["frontend/ touched with no single identifiable backend target domain"]
        return []

    if not is_new:
        if fe_domains or api_touched:
            return [
                f"{domain}: frontend/ touched on an existing-domain run -- frontend "
                f"wiring is out of scope for [ready]-bullet builds"
            ]
        return []

    issues = []
    if len(fe_domains) > 1:
        issues.append(
            f"more than one frontend domain touched: {sorted(fe_domains)} -- "
            f"the Builder may only work on one domain per run"
        )
    elif fe_domains and next(iter(fe_domains)) != domain:
        issues.append(
            f"frontend component touched for '{next(iter(fe_domains))}' doesn't "
            f"match the backend target domain '{domain}'"
        )

    component_name = domain.capitalize()
    component_path = f"{FRONTEND_COMPONENTS_DIR}{component_name}.jsx"
    test_path = f"{FRONTEND_COMPONENTS_DIR}{component_name}.test.jsx"
    if component_path not in files:
        issues.append(f"{domain}: new-domain build missing frontend component {component_path}")
    if test_path not in files:
        issues.append(f"{domain}: new-domain build missing frontend test {test_path}")

    api_file = REPO_ROOT / "frontend" / "src" / "api.js"
    if not api_touched:
        issues.append(f"{domain}: new-domain build didn't touch {FRONTEND_API_PATH}")
    elif f"export const {domain}Api" not in api_file.read_text(encoding="utf-8"):
        issues.append(f"{domain}: missing 'export const {domain}Api' in {FRONTEND_API_PATH}")

    return issues


def count_test_functions(source: str) -> set[str]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return set()
    return {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
    }


def count_ready_requirements(spec_text: str, is_new: bool) -> int:
    if is_new:
        match = BEHAVIOR_SECTION_PATTERN.search(spec_text)
        if not match:
            return 0
        return len(BEHAVIOR_BULLET_PATTERN.findall(match.group(1)))
    return len(READY_BULLET_PATTERN.findall(spec_text))


def check_traceability(base: str, domain: str) -> list[str]:
    """A lower bound only: the target's new test functions (by name, diffed
    against base) must be at least as numerous as its ready-marked spec
    requirements. Doesn't prove semantic coverage -- kills the specific
    failure of a PR's requirement-to-test table overclaiming what's tested."""
    spec_text = read_spec_at(base, domain)
    test_path = REPO_ROOT / "tests" / domain / "test_service.py"
    if spec_text is None or not test_path.exists():
        return []  # other checks already cover a missing spec/domain

    is_new = not domain_exists_at(base, domain)
    requirement_count = count_ready_requirements(spec_text, is_new)
    if requirement_count == 0:
        return []

    head_tests = count_test_functions(test_path.read_text(encoding="utf-8"))
    if is_new:
        base_tests: set[str] = set()
    else:
        result = subprocess.run(
            ["git", "show", f"{base}:tests/{domain}/test_service.py"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        base_tests = count_test_functions(result.stdout) if result.returncode == 0 else set()

    new_tests = head_tests - base_tests
    if len(new_tests) < requirement_count:
        return [
            f"{domain}: {requirement_count} ready-marked requirement(s) but only "
            f"{len(new_tests)} new test function(s) in tests/{domain}/test_service.py "
            f"-- traceability table can't be backed by this diff"
        ]
    return []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="origin/master", help="base ref to diff against")
    args = parser.parse_args()

    files = changed_files(args.base)
    issues: list[str] = []
    issues.extend(check_forbidden_paths(files))
    issues.extend(check_domain_count(files))
    if "pyproject.toml" in files:
        issues.extend(check_contracts_only_appended(args.base))

    domain = target_domain(files)
    is_new = domain is not None and not domain_exists_at(args.base, domain)
    if domain is not None:
        issues.extend(check_target_authorized(args.base, domain))
        issues.extend(check_traceability(args.base, domain))
    issues.extend(check_frontend_scope(files, domain, is_new))

    if not issues:
        print("check_builder_scope: no violations found.")
        return 0

    print(f"check_builder_scope: {len(issues)} violation(s):\n")
    for issue in issues:
        print(f"  {issue}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
