"""Streamlit login view."""

import streamlit as st

from auth.database import verify_login
from auth.session import login_user


def show_login_page() -> None:
    """Render the login form and authenticate the submitted credentials."""
    st.subheader("Welcome back")
    st.caption("Sign in to continue to your research paper assistant.")

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign in", use_container_width=True)

    if not submitted:
        return

    email = email.strip().lower()
    if not email or not password:
        st.error("Enter both your email address and password.")
        return

    user = verify_login(email, password)
    if user is None:
        st.error("Invalid email address or password.")
        return

    login_user(user)
    st.rerun()
