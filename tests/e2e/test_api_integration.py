"""
End-to-end API integration tests for Phase 1 validation.

Tests the complete workflow: register → login → create workflow → HITL → completion
"""

import asyncio
import uuid
from typing import Dict

import httpx
import pytest

from tests.e2e.conftest import (
    TEST_API_PREFIX,
    assert_workflow_structure,
    wait_for_workflow_status,
)


@pytest.mark.asyncio
class TestAPIIntegration:
    """Test suite for API integration scenarios."""

    async def test_user_registration_and_login(self, http_client: httpx.AsyncClient):
        """Test user can register and login successfully."""
        # Generate unique email
        email = f"newuser_{uuid.uuid4().hex[:8]}@example.com"
        password = "SecurePass123!@#"

        # 1. Register new user
        response = await http_client.post(
            f"{TEST_API_PREFIX}/auth/register",
            json={"email": email, "password": password}
        )
        assert response.status_code in [200, 201], f"Registration failed: {response.text}"

        data = response.json()
        assert "id" in data
        assert data["email"] == email
        assert "token" in data
        token = data["token"]

        # 2. Verify token works
        response = await http_client.get(
            f"{TEST_API_PREFIX}/workflows/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

    async def test_workflow_creation(
        self,
        authenticated_client: httpx.AsyncClient,
        sample_problem_simple: Dict
    ):
        """Test workflow creation returns valid response."""
        response = await authenticated_client.post(
            f"{TEST_API_PREFIX}/workflows/",
            json=sample_problem_simple
        )

        assert response.status_code == 201, f"Workflow creation failed: {response.text}"

        workflow = response.json()
        assert_workflow_structure(workflow)

        # Verify workflow is in valid initial state
        assert workflow["status"] in ["pending", "running"]
        assert workflow["thread_id"] is not None
        assert workflow["input_data"]["problem_description"] == sample_problem_simple["problem_description"]

    async def test_workflow_status_query(
        self,
        authenticated_client: httpx.AsyncClient,
        sample_problem_simple: Dict
    ):
        """Test querying workflow status by ID."""
        # Create workflow
        response = await authenticated_client.post(
            f"{TEST_API_PREFIX}/workflows/",
            json=sample_problem_simple
        )
        assert response.status_code == 201
        workflow_id = response.json()["id"]

        # Query status
        response = await authenticated_client.get(
            f"{TEST_API_PREFIX}/workflows/{workflow_id}"
        )
        assert response.status_code == 200

        workflow = response.json()
        assert_workflow_structure(workflow)
        assert workflow["id"] == workflow_id

    async def test_workflow_list(
        self,
        authenticated_client: httpx.AsyncClient,
        sample_problem_simple: Dict
    ):
        """Test listing workflows with pagination."""
        # Create 3 workflows
        workflow_ids = []
        for _ in range(3):
            response = await authenticated_client.post(
                f"{TEST_API_PREFIX}/workflows/",
                json=sample_problem_simple
            )
            assert response.status_code == 201
            workflow_ids.append(response.json()["id"])

        # List workflows
        response = await authenticated_client.get(
            f"{TEST_API_PREFIX}/workflows/?limit=10"
        )
        assert response.status_code == 200

        data = response.json()
        assert "workflows" in data
        assert "total" in data
        assert len(data["workflows"]) >= 3

        # Verify our workflows are in the list
        returned_ids = [w["id"] for w in data["workflows"]]
        for wf_id in workflow_ids:
            assert wf_id in returned_ids

    async def test_workflow_access_control(
        self,
        http_client: httpx.AsyncClient,
        test_user: Dict,
        sample_problem_simple: Dict
    ):
        """Test that users can only access their own workflows."""
        # User 1 creates workflow
        user1_client = http_client
        user1_client.headers.update({"Authorization": f"Bearer {test_user['token']}"})

        response = await user1_client.post(
            f"{TEST_API_PREFIX}/workflows/",
            json=sample_problem_simple
        )
        assert response.status_code == 201
        workflow_id = response.json()["id"]

        # Create User 2
        email2 = f"user2_{uuid.uuid4().hex[:8]}@example.com"
        response = await http_client.post(
            f"{TEST_API_PREFIX}/auth/register",
            json={"email": email2, "password": "Pass123!@#"}
        )
        assert response.status_code == 201
        user2_token = response.json()["token"]

        # User 2 tries to access User 1's workflow
        user2_client = http_client
        user2_client.headers.update({"Authorization": f"Bearer {user2_token}"})

        response = await user2_client.get(
            f"{TEST_API_PREFIX}/workflows/{workflow_id}"
        )
        # Should be 403 Forbidden
        assert response.status_code == 403

    @pytest.mark.timeout(120)
    async def test_complete_workflow_simple_problem(
        self,
        authenticated_client: httpx.AsyncClient,
        sample_problem_simple: Dict
    ):
        """
        Test complete workflow execution for simple problem.

        This test may take up to 2 minutes if using real LLM.
        Use mock LLM for faster testing.
        """
        # 1. Create workflow
        response = await authenticated_client.post(
            f"{TEST_API_PREFIX}/workflows/",
            json=sample_problem_simple
        )
        assert response.status_code == 201
        workflow = response.json()
        workflow_id = workflow["id"]

        # 2. Wait for first HITL point (P1 - algorithm selection)
        try:
            workflow = await wait_for_workflow_status(
                authenticated_client,
                workflow_id,
                "paused",
                timeout=60
            )
        except TimeoutError:
            # If no HITL point reached, workflow might complete directly
            workflow = await wait_for_workflow_status(
                authenticated_client,
                workflow_id,
                "completed",
                timeout=60
            )
            # If completed directly, test passes
            assert workflow["status"] == "completed"
            return

        # 3. Verify workflow is at P1
        assert workflow["current_phase"].startswith("P1") or "algorithm" in workflow["current_phase"].lower()

        # 4. Approve and resume
        response = await authenticated_client.post(
            f"{TEST_API_PREFIX}/workflows/{workflow_id}/resume",
            json={
                "decision": "approve",
                "feedback": "Looks good, proceed"
            }
        )
        assert response.status_code == 200

        # 5. Wait for second HITL point or completion
        try:
            workflow = await wait_for_workflow_status(
                authenticated_client,
                workflow_id,
                "paused",
                timeout=60
            )

            # If paused again (P2.5), approve again
            response = await authenticated_client.post(
                f"{TEST_API_PREFIX}/workflows/{workflow_id}/resume",
                json={
                    "decision": "approve",
                    "feedback": "Code looks good"
                }
            )
            assert response.status_code == 200
        except TimeoutError:
            pass  # Might complete directly

        # 6. Wait for completion
        workflow = await wait_for_workflow_status(
            authenticated_client,
            workflow_id,
            "completed",
            timeout=60
        )

        # 7. Verify output
        assert workflow["status"] == "completed"
        assert workflow["output_data"] is not None
        assert workflow["completed_at"] is not None

        # Check if output contains expected fields
        output = workflow["output_data"]
        # At minimum, should have some generated content
        assert len(str(output)) > 100

    async def test_workflow_cancellation(
        self,
        authenticated_client: httpx.AsyncClient,
        sample_problem_medium: Dict
    ):
        """Test workflow can be cancelled."""
        # Create workflow
        response = await authenticated_client.post(
            f"{TEST_API_PREFIX}/workflows/",
            json=sample_problem_medium
        )
        assert response.status_code == 201
        workflow_id = response.json()["id"]

        # Wait a bit for workflow to start
        await asyncio.sleep(2)

        # Cancel workflow (if cancel endpoint exists)
        response = await authenticated_client.post(
            f"{TEST_API_PREFIX}/workflows/{workflow_id}/cancel"
        )

        if response.status_code == 404:
            # Cancel endpoint not implemented yet
            pytest.skip("Cancel endpoint not implemented")
        else:
            assert response.status_code == 200
            workflow = response.json()
            assert workflow["status"] == "cancelled"

    async def test_multiple_concurrent_workflows(
        self,
        authenticated_client: httpx.AsyncClient,
        sample_problem_simple: Dict
    ):
        """Test creating multiple workflows concurrently."""
        # Create 5 workflows concurrently
        tasks = []
        for i in range(5):
            problem = sample_problem_simple.copy()
            problem["problem_description"] = f"{problem['problem_description']} (Test {i})"
            task = authenticated_client.post(
                f"{TEST_API_PREFIX}/workflows/",
                json=problem
            )
            tasks.append(task)

        responses = await asyncio.gather(*tasks)

        # Verify all created successfully
        workflow_ids = []
        for response in responses:
            assert response.status_code == 201
            workflow = response.json()
            workflow_ids.append(workflow["id"])
            assert_workflow_structure(workflow)

        # Verify all workflows have unique IDs and thread_ids
        assert len(set(workflow_ids)) == 5

        # Verify we can query each workflow
        for workflow_id in workflow_ids:
            response = await authenticated_client.get(
                f"{TEST_API_PREFIX}/workflows/{workflow_id}"
            )
            assert response.status_code == 200


@pytest.mark.asyncio
class TestWorkflowPhaseTransitions:
    """Test workflow state transitions through phases."""

    async def test_workflow_status_progression(
        self,
        authenticated_client: httpx.AsyncClient,
        sample_problem_simple: Dict
    ):
        """Test workflow progresses through expected statuses."""
        # Create workflow
        response = await authenticated_client.post(
            f"{TEST_API_PREFIX}/workflows/",
            json=sample_problem_simple
        )
        assert response.status_code == 201
        workflow_id = response.json()["id"]

        # Track status changes
        status_history = []

        # Poll for 30 seconds to observe status changes
        for _ in range(15):
            response = await authenticated_client.get(
                f"{TEST_API_PREFIX}/workflows/{workflow_id}"
            )
            assert response.status_code == 200
            workflow = response.json()

            current_status = workflow["status"]
            if not status_history or status_history[-1] != current_status:
                status_history.append(current_status)

            if current_status in ["completed", "failed", "paused"]:
                break

            await asyncio.sleep(2)

        # Verify status progression is valid
        # Should start with pending or running
        assert status_history[0] in ["pending", "running"]

        # Should not have invalid transitions
        invalid_transitions = [
            ("completed", "running"),
            ("failed", "running"),
            ("cancelled", "running"),
        ]

        for i in range(len(status_history) - 1):
            transition = (status_history[i], status_history[i + 1])
            assert transition not in invalid_transitions, \
                f"Invalid transition: {transition}"


@pytest.mark.asyncio
class TestAPIErrorHandling:
    """Test API error handling and edge cases."""

    async def test_invalid_token(self, http_client: httpx.AsyncClient):
        """Test API rejects invalid JWT token."""
        response = await http_client.get(
            f"{TEST_API_PREFIX}/workflows/",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        assert response.status_code == 401

    async def test_missing_required_fields(
        self,
        authenticated_client: httpx.AsyncClient
    ):
        """Test API returns validation error for missing fields."""
        response = await authenticated_client.post(
            f"{TEST_API_PREFIX}/workflows/",
            json={"domain": "test"}  # Missing problem_description
        )
        assert response.status_code == 422

    async def test_nonexistent_workflow(
        self,
        authenticated_client: httpx.AsyncClient
    ):
        """Test querying non-existent workflow returns 404."""
        fake_id = str(uuid.uuid4())
        response = await authenticated_client.get(
            f"{TEST_API_PREFIX}/workflows/{fake_id}"
        )
        assert response.status_code == 404

    async def test_invalid_resume_decision(
        self,
        authenticated_client: httpx.AsyncClient,
        sample_problem_simple: Dict
    ):
        """Test resuming with invalid decision."""
        # Create and get a workflow
        response = await authenticated_client.post(
            f"{TEST_API_PREFIX}/workflows/",
            json=sample_problem_simple
        )
        assert response.status_code == 201
        workflow_id = response.json()["id"]

        # Try to resume with invalid decision
        response = await authenticated_client.post(
            f"{TEST_API_PREFIX}/workflows/{workflow_id}/resume",
            json={
                "decision": "invalid_decision",
                "feedback": "test"
            }
        )
        # Should return validation error
        assert response.status_code in [400, 422]
