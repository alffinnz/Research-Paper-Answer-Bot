"""Environment configuration and Gemini embedding initialization."""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = PROJECT_ROOT / ".env"

if ENV_PATH.is_file():
    load_dotenv(dotenv_path=ENV_PATH, override=False)


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise EnvironmentError(
        "GOOGLE_API_KEY is missing. "
        "Set it in your local .env file or in Streamlit Secrets."
    )

try:
    embeddings = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-2",
        google_api_key=GOOGLE_API_KEY,
    )
except Exception as error:
    raise RuntimeError(
        "Gemini embedding initialization failed. "
        "Verify your GOOGLE_API_KEY and internet connection."
    ) from error