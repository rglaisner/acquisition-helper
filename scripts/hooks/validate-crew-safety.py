#!/usr/bin/env python3
"""Post-edit safety validator for Acquisition Helper Python sources."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"

API_KEY_PATTERNS = [
    re.compile(r'(?i)(api[_-]?key|secret|password)\s*=\s*["\'][^"\']{8,}["\']'),
    re.compile(r'(?i)sk-[a-zA-Z0-9]{20,}'),
    re.compile(r'(?i)AIza[a-zA-Z0-9_-]{20,}'),
]

EMPTY_EXCEPT = re.compile(r"except\s*:\s*pass")


def scan_file(path: Path) -> list[str]:
    issues: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        return [f"{path}: cannot read ({error})"]

    for pattern in API_KEY_PATTERNS:
        if pattern.search(text):
            issues.append(f"{path}: possible hardcoded secret")

    if EMPTY_EXCEPT.search(text):
        issues.append(f"{path}: empty except block")

    return issues


def main() -> int:
    targets = [Path(p) for p in sys.argv[1:]] if len(sys.argv) > 1 else []
    if not targets and SRC.exists():
        targets = list(SRC.rglob("*.py"))

    all_issues: list[str] = []
    for target in targets:
        if target.is_dir():
            all_issues.extend(issue for f in target.rglob("*.py") for issue in scan_file(f))
        elif target.suffix == ".py" and target.exists():
            all_issues.extend(scan_file(target))

    if all_issues:
        print("Crew safety validation failed:", file=sys.stderr)
        for issue in all_issues:
            print(f"  - {issue}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
