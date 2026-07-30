"""Environment configuration and Gemini embedding initialization."""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = PROJECT_ROOT / ".env"

if ENV_PATH.is_file():
    load_dotenv(dotenv_path=ENV_PATH, override=False)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "").strip()
GOOGLE_API_KEY_SOURCE = ".env or environment"

if not GOOGLE_API_KEY:
    import streamlit as st

    try:
        GOOGLE_API_KEY = str(st.secrets.get("GOOGLE_API_KEY", "")).strip()
    except FileNotFoundError:
        GOOGLE_API_KEY = ""
    else:
        GOOGLE_API_KEY_SOURCE = "Streamlit Secrets"

if not GOOGLE_API_KEY:
    raise EnvironmentError(
        "GOOGLE_API_KEY is missing. "
        "Set it in your local .env file or in Streamlit Secrets."
    )

EMBEDDING_MODEL = "gemini-embedding-2"

embeddings = GoogleGenerativeAIEmbeddings(
    model=EMBEDDING_MODEL,
    google_api_key=GOOGLE_API_KEY,
)
