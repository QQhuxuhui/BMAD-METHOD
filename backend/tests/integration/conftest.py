"""Integration test configuration for workflow and LangGraph tests.

This module provides fixtures and configuration for integration tests that:
- Use real PostgreSQL database
- Test actual LangGraph workflow execution
- Verify checkpoint persistence
- Test HITL interrupt/resume mechanisms
"""

import asyncio
import os
import sys
import uuid
from datetime import datetime, UTC
from pathlib import Path
from typing import AsyncGenerator, Dict, Any

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlmodel import Session, select
from langgraph.graph.state import CompiledStateGraph

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

# Set test environment
os.environ['TESTING'] = 'true'
os.environ['ENVIRONMENT'] = 'development'

from app.models.user import User
from app.models.workflow_execution import WorkflowExecution
from app.services.database import database_service
from app.utils.auth import create_access_token
from app.core.langgraph.workflow import create_bmad_workflow


# Test database setup - uses real PostgreSQL
@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_db_engine():
    """Use the real PostgreSQL database engine for integration tests.

    Note: This uses the actual development database, not an in-memory database.
    Make sure your PostgreSQL instance is running before running integration tests.
    """
    return database_service.engine


@pytest.fixture(scope="function")
def test_db_session(test_db_engine):
    """Create a test database session."""
    with Session(test_db_engine) as session:
        yield session


@pytest_asyncio.fixture
async def test_user(test_db_session: Session) -> User:
    """Create or get a test user for authentication."""
    # Try to find existing test user
    statement = select(User).where(User.email == "integration_test@example.com")
    user = test_db_session.exec(statement).first()

    if user:
        return user

    # Create new test user
    user = User(
        email="integration_test@example.com",
        hashed_password=User.hash_password("integrationtest123"),
    )
    test_db_session.add(user)
    test_db_session.commit()
    test_db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_token(test_user: User) -> str:
    """Generate a JWT token for the test user."""
    token = create_access_token(str(test_user.id))
    return token.access_token


@pytest_asyncio.fixture
async def client(test_user: User, auth_token: str) -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client for API testing with real database."""
    from app.main import app
    from app.api.v1.auth import get_current_user

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


@pytest_asyncio.fixture
async def bmad_workflow() -> AsyncGenerator[CompiledStateGraph, None]:
    """Create a real BMAD workflow instance for testing.

    This fixture creates an actual LangGraph workflow with PostgreSQL checkpoint.
    Use this for integration tests that need to verify actual workflow execution.
    """
    workflow = await create_bmad_workflow()
    yield workflow
    # Cleanup if needed


@pytest.fixture
def sample_workflow_data() -> Dict[str, Any]:
    """Create sample workflow request data for integration tests."""
    return {
        "problem_description": "优化一个包含10个城市的旅行商问题(TSP)，需要找到访问所有城市并返回起点的最短路径",
        "domain": "logistics",
        "constraints": ["每个城市只能访问一次", "必须返回起点", "路径总长度最短"]
    }


@pytest.fixture
def unique_thread_id() -> str:
    """Generate a unique thread ID for each test."""
    return f"integration_test_{uuid.uuid4().hex[:12]}_{int(datetime.now(UTC).timestamp())}"


@pytest_asyncio.fixture
async def cleanup_workflow(test_db_session: Session):
    """Cleanup fixture to remove test workflows after tests."""
    created_workflow_ids = []

    def track_workflow(workflow_id: uuid.UUID):
        """Track a workflow ID for cleanup."""
        created_workflow_ids.append(workflow_id)

    yield track_workflow

    # Cleanup after test
    for workflow_id in created_workflow_ids:
        try:
            workflow = test_db_session.get(WorkflowExecution, workflow_id)
            if workflow:
                test_db_session.delete(workflow)
            test_db_session.commit()
        except Exception as e:
            print(f"Failed to cleanup workflow {workflow_id}: {e}")
