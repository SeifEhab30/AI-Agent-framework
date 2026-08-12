"""Golden-principle checks not covered by ruff.

Rule 1: functions in service.py/ui.py must not take bare dict/Any params --
validate at boundaries with typed models instead.
Rule 2: no local helper redefines a name already provided by platform/.
Rule 3: no bare `except:` -- it swallows everything including
KeyboardInterrupt/SystemExit, hiding real bugs.
Rule 4: no print() in domain code (src/todoapp/**, excluding scripts/) --
use the providers logger instead of ad hoc prints.

Usage: python scripts/check_golden_rules.py
"""

import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src" / "todoapp"
PLATFORM_DIR = SRC_DIR / "platform"
BOUNDARY_FILENAMES = {"service.py", "ui.py"}
DISALLOWED_ANNOTATIONS = {"dict", "Dict", "Any"}


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

    if not issues:
        print("check_golden_rules: no violations found.")
        return 0

    print(f"check_golden_rules: {len(issues)} violation(s):\n")
    for issue in issues:
        print(f"  {issue}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
