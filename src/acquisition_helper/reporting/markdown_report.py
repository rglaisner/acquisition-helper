"""Markdown report assembly — migrated from Baseline.py."""

from __future__ import annotations

import re
import sys
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import TextIO

from crewai.crews.crew_output import CrewOutput

ANSI_ESCAPE_PATTERN = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def configure_console_encoding() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8")
            except (OSError, ValueError, AttributeError):
                pass


def strip_ansi(text: str) -> str:
    return ANSI_ESCAPE_PATTERN.sub("", text)


class TeeWriter:
    def __init__(self, stream: TextIO, buffer: list[str]) -> None:
        self._stream = stream
        self._buffer = buffer

    def write(self, text: str) -> int:
        if text:
            self._stream.write(text)
            self._buffer.append(text)
        return len(text) if text else 0

    def flush(self) -> None:
        self._stream.flush()

    def __getattr__(self, name: str):
        return getattr(self._stream, name)


@contextmanager
def capture_console(log_buffer: list[str]):
    stdout_tee = TeeWriter(sys.stdout, log_buffer)
    stderr_tee = TeeWriter(sys.stderr, log_buffer)
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    try:
        sys.stdout = stdout_tee
        sys.stderr = stderr_tee
        yield
    finally:
        sys.stdout = original_stdout
        sys.stderr = original_stderr


def get_final_report_text(crew_output: CrewOutput) -> str:
    if crew_output.raw:
        return crew_output.raw
    if crew_output.tasks_output:
        return crew_output.tasks_output[-1].raw
    return ""


def build_markdown_report(
    log_text: str,
    crew_output: CrewOutput | None,
    *,
    script_path: Path,
    tier: str | None = None,
    error_message: str | None = None,
) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    sections: list[str] = [
        "# SME Platform Acquisition Report",
        "",
        f"**Generated:** {timestamp}  ",
        f"**Entry:** {script_path}",
    ]
    if tier:
        sections.append(f"**Tier:** {tier}  ")
    sections.extend(["", "---", "", "## Execution Log", "", "```text", strip_ansi(log_text).strip() or "(no output captured)", "```", ""])

    if crew_output is not None:
        final_report = get_final_report_text(crew_output)
        sections.extend(["---", "", "## Final Report", "", final_report or "(no final report content)", ""])

        if crew_output.tasks_output:
            sections.extend(["---", "", "## Task Outputs", ""])
            for task_output in crew_output.tasks_output:
                task_name = task_output.name or "Unnamed Task"
                sections.extend([
                    f"### Task: {task_name}",
                    "",
                    f"**Description:** {task_output.description or 'N/A'}",
                    "",
                    "**Output:**",
                    "",
                    task_output.raw or "(empty)",
                    "",
                ])

        usage = crew_output.token_usage
        if usage.total_tokens > 0:
            sections.extend([
                "---", "", "## Token Usage", "",
                f"- **Total tokens:** {usage.total_tokens}",
                f"- **Prompt tokens:** {usage.prompt_tokens}",
                f"- **Completion tokens:** {usage.completion_tokens}",
                f"- **Successful requests:** {usage.successful_requests}",
                "",
            ])

    if error_message:
        sections.extend(["---", "", "## Error", "", "```text", error_message, "```", ""])

    return "\n".join(sections)


def write_report(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def save_report(
    report_path: Path,
    log_buffer: list[str],
    crew_output: CrewOutput | None,
    *,
    script_path: Path,
    tier: str | None = None,
    error_message: str | None = None,
) -> None:
    markdown = build_markdown_report(
        "".join(log_buffer),
        crew_output,
        script_path=script_path,
        tier=tier,
        error_message=error_message,
    )
    write_report(report_path, markdown)
