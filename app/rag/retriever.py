"""Load the persisted Chroma collection and configure retrieval."""

from langchain_chroma import Chroma

from rag.embeddings import PROJECT_ROOT, embeddings


VECTOR_DB_PATH = PROJECT_ROOT / "vector_db"
COLLECTION_NAME = "research_papers"

vector_store = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=str(VECTOR_DB_PATH),
)

if vector_store._collection.count() == 0:
    raise RuntimeError(
        "The vector database contains no chunks. Complete Section 7 before creating a retriever."
    )

retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5},
)
