"""Standalone Gemini connectivity and quota diagnostic for this project."""

from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "app"))

from google import genai
from rag.gemini_config import GOOGLE_API_KEY, GOOGLE_API_KEY_SOURCE, emit_startup_diagnostic


def identify_problem(error: Exception) -> str:
    text = str(error).lower()
    if "resource_exhausted" in text or "429" in text or "quota" in text:
        return "NO QUOTA: this key's project exhausted its request and/or input-token allowance."
    if "model_not_found" in text or "404" in text or "not found" in text:
        return "MODEL UNAVAILABLE: the model is not enabled or available for this key/project."
    if "api key not valid" in text or "invalid api key" in text or "401" in text:
        return "INVALID KEY: verify GOOGLE_API_KEY. Gemini API keys normally do not expire; create a replacement if needed."
    if "permission_denied" in text or "403" in text or "service_disabled" in text:
        return "DISABLED API / WRONG PROJECT / BILLING: enable Gemini API and check project ownership and billing."
    return f"UNCLASSIFIED GEMINI ERROR: {error}"


def main() -> int:
    emit_startup_diagnostic("auto-selected generateContent model")
    if not GOOGLE_API_KEY:
        print("MISSING API KEY: add GOOGLE_API_KEY to .env or Streamlit Secrets.")
        return 1

    print(f"Key source: {GOOGLE_API_KEY_SOURCE}")
    try:
        client = genai.Client(api_key=GOOGLE_API_KEY)
        models = list(client.models.list())
        available = [
            model.name.removeprefix("models/")
            for model in models
            if "generateContent" in (getattr(model, "supported_actions", None) or [])
        ]
        print("Available generateContent models:")
        for model in available:
            print(f"  - {model}")
        if not available:
            print("MODEL UNAVAILABLE: no listed model supports generateContent for this key.")
            return 1

        requested = os.getenv("GEMINI_CHAT_MODEL", "gemini-2.0-flash")
        model_name = requested if requested in available else available[0]
        print(f"Calling generateContent with model: {model_name}")
        response = client.models.generate_content(model=model_name, contents="Hello")
        print("generateContent successful. Full response:")
        print(response)
        return 0
    except Exception as error:
        print(identify_problem(error))
        print("Full error:")
        print(repr(error))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
