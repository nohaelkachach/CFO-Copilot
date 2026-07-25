# tests/conftest.py
# conftest.py is special — pytest loads it automatically before any test.
# It defines "fixtures" — reusable setup code shared across all test files.

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from db.database import Base, get_db

# Use a separate in-memory SQLite database for tests
# This means tests never touch your real database
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@pytest.fixture(scope="function")
def db():
    """
    Creates a fresh database for each test function.
    Tables are created before the test and dropped after.
    This ensures tests don't interfere with each other.
    """
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """
    Creates a test HTTP client that uses the test database.
    Override get_db dependency so FastAPI uses test DB, not real DB.
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Clean up — remove the override after the test
    app.dependency_overrides.clear()