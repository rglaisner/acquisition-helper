"""Environment and path utilities."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PACKAGE_ROOT / "config"
OUTPUT_DIR = PROJECT_ROOT / "output"
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"

REPORT_FILENAME = "SME_Platform_Acquisition_Report.md"


def ensure_output_dir() -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


def load_dotenv() -> None:
    env_path = PROJECT_ROOT / ".env"
    try:
        from dotenv import load_dotenv as _load

        _load(env_path)
    except ImportError:
        pass


def _validate_google_genai_provider() -> None:
    if importlib.util.find_spec("google.genai") is None:
        raise EnvironmentError(
            "Google Gen AI SDK is not installed. CrewAI Gemini models require "
            'crewai[google-genai]. Reinstall dependencies: uv sync or pip install -e ".'
        )


def validate_environment(*, require_serper: bool = False) -> None:
    load_dotenv()
    if not os.environ.get("GEMINI_API_KEY"):
        raise EnvironmentError(
            "GEMINI_API_KEY is not set. Export it or add it to .env in the project root."
        )
    _validate_google_genai_provider()
    if require_serper and not os.environ.get("SERPER_API_KEY"):
        raise EnvironmentError(
            "SERPER_API_KEY is not set but web search tools are required for this tier."
        )


def get_llm_model_lite() -> str:
    return os.environ.get("LLM_MODEL_LITE", "gemini/gemini-2.5-flash-lite")


def get_llm_model_pro() -> str:
    return os.environ.get("LLM_MODEL_PRO", "gemini/gemini-3-flash-preview")
