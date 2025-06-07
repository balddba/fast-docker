"""Database configuration and session management for the Docker management system.

This module provides database initialization and session management functionality using SQLModel.
It sets up an SQLite database and provides functions to initialize the database schema
and manage database sessions.

The module uses SQLite as the database backend, storing data in a file named 'docker_hosts.db'.
It provides a session factory through the get_session function which should be used
for all database operations.
"""

from sqlmodel import SQLModel, create_engine, Session
from typing import Generator

DATABASE_URL = "sqlite:///docker_hosts.db"

engine = create_engine(DATABASE_URL, echo=False)

def init_db() -> None:
    """Initialize the database by creating all defined tables.

    This function should be called when the application starts to ensure
    all necessary database tables are created. It uses the SQLModel metadata
    to create tables for all registered models.

    Note:
        This is safe to call multiple times as SQLModel will not recreate
        existing tables.
    """
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    """Create and yield a database session.

    This function is designed to be used as a FastAPI dependency for
    database operations. It creates a new database session, yields it
    for use in API endpoints, and ensures proper cleanup after use.

    Yields:
        Session: A SQLModel session instance for database operations.

    Example:
        @app.get("/items")
        def get_items(session: Session = Depends(get_session)):
            return session.query(Item).all()
    """
    with Session(engine) as session:
        yield session