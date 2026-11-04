from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker


def connect(url: str):
    """Share a session factory, never share a Session across worker threads."""
    if url.startswith("sqlite"):
        Path(".local").mkdir(exist_ok=True)
        engine = create_engine(url, connect_args={"check_same_thread": False, "timeout": 30})

        @event.listens_for(engine, "connect")
        def configure(dbapi_connection, _):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.close()
    else:
        engine = create_engine(url, pool_pre_ping=True)
    return engine, sessionmaker(engine, expire_on_commit=False)
