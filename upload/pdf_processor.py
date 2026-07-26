"""PDF text extraction for uploaded research papers."""

from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document


def load_pdf_documents(pdf_path: Path) -> list[Document]:
    """Extract non-empty, page-level LangChain documents from a PDF file."""
    try:
        documents = PyPDFLoader(str(pdf_path)).load()
    except Exception as error:
        raise RuntimeError("We could not extract text from this PDF.") from error

    text_documents = [document for document in documents if document.page_content.strip()]
    if not text_documents:
        raise ValueError("This PDF does not contain extractable text.")

    return text_documents
