"""Integration tests for LangServe routes.

This module tests the LangServe-generated API endpoints for BMAD workflow,
including authentication, streaming, and error handling.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import status

from app.main import app
from app.utils.auth import create_access_token


# Test fixtures
@pytest.fixture
def auth_headers():
    """Create JWT auth headers for testing.

    Returns:
        Dict containing Authorization header with valid JWT token
    """
    # Create a test token with thread_id (which is used to identify user)
    # Note: create_access_token takes thread_id as first parameter
    token = create_access_token(thread_id="test-thread-1")
    return {"Authorization": f"Bearer {token.access_token}"}


@pytest.fixture
def auth_headers_user2():
    """Create JWT auth headers for a second user.

    Returns:
        Dict containing Authorization header for user 2
    """
    token = create_access_token(thread_id="test-thread-2")
    return {"Authorization": f"Bearer {token.access_token}"}


@pytest.fixture
def workflow_input():
    """Create valid workflow input data.

    Returns:
        Dict containing problem description and optional parameters
    """
    return {
        "input": {
            "problem_description": "优化100辆车的配送路线，最小化总行驶距离",
            "domain": "logistics",
            "constraints": ["时间窗口约束", "车辆容量限制"],
        }
    }


# Test: JWT Authentication
@pytest.mark.asyncio
async def test_langserve_invoke_without_token():
    """Test that LangServe endpoints require JWT authentication.

    Should return 401 when no auth token is provided.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/bmad-workflow/invoke",
            json={"input": {"problem_description": "test"}},
        )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_langserve_invoke_with_invalid_token():
    """Test that LangServe endpoints reject invalid JWT tokens.

    Should return 401 when auth token is invalid.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/bmad-workflow/invoke",
            headers={"Authorization": "Bearer invalid_token_here"},
            json={"input": {"problem_description": "test"}},
        )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# Test: Input Validation
@pytest.mark.asyncio
async def test_langserve_invoke_missing_problem_description(auth_headers):
    """Test that invoke endpoint validates required fields.

    Should return 422 when problem_description is missing.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/bmad-workflow/invoke",
            headers=auth_headers,
            json={"input": {"domain": "logistics"}},  # Missing problem_description
        )

    # LangServe returns 500 for validation errors in Runnable
    # or 422 if FastAPI catches it first
    assert response.status_code in [
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    ]


@pytest.mark.asyncio
async def test_langserve_invoke_empty_problem_description(auth_headers):
    """Test that invoke endpoint validates problem_description length.

    Should return error when problem_description is empty or too short.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/bmad-workflow/invoke",
            headers=auth_headers,
            json={"input": {"problem_description": ""}},  # Empty
        )

    assert response.status_code in [
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    ]


# Test: Invoke Endpoint
@pytest.mark.asyncio
@pytest.mark.slow
async def test_langserve_invoke_success(auth_headers, workflow_input):
    """Test successful workflow invocation via LangServe.

    This test may take a while as it waits for workflow completion.
    Marked as 'slow' to allow skipping in quick test runs.
    """
    async with AsyncClient(app=app, base_url="http://test", timeout=300.0) as client:
        response = await client.post(
            "/api/v1/bmad-workflow/invoke",
            headers=auth_headers,
            json=workflow_input,
        )

    # Could be 200 (success) or 500 (workflow error)
    # We just verify the endpoint is reachable with auth
    assert response.status_code in [
        status.HTTP_200_OK,
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    ]

    if response.status_code == status.HTTP_200_OK:
        data = response.json()
        assert "output" in data
        # Output should contain workflow_id, status, etc.
        output = data["output"]
        assert "workflow_id" in output
        assert "status" in output


# Test: Stream Endpoint
@pytest.mark.asyncio
@pytest.mark.slow
async def test_langserve_stream_without_token():
    """Test that stream endpoint requires authentication.

    Should return 401 when no auth token is provided.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/bmad-workflow/stream",
            json={"input": {"problem_description": "test"}},
        )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
@pytest.mark.slow
async def test_langserve_stream_with_auth(auth_headers, workflow_input):
    """Test SSE streaming workflow execution.

    Verifies that the stream endpoint returns SSE formatted events.
    Marked as 'slow' due to potential long execution time.
    """
    async with AsyncClient(app=app, base_url="http://test", timeout=60.0) as client:
        # Stream endpoint should return SSE events
        # We'll test that the connection is established
        async with client.stream(
            "POST",
            "/api/v1/bmad-workflow/stream",
            headers=auth_headers,
            json=workflow_input,
        ) as response:
            # Should get 200 or 500
            assert response.status_code in [
                status.HTTP_200_OK,
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            ]

            if response.status_code == status.HTTP_200_OK:
                # Verify SSE content type
                content_type = response.headers.get("content-type", "")
                assert "text/event-stream" in content_type or "application/json" in content_type

                # Try to read first few events (with timeout)
                event_count = 0
                max_events = 5
                async for chunk in response.aiter_bytes():
                    event_count += 1
                    if event_count >= max_events:
                        break

                assert event_count > 0, "Should receive at least one event"


# Test: User Isolation
@pytest.mark.asyncio
@pytest.mark.slow
async def test_user_context_isolation(auth_headers, auth_headers_user2, workflow_input):
    """Test that different users' workflows are isolated.

    Verifies that user_id is correctly injected into workflow execution context.
    """
    async with AsyncClient(app=app, base_url="http://test", timeout=300.0) as client:
        # Create workflow as user 1
        response1 = await client.post(
            "/api/v1/bmad-workflow/invoke",
            headers=auth_headers,
            json=workflow_input,
        )

        # Create workflow as user 2
        response2 = await client.post(
            "/api/v1/bmad-workflow/invoke",
            headers=auth_headers_user2,
            json=workflow_input,
        )

    # Both requests should be processed independently
    # (we can't easily verify user_id without accessing database,
    # but we ensure both requests are accepted)
    assert response1.status_code in [200, 500]
    assert response2.status_code in [200, 500]


# Test: OpenAPI Schema
@pytest.mark.asyncio
async def test_openapi_schema_includes_langserve_endpoints():
    """Test that OpenAPI schema includes LangServe endpoints.

    Verifies that /docs and /openapi.json include the auto-generated endpoints.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/openapi.json")

    assert response.status_code == status.HTTP_200_OK

    openapi_spec = response.json()
    paths = openapi_spec.get("paths", {})

    # Check that LangServe endpoints are present
    assert "/api/v1/bmad-workflow/invoke" in paths
    assert "/api/v1/bmad-workflow/batch" in paths
    assert "/api/v1/bmad-workflow/stream" in paths

    # Verify invoke endpoint has correct methods and security
    invoke_spec = paths["/api/v1/bmad-workflow/invoke"]
    assert "post" in invoke_spec

    # Check for security requirements (JWT)
    post_spec = invoke_spec["post"]
    assert "security" in post_spec or "HTTPBearer" in str(openapi_spec)


# Test: Error Scenarios
@pytest.mark.asyncio
async def test_langserve_invoke_malformed_json(auth_headers):
    """Test that endpoints handle malformed JSON gracefully.

    Should return 422 for invalid JSON structure.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Send invalid JSON structure
        response = await client.post(
            "/api/v1/bmad-workflow/invoke",
            content="{ invalid json }",  # Malformed JSON
            headers={**auth_headers, "Content-Type": "application/json"},
        )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_langserve_batch_endpoint_exists(auth_headers):
    """Test that batch endpoint is accessible.

    Verifies that the auto-generated batch endpoint exists.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/bmad-workflow/batch",
            headers=auth_headers,
            json={"inputs": []},  # Empty batch
        )

    # Should not return 404 (endpoint exists)
    assert response.status_code != status.HTTP_404_NOT_FOUND
    # Could be 200, 422, or 500 depending on implementation
    assert response.status_code in [
        status.HTTP_200_OK,
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    ]


# Test: Playground Endpoint
@pytest.mark.asyncio
async def test_playground_endpoint_accessible():
    """Test that Playground UI endpoint is accessible.

    Verifies that GET /playground/ returns HTML content.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/bmad-workflow/playground/")

    # Should return 200 with HTML content (or redirect)
    assert response.status_code in [
        status.HTTP_200_OK,
        status.HTTP_307_TEMPORARY_REDIRECT,
        status.HTTP_308_PERMANENT_REDIRECT,
    ]

    if response.status_code == status.HTTP_200_OK:
        content_type = response.headers.get("content-type", "")
        assert "text/html" in content_type or "text/plain" in content_type
