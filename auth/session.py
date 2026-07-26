"""Session-state helpers for Streamlit authentication."""

from collections.abc import Mapping

import streamlit as st


def login_user(user: Mapping[str, object]) -> None:
    """Store the authenticated user's safe profile data in session state."""
    st.session_state.logged_in = True
    st.session_state.user = {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
    }


def logout_user() -> None:
    """Clear the current authentication session and return to the login view."""
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.auth_page = "login"


def current_user() -> dict[str, object] | None:
    """Return the current authenticated user's safe profile, if any."""
    return st.session_state.get("user")


def is_logged_in() -> bool:
    """Return whether the current Streamlit session is authenticated."""
    return bool(st.session_state.get("logged_in", False) and current_user())
