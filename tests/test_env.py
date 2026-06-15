"""Tests for environment validation."""

from unittest.mock import patch

import pytest

from acquisition_helper.env import (
    _validate_google_genai_provider,
    get_llm_model_lite,
    get_llm_model_pro,
    validate_environment,
)


@patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}, clear=False)
@patch("acquisition_helper.env.importlib.util.find_spec", return_value=None)
def test_validate_environment_raises_without_google_genai(mock_find_spec):
    with pytest.raises(EnvironmentError, match="Google Gen AI SDK is not installed"):
        validate_environment()
    mock_find_spec.assert_called_with("google.genai")


@patch("acquisition_helper.env.load_dotenv")
@patch.dict("os.environ", {}, clear=True)
def test_validate_environment_raises_without_gemini_key(mock_load_dotenv):
    with pytest.raises(EnvironmentError, match="GEMINI_API_KEY is not set"):
        validate_environment()
    mock_load_dotenv.assert_called_once()


@patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}, clear=False)
@patch("acquisition_helper.env.importlib.util.find_spec", return_value=object())
def test_validate_environment_passes_with_google_genai(mock_find_spec):
    validate_environment()
    mock_find_spec.assert_called_with("google.genai")


def test_validate_google_genai_provider_raises_when_missing():
    with patch("acquisition_helper.env.importlib.util.find_spec", return_value=None):
        with pytest.raises(EnvironmentError, match="crewai\\[google-genai\\]"):
            _validate_google_genai_provider()


def test_default_llm_models():
    with patch.dict("os.environ", {}, clear=True):
        assert get_llm_model_lite() == "gemini/gemini-2.5-flash-lite"
        assert get_llm_model_pro() == "gemini/gemini-3-flash-preview"
