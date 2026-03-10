from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os
from pathlib import Path

# Create database directory if it doesn't exist
db_dir = Path(__file__).parent / 'data'
db_dir.mkdir(exist_ok=True)

SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_dir}/netguard.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    from .models import TrafficLog, Alert  # Import here to avoid circular imports
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")

# Example usage
if __name__ == "__main__":
    init_db()
