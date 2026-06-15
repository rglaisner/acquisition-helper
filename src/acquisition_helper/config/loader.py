"""Config loading helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from acquisition_helper.env import CONFIG_DIR


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return data if isinstance(data, dict) else {}


def load_agents_config() -> dict[str, Any]:
    return load_yaml(CONFIG_DIR / "agents" / "agents_all.yaml")


def load_tasks_config() -> dict[str, Any]:
    return load_yaml(CONFIG_DIR / "tasks" / "tasks_all.yaml")


def load_defaults() -> dict[str, Any]:
    return load_yaml(CONFIG_DIR / "defaults.yaml")


def format_template(text: str, variables: dict[str, Any]) -> str:
    result = text
    for key, value in variables.items():
        result = result.replace("{" + key + "}", str(value))
    return result
