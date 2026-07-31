"""Shared, early Gemini configuration and user-safe error messages."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import dotenv_values, load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = PROJECT_ROOT / ".env"
_key_already_in_environment = bool(os.getenv("GOOGLE_API_KEY", "").strip())
_dotenv_key = str(dotenv_values(ENV_PATH).get("GOOGLE_API_KEY") or "").strip()

# This module is deliberately imported before any Gemini client is constructed.
if ENV_PATH.is_file():
    load_dotenv(dotenv_path=ENV_PATH, override=False)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "").strip()
GOOGLE_API_KEY_SOURCE = "environment"
if GOOGLE_API_KEY and not _key_already_in_environment and _dotenv_key:
    GOOGLE_API_KEY_SOURCE = ".env"

if not GOOGLE_API_KEY:
    try:
        import streamlit as st
        GOOGLE_API_KEY = str(st.secrets.get("GOOGLE_API_KEY", "")).strip()
    except (FileNotFoundError, KeyError):
        GOOGLE_API_KEY = ""
    else:
        if GOOGLE_API_KEY:
            GOOGLE_API_KEY_SOURCE = "Streamlit Secrets"


def get_key_preview() -> str:
    return f"{GOOGLE_API_KEY[:8]}..." if GOOGLE_API_KEY else "not available"


def emit_startup_diagnostic(model: str) -> None:
    """Print the requested non-secret Gemini startup state."""
    print(
        "Gemini startup diagnostic | "
        f"Current model: {model} | GOOGLE_API_KEY exists: {bool(GOOGLE_API_KEY)} | "
        f"Key prefix: {get_key_preview()} | "
        f"Key source: {GOOGLE_API_KEY_SOURCE if GOOGLE_API_KEY else 'not found'}"
    )


def is_gemini_error(error: Exception) -> bool:
    """Return whether an exception originated from Gemini configuration or API use."""
    details = str(error).lower()
    return not GOOGLE_API_KEY or any(
        marker in details
        for marker in (
            "resource_exhausted", "quota", "model_not_found", "gemini", "google.api", "api key",
            "permission_denied", "invalid_argument", "401", "403", "404", "429",
        )
    )


def gemini_error_message(error: Exception) -> str:
    """Convert Gemini SDK errors into friendly Streamlit messages."""
    details = str(error).lower()
    if not GOOGLE_API_KEY:
        return "Gemini is not configured: add GOOGLE_API_KEY to .env or Streamlit Secrets, then restart the app."
    if "resource_exhausted" in details or "429" in details or "quota" in details:
        return ("Gemini quota is exhausted for this key's Google project. The free-tier request or "
                "input-token allowance has been used; wait for its reset, use a project with quota, or enable billing.")
    if "model_not_found" in details or "404" in details or "not found" in details:
        return "The selected Gemini model is unavailable to this API key. Choose a model returned by the diagnostic."
    if ("api key not valid" in details or "invalid api key" in details or "invalid_argument" in details
            or "permission_denied" in details or "401" in details or "403" in details):
        return "Gemini rejected the API key. Verify the key, Google project, and that the Gemini API is enabled."
    return f"Gemini could not complete the request: {error}"
