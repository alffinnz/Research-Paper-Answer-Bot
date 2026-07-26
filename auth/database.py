"""SQLite helpers for application authentication."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import bcrypt


DATABASE_PATH = Path(__file__).resolve().parent.parent / "database" / "users.db"


def _get_connection() -> sqlite3.Connection:
    """Return a SQLite connection configured for dictionary-like rows."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    """Create the users table when the application is first started."""
    with _get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password_hash BLOB NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


def create_user(username: str, email: str, password_hash: bytes) -> int:
    """Save a new user and return its database id.

    ``sqlite3.IntegrityError`` is raised if the username or email already exists.
    """
    created_at = datetime.now(timezone.utc).isoformat()
    with _get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO users (username, email, password_hash, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (username, email, password_hash, created_at),
        )
        return cursor.lastrowid


def get_user_by_email(email: str) -> sqlite3.Row | None:
    """Return the user with the supplied email, if present."""
    with _get_connection() as connection:
        return connection.execute(
            "SELECT id, username, email, password_hash, created_at FROM users WHERE email = ?",
            (email,),
        ).fetchone()


def get_user_by_username(username: str) -> sqlite3.Row | None:
    """Return the user with the supplied username, if present."""
    with _get_connection() as connection:
        return connection.execute(
            "SELECT id, username, email, password_hash, created_at FROM users WHERE username = ?",
            (username,),
        ).fetchone()


def verify_login(email: str, password: str) -> sqlite3.Row | None:
    """Return the authenticated user, or ``None`` for invalid credentials."""
    user = get_user_by_email(email)
    if user is None:
        return None

    stored_hash = user["password_hash"]
    if isinstance(stored_hash, str):
        stored_hash = stored_hash.encode("utf-8")

    if bcrypt.checkpw(password.encode("utf-8"), stored_hash):
        return user

    return None
