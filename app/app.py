import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
APP_DIRECTORY = Path(__file__).resolve().parent

for import_path in (PROJECT_ROOT, APP_DIRECTORY):
    import_path_string = str(import_path)
    if import_path_string not in sys.path:
        sys.path.insert(0, import_path_string)

import streamlit as st

from rag.gemini_config import emit_startup_diagnostic, gemini_error_message, is_gemini_error
from auth.database import initialize_database
from auth.login import show_login_page
from auth.register import show_register_page
from auth.session import current_user, is_logged_in, logout_user
from rag.chatbot import ask_question
from upload.indexing import index_documents
from upload.pdf_processor import load_pdf_documents
from upload.uploader import render_upload_form


emit_startup_diagnostic(os.getenv("GEMINI_CHAT_MODEL", "gemini-3.5-flash"))

st.set_page_config(
    page_title="Research Paper AI",
    page_icon="📚",
    layout="wide",
)

initialize_database()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "auth_page" not in st.session_state:
    st.session_state.auth_page = "login"

st.markdown(
    """
    <style>
        .block-container {
            max-width: 1100px;
            padding-top: 3.5rem;
            padding-bottom: 4rem;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #07111f 0%, #0f172a 100%);
            border-right: 1px solid rgba(148, 163, 184, 0.18);
        }

        [data-testid="stSidebar"] > div:first-child {
            padding: 1.2rem 1rem 1.2rem;
            background: linear-gradient(135deg, rgba(124, 58, 237, 0.18), rgba(59, 130, 246, 0.14));
        }

        .sidebar-shell {
            padding: 0.2rem 0 0.75rem;
        }

        .sidebar-brand {
            display: flex;
            align-items: center;
            gap: 0.8rem;
            margin-bottom: 0.7rem;
        }

        .sidebar-icon {
            display: grid;
            place-items: center;
            width: 2.4rem;
            height: 2.4rem;
            border-radius: 0.9rem;
            background: linear-gradient(135deg, #8b5cf6, #3b82f6);
            box-shadow: 0 8px 20px rgba(59, 130, 246, 0.25);
            font-size: 1.1rem;
        }

        .sidebar-title {
            font-size: 1rem;
            font-weight: 700;
            color: #f8fafc;
            letter-spacing: -0.02em;
        }

        .sidebar-subtitle {
            font-size: 0.78rem;
            color: rgba(226, 232, 240, 0.72);
            margin-top: 0.15rem;
        }

        .sidebar-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.35rem 0.65rem;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.08);
            color: #dbeafe;
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.06em;
            text-transform: uppercase;
        }

        .sidebar-card {
            margin: 0.9rem 0 0.8rem;
            padding: 0.9rem 0.95rem;
            border: 1px solid rgba(148, 163, 184, 0.16);
            border-radius: 16px;
            background: rgba(15, 23, 42, 0.7);
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
        }

        .sidebar-card .section-label {
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.16em;
            text-transform: uppercase;
            color: #93c5fd;
            margin-bottom: 0.45rem;
        }

        .sidebar-card p,
        .sidebar-card li {
            color: rgba(241, 245, 249, 0.84);
            font-size: 0.93rem;
            line-height: 1.55;
        }

        .sidebar-card ul {
            padding-left: 1rem;
            margin: 0.4rem 0 0;
        }

        .sidebar-card .status-row {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin: 0.35rem 0;
            color: #e2e8f0;
            font-size: 0.92rem;
        }

        .sidebar-card .dot {
            width: 0.6rem;
            height: 0.6rem;
            border-radius: 999px;
            background: linear-gradient(135deg, #34d399, #22c55e);
            box-shadow: 0 0 0 3px rgba(34, 197, 84, 0.15);
        }

        .sidebar-card .tip {
            margin-top: 0.5rem;
            padding: 0.7rem;
            border-radius: 12px;
            background: rgba(59, 130, 246, 0.12);
            border: 1px solid rgba(96, 165, 250, 0.2);
            color: #bfdbfe;
        }

        .hero {
            max-width: 780px;
            margin: 0 auto 3.25rem;
            padding: 2.75rem 2rem 2.25rem;
            text-align: center;
            border: 1px solid rgba(250, 250, 250, 0.10);
            border-radius: 24px;
            background: linear-gradient(
                145deg,
                rgba(255, 255, 255, 0.055),
                rgba(255, 255, 255, 0.018)
            );
        }

        .hero-kicker {
            margin-bottom: 0.8rem;
            color: #a7b4ff;
            font-size: 0.82rem;
            font-weight: 600;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }

        .hero h1 {
            margin: 0;
            font-size: clamp(2.5rem, 7vw, 4.5rem);
            font-weight: 650;
            letter-spacing: -0.065em;
            line-height: 1.04;
        }

        .hero-tagline {
            margin: 1rem 0 0;
            color: rgba(250, 250, 250, 0.92);
            font-size: 1.3rem;
            font-weight: 500;
        }

        .hero-subtitle {
            margin: 0.55rem 0 1.45rem;
            color: rgba(250, 250, 250, 0.58);
            font-size: 0.92rem;
        }

        .hero-description {
            max-width: 570px;
            margin: 0 auto;
            color: rgba(250, 250, 250, 0.74);
            font-size: 1.03rem;
            line-height: 1.65;
        }

        div[data-testid="stTextInput"] input {
            border-radius: 12px;
        }

        div[data-testid="stPills"] [role="radiogroup"] {
            display: flex;
            flex-wrap: wrap;
            gap: 0.55rem;
        }

        div[data-testid="stPills"] [role="radio"] {
            margin: 0;
            padding: 0.45rem 0.8rem;
            border: 1px solid rgba(148, 163, 184, 0.24);
            border-radius: 999px;
            background: rgba(30, 41, 59, 0.72);
            color: #dbeafe;
            font-size: 0.86rem;
            font-weight: 600;
            transition: background 160ms ease, border-color 160ms ease, color 160ms ease;
        }

        div[data-testid="stPills"] [role="radio"]:hover {
            background: rgba(59, 130, 246, 0.18);
            border-color: rgba(147, 197, 253, 0.62);
            color: #f8fafc;
        }

        div[data-testid="stButton"] > button {
            min-height: 3rem;
            border-radius: 12px;
            font-weight: 600;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

if not is_logged_in():
    st.markdown(
        """
        <section class="hero" style="margin-bottom: 1.5rem;">
            <div class="hero-kicker">Research Intelligence</div>
            <h1 style="font-size: clamp(2.2rem, 6vw, 3.5rem);">Research Paper AI</h1>
            <p class="hero-subtitle">Sign in to access your research assistant.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    _, auth_column, _ = st.columns([1, 2, 1])
    with auth_column:
        with st.container(border=True):
            if st.session_state.auth_page == "register":
                show_register_page()
                if st.button("Already have an account? Sign in", use_container_width=True):
                    st.session_state.auth_page = "login"
                    st.rerun()
            else:
                show_login_page()
                if st.button("Need an account? Register", use_container_width=True):
                    st.session_state.auth_page = "register"
                    st.rerun()

    st.stop()

# Sidebar
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-shell">
            <div class="sidebar-brand">
                <div class="sidebar-icon">📚</div>
                <div>
                    <div class="sidebar-title">Research Paper Bot</div>
                    <div class="sidebar-subtitle">RAG-powered research assistant</div>
                </div>
            </div>
            <div class="sidebar-pill">● Live workspace</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    user = current_user()
    with st.container(border=True):
        st.caption("LOGGED IN AS")
        st.write(f"**{user['username']}**")
        st.caption(str(user["email"]))
        if st.button("Logout", use_container_width=True):
            logout_user()
            st.rerun()

    with st.container(border=True):
        st.markdown("#### 📄 Upload Research Paper")
        uploaded_pdf_path = render_upload_form()

        if uploaded_pdf_path:
            try:
                documents = load_pdf_documents(uploaded_pdf_path)
                with st.status("Indexing...", expanded=True) as upload_status:
                    st.write("Creating embeddings...")
                    st.write("Updating vector database...")
                    indexing_result = index_documents(documents)
                    upload_status.update(label="Index completed", state="complete")
            except (RuntimeError, ValueError) as error:
                st.error(str(error))
            else:
                st.success("✔ Upload successful")
                st.caption("Index completed")
                st.write(f"**Filename:** {uploaded_pdf_path.name}")
                pages_column, chunks_column = st.columns(2)
                pages_column.metric("Pages processed", indexing_result.pages_processed)
                chunks_column.metric("Chunks created", indexing_result.chunks_created)
                st.metric("Embedding time", f"{indexing_result.embedding_time:.2f} sec")

    st.markdown(
        """
        <div class="sidebar-card">
            <div class="section-label">About</div>
            <p>This AI chatbot answers questions from research papers using:</p>
            <ul>
                <li>🧠 Gemini</li>
                <li>🔗 LangChain</li>
                <li>🗂️ ChromaDB</li>
                <li>🎈 Streamlit</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="sidebar-card">
            <div class="section-label">Backend status</div>
            <div class="status-row"><span class="dot"></span> Gemini connected</div>
            <div class="status-row"><span class="dot"></span> Vector database loaded</div>
            <div class="status-row"><span class="dot"></span> Retriever ready</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="sidebar-card">
            <div class="section-label">Quick tip</div>
            <div class="tip">Ask complete questions like “Summarize this paper” or “Explain the methodology.”</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("""
<section class="hero">

<div class="hero-kicker">Research Intelligence</div>

<h1>Research Paper AI</h1>

<p class="hero-tagline">
Understand Research Instantly
</p>

<p class="hero-subtitle">
Powered by Gemini × LangChain × ChromaDB
</p>

<div style="text-align:center;">
    <p style="
        max-width:720px;
        margin:0 auto;
        padding:0 20px;
        text-align:center;
        line-height:1.8;
        color:#c9d1d9;
    ">
        Ask intelligent questions from your research papers using
        Retrieval-Augmented Generation (RAG).
    </p>
</div>

</section>
""", unsafe_allow_html=True)

with st.container(border=True):
    _, center, _ = st.columns([1, 5, 1])

    with center:
        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 1rem;">
                <h2 style="margin: 0 0 0.35rem;">Ask your research assistant</h2>
                <p style="margin: 0; color: rgba(250, 250, 250, 0.58);">
                    Grounded answers drawn from the papers in your knowledge base.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        suggestions = {
            "📄 Summarize this paper": "Summarize this paper.",
            "🧪 Explain the methodology": "Explain the methodology used in this paper.",
            "🔑 Key findings": "What are the key findings of this paper?",
            "⚠️ Limitations": "What are the limitations of this paper?",
            "🔮 Future work": "What future work does this paper suggest?",
            "⚖️ Compare papers": "Compare the papers in the knowledge base.",
        }

        def populate_question_from_suggestion():
            selected_suggestion = st.session_state.question_suggestion
            if selected_suggestion:
                st.session_state.question_input = suggestions[selected_suggestion]
            st.session_state.question_suggestion = None

        st.pills(
            "Suggested questions",
            options=list(suggestions),
            selection_mode="single",
            key="question_suggestion",
            on_change=populate_question_from_suggestion,
            label_visibility="collapsed",
        )

        question = st.text_input(
            "",
            placeholder="e.g., What methodology does this paper use?",
            key="question_input",
            label_visibility="collapsed",
        )
        ask_clicked = st.button("🚀 Ask AI", use_container_width=True, type="primary")

if ask_clicked and question:
    try:
        with st.spinner("🔍 Searching research papers..."):
            result = ask_question(question)
    except Exception as error:
        st.error(gemini_error_message(error) if is_gemini_error(error) else str(error))
        st.stop()

    st.divider()
    st.success("✅ Answer generated successfully!")

    answer_column, details_column = st.columns([4, 1], vertical_alignment="top")
    with answer_column:
        with st.container(border=True):
            st.markdown("#### 🤖 Answer")
            st.markdown(result["answer"])

    with details_column:
        with st.container(border=True):
            st.markdown("##### Response time")
            st.metric("⏱", f"{result['response_time']:.2f} sec")

    st.markdown("#### 📄 Sources")
    for index, source in enumerate(result["source_documents"], start=1):
        metadata = source.metadata
        filename = metadata.get("source", "Unknown File").split("\\")[-1].split("/")[-1]
        page = metadata.get("page", "N/A")

        with st.expander(f"Source {index}: {filename}"):
            st.write(f"**Page:** {page}")
            st.write(source.page_content[:500] + "...")
