"""Chunk and index uploaded PDFs using the application's existing vector store."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


TEXT_SPLITTER = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)


@dataclass(frozen=True)
class IndexingResult:
    """Summary of one completed PDF indexing operation."""

    pages_processed: int
    chunks_created: int
    embedding_time: float


def index_documents(documents: list[Document]) -> IndexingResult:
    """Chunk documents and add them to the existing Chroma collection."""
    chunks = TEXT_SPLITTER.split_documents(documents)
    if not chunks:
        raise ValueError("No text chunks could be created from this PDF.")

    from rag.retriever import vector_store

    started_at = perf_counter()
    vector_store.add_documents(chunks)

    refresh_retriever(vector_store)
    return IndexingResult(
        pages_processed=len(documents),
        chunks_created=len(chunks),
        embedding_time=perf_counter() - started_at,
    )


def refresh_retriever(vector_store) -> None:
    """Synchronize the live Chroma collection used by the existing retriever.

    The application's retriever queries this same ``vector_store`` object, so
    newly added chunks are available to the unchanged RetrievalQA chain at once.
    """
    vector_store._collection.count()
