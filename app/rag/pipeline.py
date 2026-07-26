"""Gemini retrieval-augmented generation chain."""

from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from rag.embeddings import GOOGLE_API_KEY
from rag.retriever import retriever


if not GOOGLE_API_KEY:
    raise EnvironmentError("GOOGLE_API_KEY is required to create the Gemini chat model.")

try:
    chat_model = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash",
        google_api_key=GOOGLE_API_KEY,
        temperature=0,
    )
except Exception as error:
    raise RuntimeError(
        "Gemini chat model initialization failed. Verify GOOGLE_API_KEY and model access."
    ) from error

if chat_model is None:
    raise RuntimeError("Gemini chat model initialization returned no model.")

try:
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
    retrieval_qa_chain = create_retrieval_chain(retriever, document_chain)
except Exception as error:
    raise RuntimeError(
        "Could not create the Gemini RetrievalQA chain. Verify the API key, model access, and Sections 8 dependencies."
    ) from error
