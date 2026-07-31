"""Environment configuration and Gemini embedding initialization."""

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from rag.gemini_config import GOOGLE_API_KEY, GOOGLE_API_KEY_SOURCE, PROJECT_ROOT

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
