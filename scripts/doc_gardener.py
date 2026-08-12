"""Scan docs/ for stale references and out-of-date Verified: markers.

Usage: python scripts/doc_gardener.py
"""

import re
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs"

PATH_PATTERN = re.compile(r"(?:`|\[.*?\]\()((?:src|tests|scripts|docs)/[\w./-]+)")
VERIFIED_PATTERN = re.compile(r"Verified:\s*(\d{4}-\d{2}-\d{2})")


@dataclass
class Flag:
    doc: Path
    reason: str


def find_referenced_paths(text: str) -> list[str]:
    return PATH_PATTERN.findall(text)


def find_verified_date(text: str) -> date | None:
    match = VERIFIED_PATTERN.search(text)
    if not match:
        return None
    return datetime.strptime(match.group(1), "%Y-%m-%d").date()


def check_doc(doc: Path) -> list[Flag]:
    flags: list[Flag] = []
    text = doc.read_text(encoding="utf-8")

    for ref in find_referenced_paths(text):
        if not (REPO_ROOT / ref).exists():
            flags.append(Flag(doc, f"stale reference: {ref} not found"))

    verified = find_verified_date(text)
    if verified is None:
        flags.append(Flag(doc, "missing Verified: date"))
        return flags

    newest_source = None
    for ref in find_referenced_paths(text):
        source = REPO_ROOT / ref
        if source.exists() and source.is_file():
            mtime = date.fromtimestamp(source.stat().st_mtime)
            if newest_source is None or mtime > newest_source:
                newest_source = mtime

    if newest_source and newest_source > verified:
        flags.append(
            Flag(
                doc,
                f"possibly stale: source changed ({newest_source}) after Verified: ({verified})",
            )
        )

    return flags


def main() -> int:
    all_flags: list[Flag] = []
    for doc in sorted(DOCS_DIR.rglob("*.md")):
        all_flags.extend(check_doc(doc))

    if not all_flags:
        print("doc_gardener: no staleness found.")
        return 0

    print(f"doc_gardener: {len(all_flags)} issue(s) found:\n")
    for flag in all_flags:
        rel = flag.doc.relative_to(REPO_ROOT)
        print(f"  {rel}: {flag.reason}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
