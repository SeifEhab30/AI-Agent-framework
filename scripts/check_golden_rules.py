"""Golden-principle checks not covered by ruff.

Rule 1: functions in service.py/ui.py must not take bare dict/Any params --
validate at boundaries with typed models instead.
Rule 2: no local helper redefines a name already provided by platform/.
Rule 3: no bare `except:` -- it swallows everything including
KeyboardInterrupt/SystemExit, hiding real bugs.
Rule 4: no print() in domain code (src/todoapp/**, excluding scripts/) --
use the providers logger instead of ad hoc prints.
Rule 5: every domain folder must be fully declared -- all six layer files
present, layering + forbidden-providers + independence contracts in
pyproject.toml, and a row in MAP.md's domain table. Stops a new domain
from silently escaping the architecture rules the others are held to.
Rule 6: in service.py, a string variable assigned from a `.strip()` call
must be blank-checked (`if not <name>: raise ...`) somewhere in the same
function. Stripping only makes sense if the result is then validated --
a stripped-but-unchecked field is exactly how a required-field check goes
missing without any test or lint catching it.

Usage: python scripts/check_golden_rules.py
"""

import ast
import re
import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src" / "todoapp"
PLATFORM_DIR = SRC_DIR / "platform"
PYPROJECT = REPO_ROOT / "pyproject.toml"
MAP_FILE = REPO_ROOT / "MAP.md"
BOUNDARY_FILENAMES = {"service.py", "ui.py"}
DISALLOWED_ANNOTATIONS = {"dict", "Dict", "Any"}
LAYER_FILENAMES = {
    "types.py",
    "config.py",
    "repo.py",
    "service.py",
    "runtime.py",
    "ui.py",
}
NON_DOMAIN_DIRS = {"providers", "platform", "__pycache__"}


def platform_function_names() -> set[str]:
    names = set()
    for path in PLATFORM_DIR.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                names.add(node.name)
    return names


def annotation_name(annotation: ast.expr | None) -> str | None:
    if annotation is None:
        return None
    if isinstance(annotation, ast.Name):
        return annotation.id
    if isinstance(annotation, ast.Attribute):
        return annotation.attr
    return None


def check_boundary_file(path: Path) -> list[str]:
    issues = []
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for arg in node.args.args:
                if arg.arg == "self":
                    continue
                name = annotation_name(arg.annotation)
                if name in DISALLOWED_ANNOTATIONS:
                    issues.append(
                        f"{path.relative_to(REPO_ROOT)}:{node.lineno}: "
                        f"'{node.name}' param '{arg.arg}' is untyped ({name}) -- "
                        f"use a typed model at this boundary"
                    )
    return issues


def check_duplicate_helpers(path: Path, reserved: set[str]) -> list[str]:
    issues = []
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in reserved:
            issues.append(
                f"{path.relative_to(REPO_ROOT)}:{node.lineno}: "
                f"local function '{node.name}' duplicates a name already "
                f"in platform/ -- reuse it instead"
            )
    return issues


def check_bare_except(path: Path) -> list[str]:
    issues = []
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            issues.append(
                f"{path.relative_to(REPO_ROOT)}:{node.lineno}: "
                f"bare 'except:' catches everything including "
                f"KeyboardInterrupt/SystemExit -- catch a specific exception"
            )
    return issues


def check_no_print(path: Path) -> list[str]:
    issues = []
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "print"
        ):
            issues.append(
                f"{path.relative_to(REPO_ROOT)}:{node.lineno}: "
                f"print() in domain code -- use the providers logger instead"
            )
    return issues


def check_unvalidated_stripped_fields(path: Path) -> list[str]:
    """Rule 6: a `.strip()`'d local must be blank-checked in the same function."""
    issues = []
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        stripped_vars: dict[str, int] = {}
        checked_vars: set[str] = set()
        for stmt in node.body:
            if (
                isinstance(stmt, ast.Assign)
                and len(stmt.targets) == 1
                and isinstance(stmt.targets[0], ast.Name)
                and isinstance(stmt.value, ast.Call)
                and isinstance(stmt.value.func, ast.Attribute)
                and stmt.value.func.attr == "strip"
            ):
                stripped_vars[stmt.targets[0].id] = stmt.lineno
            elif isinstance(stmt, ast.If):
                test = stmt.test
                name = None
                if (
                    isinstance(test, ast.UnaryOp)
                    and isinstance(test.op, ast.Not)
                    and isinstance(test.operand, ast.Name)
                ):
                    name = test.operand.id
                if name and any(isinstance(s, ast.Raise) for s in stmt.body):
                    checked_vars.add(name)
        for name, lineno in stripped_vars.items():
            if name not in checked_vars:
                issues.append(
                    f"{path.relative_to(REPO_ROOT)}:{lineno}: "
                    f"'{name}' is stripped but never blank-checked -- add "
                    f"'if not {name}: raise ValidationError(...)' or drop the strip()"
                )
    return issues


def discover_domains() -> tuple[list[str], list[str]]:
    """Find domain folders. Returns (complete domains, issues for partial ones)."""
    domains, issues = [], []
    for path in sorted(SRC_DIR.iterdir()):
        if not path.is_dir() or path.name in NON_DOMAIN_DIRS:
            continue
        present = {p.name for p in path.glob("*.py")} & LAYER_FILENAMES
        if not present:
            continue
        missing = LAYER_FILENAMES - present
        if missing:
            issues.append(
                f"src/todoapp/{path.name}/: incomplete domain -- missing "
                f"{', '.join(sorted(missing))}. One domain = one folder with "
                f"all six layer files."
            )
            continue
        domains.append(path.name)
    return domains, issues


def declared_contracts() -> tuple[set[str], set[str], set[str]]:
    """Domains covered by each contract type in pyproject.toml."""
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    contracts = data.get("tool", {}).get("importlinter", {}).get("contracts", [])
    layered: set[str] = set()
    guarded: set[str] = set()
    independent: set[str] = set()

    def domain_of(module: str) -> str | None:
        parts = module.split(".")
        return parts[1] if len(parts) > 1 and parts[0] == "todoapp" else None

    for contract in contracts:
        kind = contract.get("type")
        if kind == "layers":
            found = {domain_of(m) for m in contract.get("layers", [])}
            layered |= {d for d in found if d}
        elif kind == "forbidden":
            if "todoapp.providers" in contract.get("forbidden_modules", []):
                found = {domain_of(m) for m in contract.get("source_modules", [])}
                guarded |= {d for d in found if d}
        elif kind == "independence":
            found = {domain_of(m) for m in contract.get("modules", [])}
            independent |= {d for d in found if d}

    return layered, guarded, independent


def mapped_domains() -> set[str]:
    """Domain names listed in MAP.md's 'Current domains' table."""
    text = MAP_FILE.read_text(encoding="utf-8")
    section = text.split("## Current domains", 1)
    if len(section) < 2:
        return set()
    rows = re.findall(r"^\|\s*([A-Za-z0-9_-]+)\s*\|", section[1], re.MULTILINE)
    return {row for row in rows if row not in {"Domain", "-"}}


def check_domain_registration() -> list[str]:
    domains, issues = discover_domains()
    layered, guarded, independent = declared_contracts()
    mapped = mapped_domains()

    for domain in domains:
        if domain not in layered:
            issues.append(
                f"domain '{domain}' has no layering contract in pyproject.toml -- "
                f"add a 'layers' contract for todoapp.{domain}"
            )
        if domain not in guarded:
            issues.append(
                f"domain '{domain}' has no forbidden-providers contract in "
                f"pyproject.toml -- only runtime.py may reach providers/"
            )
        if domain not in independent:
            issues.append(
                f"domain '{domain}' is missing from the independence contract in "
                f"pyproject.toml -- domains must not import each other"
            )
        if domain not in mapped:
            issues.append(
                f"domain '{domain}' is not listed in MAP.md's domain table -- "
                f"agents find domains through MAP.md, so it must be indexed there"
            )
    return issues


def main() -> int:
    issues: list[str] = []
    reserved = platform_function_names()

    for path in SRC_DIR.rglob("*.py"):
        if path.parent == PLATFORM_DIR:
            continue
        if path.name in BOUNDARY_FILENAMES:
            issues.extend(check_boundary_file(path))
        issues.extend(check_duplicate_helpers(path, reserved))
        issues.extend(check_bare_except(path))
        issues.extend(check_no_print(path))
        if path.name == "service.py":
            issues.extend(check_unvalidated_stripped_fields(path))

    issues.extend(check_domain_registration())

    if not issues:
        print("check_golden_rules: no violations found.")
        return 0

    print(f"check_golden_rules: {len(issues)} violation(s):\n")
    for issue in issues:
        print(f"  {issue}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
