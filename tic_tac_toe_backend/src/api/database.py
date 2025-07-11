from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

# Persistent SQLite DB (overridable by env)
DATABASE_URL = os.environ.get("SQLITE_URL", "sqlite:///./tic_tac_toe.sqlite3")

# Singleton SQLAlchemy engine/session/base for persistence
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# PUBLIC_INTERFACE
def get_db():
    """
    Dependency to get a SQLAlchemy session, closes automatically.
    Used by FastAPI dependency injection for persistent DB access.
    Yields:
        db (Session): SQLAlchemy session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Password hashing utils (bcrypt, in production use passlib or similar)
import hashlib

def hash_password(password: str) -> str:
    # PUBLIC_INTERFACE
    """Hash a password in a simple manner (for demo only)."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    # PUBLIC_INTERFACE
    """Verify the given password against hash."""
    return hash_password(password) == hashed
