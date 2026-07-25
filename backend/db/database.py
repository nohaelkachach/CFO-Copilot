# database.py
# This file sets up the database connection and provides a session factory.
# Everything that talks to the database goes through these.

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base 
from core.config import settings

# Engine = the actual connection to the database
# For SQLite, check_same_thread=False is required because FastAPI
# can handle multiple requests concurrently across different threads
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite only — remove for PostgreSQL
)

# SessionLocal = a factory that creates database sessions
# Each request gets its own session — opened at start, closed at end
# autocommit=False means we control when changes are saved
# autoflush=False means SQLAlchemy won't auto-sync before queries
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = the parent class all your models will inherit from
# SQLAlchemy uses it to track which classes are database tables
Base = declarative_base() 

def get_db():
    """
    Dependency function used by FastAPI route handlers.
    Creates a new database session for each request,
    yields it to the route, then closes it when done.
    Usage in a router: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    Creates all database tables based on the models that inherit from Base.
    Call this once at app startup — it won't recreate tables that already exist.
    """
    Base.metadata.create_all(bind=engine)