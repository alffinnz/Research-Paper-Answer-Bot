"""Public question-answering interface for the research-paper bot."""

import time

from rag.pipeline import retrieval_qa_chain


def ask_question(question: str) -> dict:
    """Answer a non-empty research question with supporting source documents."""
    if not isinstance(question, str) or not question.strip():
        raise ValueError("Enter a non-empty research question.")

    started_at = time.perf_counter()
    try:
        result = retrieval_qa_chain.invoke({"input": question.strip()})
    except Exception as error:
        raise RuntimeError(
            "The question could not be answered. Check Gemini API access and try again."
        ) from error

    response_time = time.perf_counter() - started_at
    source_documents = result.get("context", [])
    answer = result.get("answer", "No answer was returned.")

    return {
        "answer": answer,
        "source_documents": source_documents,
        "response_time": response_time,
    }
