"""Pytest configuration and fixtures for E2E tests."""

import asyncio
import os
import uuid
from typing import AsyncGenerator, Dict

import httpx
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from sqlmodel import SQLModel
from app.services.database import database_service

# Test configuration
TEST_BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8000")
TEST_API_PREFIX = "/api/v1"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_db():
    """Create a clean test database for each test."""
    # Use a separate test database
    test_db_url = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/bmad_test"
    )

    engine = create_async_engine(test_db_url, echo=False)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def http_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Create an async HTTP client for API testing."""
    async with httpx.AsyncClient(
        base_url=TEST_BASE_URL,
        timeout=30.0,
        follow_redirects=True
    ) as client:
        yield client


@pytest_asyncio.fixture
async def test_user(http_client: httpx.AsyncClient) -> Dict[str, str]:
    """Create a test user and return credentials with JWT token."""
    # Generate unique email for this test
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    password = "TestPass123!@#"

    # Register user
    response = await http_client.post(
        f"{TEST_API_PREFIX}/auth/register",
        json={"email": email, "password": password}
    )

    if response.status_code == 201:
        data = response.json()
        return {
            "id": data["id"],
            "email": email,
            "password": password,
            "token": data["token"]
        }
    elif response.status_code == 400:
        # User might already exist, try to login
        response = await http_client.post(
            f"{TEST_API_PREFIX}/auth/login",
            data={
                "username": email,
                "password": password,
                "grant_type": "password"
            }
        )
        assert response.status_code == 200
        data = response.json()
        return {
            "id": None,
            "email": email,
            "password": password,
            "token": data["access_token"]
        }
    else:
        raise Exception(f"Failed to create test user: {response.status_code} - {response.text}")


@pytest_asyncio.fixture
async def authenticated_client(
    http_client: httpx.AsyncClient,
    test_user: Dict[str, str]
) -> httpx.AsyncClient:
    """Create an HTTP client with authentication headers."""
    http_client.headers.update({
        "Authorization": f"Bearer {test_user['token']}"
    })
    return http_client


@pytest.fixture
def sample_problem_simple() -> Dict:
    """Simple optimization problem for testing."""
    return {
        "problem_description": "给定数组 [3, 1, 4, 1, 5, 9]，找出最大值",
        "domain": "算法基础",
        "constraints": {}
    }


@pytest.fixture
def sample_problem_medium() -> Dict:
    """Medium complexity optimization problem."""
    return {
        "problem_description": "优化物流配送路径，有10个配送点，需要最小化总行驶距离",
        "domain": "物流优化",
        "constraints": {
            "vehicle_capacity": 100,
            "time_windows": [[8, 18]] * 10,
            "max_distance": 200
        }
    }


@pytest.fixture
def sample_problem_complex() -> Dict:
    """Complex optimization problem for testing."""
    return {
        "problem_description": """
        生产调度优化：3台机器，8个作业，每个作业有不同的处理时间和优先级。
        目标：最小化最大完工时间（makespan）。
        约束：每个作业必须按指定顺序经过多台机器。
        """,
        "domain": "制造业调度",
        "constraints": {
            "machines": 3,
            "jobs": 8,
            "precedence_constraints": True,
            "priorities": [1, 2, 3, 1, 2, 3, 1, 2]
        }
    }


# Helper functions

async def wait_for_workflow_status(
    client: httpx.AsyncClient,
    workflow_id: str,
    expected_status: str,
    timeout: int = 300,
    poll_interval: int = 2
) -> Dict:
    """
    Poll workflow status until it matches expected status or timeout.

    Args:
        client: HTTP client
        workflow_id: Workflow UUID
        expected_status: Expected status (e.g., 'paused', 'completed')
        timeout: Maximum wait time in seconds
        poll_interval: Time between polls in seconds

    Returns:
        Workflow data dict when status matches

    Raises:
        TimeoutError: If status doesn't match within timeout
    """
    elapsed = 0
    while elapsed < timeout:
        response = await client.get(f"{TEST_API_PREFIX}/workflows/{workflow_id}")
        assert response.status_code == 200

        workflow = response.json()
        if workflow["status"] == expected_status:
            return workflow

        if workflow["status"] == "failed":
            raise Exception(f"Workflow failed: {workflow.get('error_message')}")

        await asyncio.sleep(poll_interval)
        elapsed += poll_interval

    raise TimeoutError(
        f"Workflow {workflow_id} did not reach status '{expected_status}' within {timeout}s"
    )


def assert_workflow_structure(workflow: Dict):
    """Assert that workflow response has expected structure."""
    required_fields = [
        "id", "thread_id", "status", "current_phase",
        "input_data", "created_at"
    ]
    for field in required_fields:
        assert field in workflow, f"Missing required field: {field}"

    # Validate status
    valid_statuses = ["pending", "running", "paused", "completed", "failed", "cancelled"]
    assert workflow["status"] in valid_statuses, f"Invalid status: {workflow['status']}"
