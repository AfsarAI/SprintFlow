from datetime import timedelta
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.core.security import create_access_token, hash_password
from app.db.base import Base
from app.main import app
from app.models.user import User

# Isolated in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


# Enforce foreign key constraints in SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_database():
    """Create all tables before each test and drop them after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Provide a transactional database session for tests."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    """Provide a TestClient with the database session overridden."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Provide a default registered test user (User A)."""
    user = User(
        email="testuser@example.com",
        password_hash=hash_password("password123"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    """Provide Bearer auth headers for User A."""
    token = create_access_token(subject=test_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def other_user(db_session):
    """Provide a second test user (User B) for cross-user tests."""
    user = User(
        email="otheruser@example.com",
        password_hash=hash_password("password456"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def other_auth_headers(other_user):
    """Provide Bearer auth headers for User B."""
    token = create_access_token(subject=other_user.id)
    return {"Authorization": f"Bearer {token}"}
