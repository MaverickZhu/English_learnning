import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def _get_database_url() -> str:
    return os.getenv(
        "DATABASE_URL",
        "postgresql://english:english@localhost:25432/english_learning",
    )


engine = create_engine(_get_database_url(), pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
