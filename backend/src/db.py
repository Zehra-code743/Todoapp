"""
Database configuration and session management
"""

from sqlmodel import Session, create_engine, SQLModel
from src.config import settings

# Import models BEFORE creating engine to register them with SQLModel metadata
from src.models.user import User
from src.models.task import Task

# Create database engine
engine = create_engine(
    settings.database_url,
    echo=settings.env == "development",
    pool_pre_ping=True,
    pool_recycle=3600,
)


def get_session():
    """
    Dependency to get database session
    Yields a SQLModel Session bound to the engine
    """
    with Session(engine) as session:
        yield session
