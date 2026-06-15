"""PII and secret scanning on pipeline I/O."""

from __future__ import annotations

import re

SECRET_PATTERNS = [
    re.compile(r"sk-[a-zA-Z0-9]{20,}"),
    re.compile(r"AIza[a-zA-Z0-9_-]{20,}"),
    re.compile(r"(?i)(api[_-]?key|secret|password)\s*[:=]\s*\S{8,}"),
]

PII_PATTERNS = [
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
]


def scan_text(text: str) -> list[str]:
    issues: list[str] = []
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            issues.append("possible secret detected")
    for pattern in PII_PATTERNS:
        if pattern.search(text):
            issues.append("possible PII detected")
    return issues


def is_safe(text: str) -> bool:
    return len(scan_text(text)) == 0
