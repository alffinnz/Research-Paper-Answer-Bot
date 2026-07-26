"""Streamlit registration view."""

import sqlite3

import bcrypt
import streamlit as st

from auth.database import create_user, get_user_by_email, get_user_by_username


def show_register_page() -> None:
    """Render the registration form and create a user after validation."""
    st.subheader("Create an account")
    st.caption("Register to access your research paper assistant.")

    with st.form("registration_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm password", type="password")
        submitted = st.form_submit_button("Create account", use_container_width=True)

    if not submitted:
        return

    username = username.strip()
    email = email.strip().lower()

    if not all([username, email, password, confirm_password]):
        st.error("Please complete every field.")
        return

    if password != confirm_password:
        st.error("Passwords do not match.")
        return

    if get_user_by_username(username):
        st.error("That username is already in use.")
        return

    if get_user_by_email(email):
        st.error("An account already exists for that email address.")
        return

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    try:
        create_user(username, email, password_hash)
    except sqlite3.IntegrityError:
        st.error("That username or email address is already in use.")
        return

    st.session_state.auth_page = "login"
    st.success("Account created. You can now sign in.")
