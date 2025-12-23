from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import config
from app.database.models import Base
import os

# Create SQLite database
engine = create_engine(
    config.DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Create database tables"""
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")

def get_db_session():
    """Get database session"""
    return SessionLocal()
