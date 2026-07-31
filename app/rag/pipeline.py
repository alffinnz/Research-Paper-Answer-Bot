"""Gemini retrieval-augmented generation chain."""

import os
from functools import lru_cache

from google import genai
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from rag.gemini_config import GOOGLE_API_KEY


if not GOOGLE_API_KEY:
    raise EnvironmentError("GOOGLE_API_KEY is required to create the Gemini chat model.")

REQUESTED_CHAT_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-3.5-flash")
FALLBACK_CHAT_MODELS = ("gemini-3.5-flash",)


@lru_cache(maxsize=1)
def get_supported_chat_model_name() -> str:
    """Use the requested model when available, otherwise choose a supported fallback."""
    client = genai.Client(api_key=GOOGLE_API_KEY)
    supported_models = {
        model.name.removeprefix("models/")
        for model in client.models.list()
        if "generateContent" in (getattr(model, "supported_actions", None) or [])
    }

    for model_name in (REQUESTED_CHAT_MODEL, *FALLBACK_CHAT_MODELS):
        if model_name in supported_models:
            return model_name

    raise RuntimeError("No Gemini model available to this API key supports generateContent.")


@lru_cache(maxsize=1)
def get_retrieval_qa_chain():
    """Build the existing RAG chain after API and vector-store validation."""
    from rag.retriever import get_retriever

    chat_model = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash",
        google_api_key=GOOGLE_API_KEY,
        temperature=0,
    )
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Answer only from the supplied research-paper context. "
                "If the context does not contain the answer, say so clearly.\n\n"
                "<context>\n{context}\n</context>",
            ),
            ("human", "{input}"),
        ]
    )
    document_chain = create_stuff_documents_chain(chat_model, qa_prompt)
    return create_retrieval_chain(get_retriever(), document_chain)
