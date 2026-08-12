"""Scan docs/ for stale references and out-of-date Verified: markers.

Report-only by default. With --fix, also auto-fixes one narrow, mechanical
case: a markdown link [text](path) where path no longer exists gets
unlinked to plain text `text`. Nothing else is ever auto-edited -- content
staleness (Verified: date vs. source mtime) is always report-only, since
deciding a doc is still accurate requires a human to actually read it.

Always writes docs/quality-score/report.md with the full findings.

Usage:
  python scripts/doc_gardener.py          # report only
  python scripts/doc_gardener.py --fix    # also unlink broken markdown links
"""

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs"
REPORT_PATH = DOCS_DIR / "quality-score" / "report.md"

PATH_PATTERN = re.compile(r"(?:`|\[.*?\]\()((?:src|tests|scripts|docs)/[\w./-]+)")
MD_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(((?:src|tests|scripts|docs)/[\w./-]+)\)")
VERIFIED_PATTERN = re.compile(r"Verified:\s*(\d{4}-\d{2}-\d{2})")


@dataclass
class Flag:
    doc: Path
    reason: str


def iter_docs():
    for doc in sorted(DOCS_DIR.rglob("*.md")):
        if doc == REPORT_PATH:
            continue
        yield doc


def find_referenced_paths(text: str) -> list[str]:
    return PATH_PATTERN.findall(text)


def find_verified_date(text: str) -> date | None:
    match = VERIFIED_PATTERN.search(text)
    if not match:
        return None
    return datetime.strptime(match.group(1), "%Y-%m-%d").date()


def autofix_broken_links(doc: Path) -> int:
    """Unlink markdown links pointing at paths that no longer exist. Returns fix count."""
    text = doc.read_text(encoding="utf-8")
    fixed = 0

    def repl(match: re.Match) -> str:
        nonlocal fixed
        link_text, path = match.group(1), match.group(2)
        if not (REPO_ROOT / path).exists():
            fixed += 1
            return link_text
        return match.group(0)

    new_text = MD_LINK_PATTERN.sub(repl, text)
    if fixed:
        doc.write_text(new_text, encoding="utf-8")
    return fixed


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


def write_report(fixed_total: int, flags: list[Flag]) -> None:
    lines = [
        "# Doc Gardener Report",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
    ]
    if fixed_total:
        lines.append(f"Auto-fixed {fixed_total} broken markdown link(s).")
        lines.append("")
    if not flags:
        lines.append("No remaining staleness found.")
    else:
        lines.append(f"{len(flags)} remaining issue(s) -- needs human review:")
        lines.append("")
        for flag in flags:
            rel = flag.doc.relative_to(REPO_ROOT)
            lines.append(f"- `{rel}`: {flag.reason}")
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fix", action="store_true", help="auto-fix broken markdown links")
    args = parser.parse_args()

    fixed_total = 0
    if args.fix:
        for doc in iter_docs():
            fixed_total += autofix_broken_links(doc)

    all_flags: list[Flag] = []
    for doc in iter_docs():
        all_flags.extend(check_doc(doc))

    write_report(fixed_total, all_flags)

    if fixed_total:
        print(f"doc_gardener: auto-fixed {fixed_total} broken link(s).")

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
