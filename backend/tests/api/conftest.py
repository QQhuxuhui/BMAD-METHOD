"""Test configuration and fixtures for API tests."""

import asyncio
import os
import sys
import uuid
from datetime import datetime, UTC
from pathlib import Path
from typing import AsyncGenerator, Dict, Any
from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

# Mock PostgreSQL and LangGraph dependencies before importing app
mock_psycopg = MagicMock()
mock_psycopg_pool = MagicMock()
sys.modules['psycopg'] = mock_psycopg
sys.modules['psycopg.pq'] = MagicMock()
sys.modules['psycopg.types'] = MagicMock()
sys.modules['psycopg.types.json'] = MagicMock()
sys.modules['psycopg_pool'] = mock_psycopg_pool
sys.modules['psycopg_pool.pool'] = MagicMock()
sys.modules['langgraph.checkpoint.postgres'] = MagicMock()
sys.modules['langgraph.checkpoint.postgres.aio'] = MagicMock()

# Set test environment
os.environ['TESTING'] = 'true'

from app.models.user import User


# Test database setup
@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def test_db_engine():
    """Create a test database engine using SQLite in-memory."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def test_db_session(test_db_engine):
    """Create a test database session."""
    with Session(test_db_engine) as session:
        yield session


@pytest_asyncio.fixture
async def test_user(test_db_engine) -> User:
    """Create a test user for authentication."""
    with Session(test_db_engine) as session:
        user = User(
            id=1,
            email="test@example.com",
            hashed_password=User.hash_password("testpassword"),
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


@pytest_asyncio.fixture
async def auth_token(test_user: User) -> str:
    """Generate a JWT token for the test user."""
    from app.utils.auth import create_access_token

    token = create_access_token(str(test_user.id))
    return token.access_token


@pytest_asyncio.fixture
async def client(test_db_engine, test_user: User, auth_token: str) -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client for API testing."""
    # Import app here to avoid import issues
    from app.main import app
    from app.services.database import database_service
    from app.api.v1.auth import get_current_user

    # Override database service engine
    original_engine = database_service.engine
    database_service.engine = test_db_engine

    # Override get_current_user dependency to use test user
    async def override_get_current_user():
        return test_user

    app.dependency_overrides[get_current_user] = override_get_current_user

    # Create async client
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"Authorization": f"Bearer {auth_token}"}
    ) as ac:
        yield ac

    # Restore original dependencies
    app.dependency_overrides.clear()
    database_service.engine = original_engine


@pytest.fixture
def sample_workflow_data() -> Dict[str, Any]:
    """Create sample workflow request data."""
    return {
        "problem_description": "优化100辆车的配送路线",
        "domain": "logistics",
        "constraints": ["实时交通", "电动车电池限制"]
    }


@pytest.fixture
def sample_resume_data() -> Dict[str, Any]:
    """Create sample resume workflow request data."""
    return {
        "decision": "approved",
        "feedback": "算法选择合理，可以继续",
        "modified_data": None
    }
