"""Load the persisted Chroma collection and configure retrieval."""

from langchain_chroma import Chroma

from rag.embeddings import PROJECT_ROOT, embeddings


VECTOR_DB_PATH = PROJECT_ROOT / "vector_db"
COLLECTION_NAME = "research_papers"

class VectorDatabaseEmptyError(RuntimeError):
    """Raised when no indexed PDF chunks are available."""

    is_empty_vector_database = True


vector_store = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=str(VECTOR_DB_PATH),
)

def get_retriever():
    """Return the existing retriever after confirming indexed chunks exist."""
    if vector_store._collection.count() == 0:
        raise VectorDatabaseEmptyError(
            "No indexed PDF chunks are available. Upload and index a PDF first."
        )

    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5},
    )
