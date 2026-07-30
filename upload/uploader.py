"""Streamlit PDF upload controls and file storage helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st


PAPERS_DIRECTORY = Path(__file__).resolve().parent.parent / "papers"


def _validate_pdf(uploaded_file: Any) -> str | None:
    """Return a friendly validation error, or ``None`` for a valid PDF."""
    filename = Path(uploaded_file.name).name
    if not filename.lower().endswith(".pdf"):
        return "Please choose a PDF file."

    file_bytes = uploaded_file.getvalue()
    if not file_bytes:
        return "The selected PDF is empty."

    if not file_bytes.startswith(b"%PDF-"):
        return "The selected file is not a valid PDF."

    return None


def render_upload_form() -> Path | None:
    """Render upload controls and save a new PDF, returning its path on success."""
    uploaded_file = st.file_uploader(
        "Choose PDF",
        type=["pdf"],
        key="research_paper_upload",
        label_visibility="visible",
    )
    upload_clicked = st.button(
        "Upload & Index",
        key="upload_and_index_paper",
        use_container_width=True,
    )

    if not upload_clicked:
        return None

    if uploaded_file is None:
        st.error("Choose a PDF before uploading.")
        return None

    validation_error = _validate_pdf(uploaded_file)
    if validation_error:
        st.error(validation_error)
        return None

    filename = Path(uploaded_file.name).name
    destination = PAPERS_DIRECTORY / filename
    if destination.exists():
        st.error("A paper with this filename has already been uploaded.")
        return None

    st.info("Uploading...")
    PAPERS_DIRECTORY.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(uploaded_file.getvalue())

    return destination
