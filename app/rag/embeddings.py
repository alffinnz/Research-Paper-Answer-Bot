"""Environment configuration and Gemini embedding initialization."""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = PROJECT_ROOT / ".env"

if not ENV_PATH.is_file():
    raise FileNotFoundError(f"Environment file not found: {ENV_PATH}")

load_dotenv(dotenv_path=ENV_PATH, override=False)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise EnvironmentError(
        "GOOGLE_API_KEY is missing. Add GOOGLE_API_KEY=your_key to the project .env file."
    )

try:
    embeddings = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-2",
        google_api_key=GOOGLE_API_KEY,
    )
except Exception as error:
    raise RuntimeError(
        "Gemini embedding initialization failed. Verify GOOGLE_API_KEY, model access, and network connectivity."
    ) from error
