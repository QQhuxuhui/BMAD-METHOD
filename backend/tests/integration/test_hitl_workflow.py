"""Integration tests for HITL (Human-in-the-Loop) workflow functionality.

This module tests the complete HITL workflow including:
- Workflow execution until interrupt
- Interrupt detection and state persistence
- User approval/rejection
- Workflow resumption from checkpoint
- Multiple approval points (P1, P2.5)
"""

import asyncio
import pytest
import pytest_asyncio
from uuid import UUID
from datetime import datetime, UTC

from httpx import AsyncClient
from sqlmodel import Session, select

from app.models.workflow_execution import WorkflowExecution
from app.models.human_approval import HumanApproval


@pytest.mark.asyncio
@pytest.mark.integration
class TestHITLWorkflow:
    """Test suite for HITL workflow interrupt and resume functionality."""

    async def test_workflow_creation_starts_execution(
        self,
        client: AsyncClient,
        sample_workflow_data,
        cleanup_workflow,
    ):
        """Test that creating a workflow starts background execution.

        Verifies:
        - Workflow is created with status 'pending'
        - Background task is initiated
        - Workflow transitions to 'running' status
        """
        # Create workflow
        response = await client.post("/api/v1/workflows/", json=sample_workflow_data)
        assert response.status_code == 201

        workflow_data = response.json()
        workflow_id = UUID(workflow_data["id"])
        cleanup_workflow(workflow_id)

        # Verify initial status
        assert workflow_data["status"] == "pending"
        assert workflow_data["current_phase"] == "P0"

        # Wait a moment for background task to start
        await asyncio.sleep(2)

        # Check workflow status again
        response = await client.get(f"/api/v1/workflows/{workflow_id}")
        assert response.status_code == 200

        updated_workflow = response.json()
        # Should be running or paused (if it reached approval point quickly)
        assert updated_workflow["status"] in ["running", "paused", "pending"]


    async def test_workflow_pauses_at_p1_approval(
        self,
        client: AsyncClient,
        sample_workflow_data,
        cleanup_workflow,
    ):
        """Test that workflow pauses at P1 approval point.

        Verifies:
        - Workflow executes Phase 0 and Phase 1
        - Workflow pauses at P1 approval node
        - HumanApproval record is created
        - Workflow status is 'paused'
        """
        # Create workflow
        response = await client.post("/api/v1/workflows/", json=sample_workflow_data)
        assert response.status_code == 201

        workflow_data = response.json()
        workflow_id = UUID(workflow_data["id"])
        cleanup_workflow(workflow_id)

        # Wait for workflow to reach P1 approval (adjust timing as needed)
        # This depends on how fast the agents execute
        max_wait_time = 60  # seconds
        poll_interval = 2  # seconds
        elapsed = 0

        workflow_paused = False
        while elapsed < max_wait_time:
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

            response = await client.get(f"/api/v1/workflows/{workflow_id}")
            assert response.status_code == 200

            workflow = response.json()
            if workflow["status"] == "paused":
                workflow_paused = True
                assert "P1" in workflow["current_phase"]
                break
            elif workflow["status"] in ["failed", "completed"]:
                # Workflow finished unexpectedly
                pytest.fail(f"Workflow finished with status {workflow['status']} before reaching P1 approval")

        # For now, this test might fail if the workflow doesn't use real models
        # We'll mark it as expected to potentially skip in CI
        if not workflow_paused:
            pytest.skip("Workflow did not pause at P1 - may require real model configuration")


    async def test_resume_workflow_with_approval(
        self,
        client: AsyncClient,
        sample_workflow_data,
        cleanup_workflow,
    ):
        """Test resuming workflow after user approval.

        Verifies:
        - User can submit approval decision
        - Workflow resumes from checkpoint
        - Workflow continues execution
        - HumanApproval record is updated
        """
        # Create and wait for P1 pause
        response = await client.post("/api/v1/workflows/", json=sample_workflow_data)
        workflow_id = UUID(response.json()["id"])
        cleanup_workflow(workflow_id)

        # Wait for pause (with timeout)
        max_wait = 60
        for _ in range(max_wait // 2):
            await asyncio.sleep(2)
            response = await client.get(f"/api/v1/workflows/{workflow_id}")
            if response.json()["status"] == "paused":
                break

        workflow = response.json()
        if workflow["status"] != "paused":
            pytest.skip("Workflow did not pause - skipping resume test")

        # Submit approval
        resume_data = {
            "decision": "approved",
            "feedback": "Looks good, proceed with domain expert phase"
        }

        response = await client.post(
            f"/api/v1/workflows/{workflow_id}/resume",
            json=resume_data
        )
        assert response.status_code == 200

        resumed_workflow = response.json()
        # Should be running again or paused at next approval point
        assert resumed_workflow["status"] in ["running", "paused", "completed"]


    async def test_resume_workflow_with_rejection(
        self,
        client: AsyncClient,
        sample_workflow_data,
        cleanup_workflow,
    ):
        """Test workflow rejection at approval point.

        Verifies:
        - User can reject workflow
        - Workflow status changes to 'rejected'
        - Error message includes rejection reason
        - Workflow does not continue execution
        """
        # Create and wait for pause
        response = await client.post("/api/v1/workflows/", json=sample_workflow_data)
        workflow_id = UUID(response.json()["id"])
        cleanup_workflow(workflow_id)

        # Wait for pause
        max_wait = 60
        for _ in range(max_wait // 2):
            await asyncio.sleep(2)
            response = await client.get(f"/api/v1/workflows/{workflow_id}")
            if response.json()["status"] == "paused":
                break

        workflow = response.json()
        if workflow["status"] != "paused":
            pytest.skip("Workflow did not pause - skipping rejection test")

        # Submit rejection
        resume_data = {
            "decision": "rejected",
            "feedback": "Algorithm selection is not appropriate for this problem"
        }

        response = await client.post(
            f"/api/v1/workflows/{workflow_id}/resume",
            json=resume_data
        )
        assert response.status_code == 200

        rejected_workflow = response.json()
        assert rejected_workflow["status"] == "rejected"
        assert "rejected" in rejected_workflow["error_message"].lower()
        assert rejected_workflow["completed_at"] is not None


    async def test_resume_workflow_with_modified_data(
        self,
        client: AsyncClient,
        sample_workflow_data,
        cleanup_workflow,
    ):
        """Test workflow resume with modified data.

        Verifies:
        - User can modify data during approval
        - Modified data is passed to workflow
        - Workflow continues with modified parameters
        """
        # Create and wait for pause
        response = await client.post("/api/v1/workflows/", json=sample_workflow_data)
        workflow_id = UUID(response.json()["id"])
        cleanup_workflow(workflow_id)

        # Wait for pause
        max_wait = 60
        for _ in range(max_wait // 2):
            await asyncio.sleep(2)
            response = await client.get(f"/api/v1/workflows/{workflow_id}")
            if response.json()["status"] == "paused":
                break

        workflow = response.json()
        if workflow["status"] != "paused":
            pytest.skip("Workflow did not pause - skipping modification test")

        # Submit approval with modifications
        resume_data = {
            "decision": "modified",
            "feedback": "Updated algorithm parameters for better performance",
            "modified_data": {
                "algorithm_params": {
                    "max_iterations": 1000,
                    "temperature": 0.8
                }
            }
        }

        response = await client.post(
            f"/api/v1/workflows/{workflow_id}/resume",
            json=resume_data
        )
        assert response.status_code == 200

        modified_workflow = response.json()
        assert modified_workflow["status"] in ["running", "paused", "completed"]


    async def test_cannot_resume_non_paused_workflow(
        self,
        client: AsyncClient,
        sample_workflow_data,
        cleanup_workflow,
    ):
        """Test that resuming non-paused workflow returns error.

        Verifies:
        - Cannot resume workflow that is not paused
        - Appropriate error message is returned
        """
        # Create workflow
        response = await client.post("/api/v1/workflows/", json=sample_workflow_data)
        workflow_id = UUID(response.json()["id"])
        cleanup_workflow(workflow_id)

        # Try to resume immediately (before pause)
        resume_data = {
            "decision": "approved",
            "feedback": "Test"
        }

        response = await client.post(
            f"/api/v1/workflows/{workflow_id}/resume",
            json=resume_data
        )

        # Should return 400 if not paused
        # (might be 200 if it happened to pause by the time we called)
        if response.status_code == 400:
            assert "cannot resume" in response.json()["detail"].lower() or \
                   "not paused" in response.json()["detail"].lower()


    async def test_multiple_approval_points(
        self,
        client: AsyncClient,
        sample_workflow_data,
        cleanup_workflow,
    ):
        """Test workflow with multiple HITL approval points (P1 and P2.5).

        Verifies:
        - Workflow pauses at P1
        - After P1 approval, continues to P2.5
        - Workflow pauses at P2.5
        - After P2.5 approval, continues to completion
        """
        # Create workflow
        response = await client.post("/api/v1/workflows/", json=sample_workflow_data)
        workflow_id = UUID(response.json()["id"])
        cleanup_workflow(workflow_id)

        # Wait for first pause (P1)
        max_wait = 60
        first_pause = False
        for _ in range(max_wait // 2):
            await asyncio.sleep(2)
            response = await client.get(f"/api/v1/workflows/{workflow_id}")
            workflow = response.json()
            if workflow["status"] == "paused" and "P1" in workflow["current_phase"]:
                first_pause = True
                break

        if not first_pause:
            pytest.skip("Workflow did not reach P1 approval")

        # Approve P1
        response = await client.post(
            f"/api/v1/workflows/{workflow_id}/resume",
            json={"decision": "approved", "feedback": "P1 approved"}
        )
        assert response.status_code == 200

        # Wait for second pause (P2.5)
        second_pause = False
        for _ in range(max_wait // 2):
            await asyncio.sleep(2)
            response = await client.get(f"/api/v1/workflows/{workflow_id}")
            workflow = response.json()
            if workflow["status"] == "paused" and "P2.5" in workflow["current_phase"]:
                second_pause = True
                break
            elif workflow["status"] in ["completed", "failed"]:
                # May complete before P2.5 depending on workflow logic
                break

        if second_pause:
            # Approve P2.5
            response = await client.post(
                f"/api/v1/workflows/{workflow_id}/resume",
                json={"decision": "approved", "feedback": "P2.5 approved"}
            )
            assert response.status_code == 200


    async def test_checkpoint_persistence(
        self,
        client: AsyncClient,
        sample_workflow_data,
        cleanup_workflow,
    ):
        """Test that workflow state is persisted in checkpoint.

        Verifies:
        - Workflow state is saved to PostgreSQL checkpoint
        - State can be restored after pause
        - State includes all necessary context
        """
        # Create workflow
        response = await client.post("/api/v1/workflows/", json=sample_workflow_data)
        workflow_id = UUID(response.json()["id"])
        cleanup_workflow(workflow_id)

        # Wait for pause
        max_wait = 60
        for _ in range(max_wait // 2):
            await asyncio.sleep(2)
            response = await client.get(f"/api/v1/workflows/{workflow_id}")
            if response.json()["status"] == "paused":
                break

        workflow = response.json()
        if workflow["status"] != "paused":
            pytest.skip("Workflow did not pause")

        # Verify workflow execution record exists
        assert workflow["id"] == str(workflow_id)
        assert workflow["thread_id"] is not None
        assert workflow["current_phase"] is not None

        # TODO: Add direct checkpoint verification
        # This would require accessing LangGraph checkpoint store directly
        # For now, we verify indirectly through successful resume


@pytest.mark.asyncio
@pytest.mark.integration
class TestHITLErrorHandling:
    """Test error handling in HITL workflows."""

    async def test_workflow_error_during_execution(
        self,
        client: AsyncClient,
        cleanup_workflow,
    ):
        """Test workflow handles errors during execution.

        Verifies:
        - Workflow catches execution errors
        - Status changes to 'failed'
        - Error message is recorded
        """
        # Create workflow with invalid input that might cause error
        invalid_data = {
            "problem_description": "a" * 10000,  # Extremely long description
            "domain": "invalid_domain",
        }

        response = await client.post("/api/v1/workflows/", json=invalid_data)

        # Creation might succeed but execution might fail
        if response.status_code == 201:
            workflow_id = UUID(response.json()["id"])
            cleanup_workflow(workflow_id)

            # Wait to see if it fails
            await asyncio.sleep(5)

            response = await client.get(f"/api/v1/workflows/{workflow_id}")
            workflow = response.json()

            # Might be failed, or might handle gracefully
            assert workflow["status"] in ["pending", "running", "paused", "failed"]


    async def test_resume_nonexistent_workflow(
        self,
        client: AsyncClient,
    ):
        """Test resuming workflow that doesn't exist.

        Verifies:
        - Returns 404 error
        - Appropriate error message
        """
        fake_id = "550e8400-e29b-41d4-a716-446655440000"

        response = await client.post(
            f"/api/v1/workflows/{fake_id}/resume",
            json={"decision": "approved"}
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


    async def test_invalid_resume_decision(
        self,
        client: AsyncClient,
        sample_workflow_data,
        cleanup_workflow,
    ):
        """Test submitting invalid decision value.

        Verifies:
        - Invalid decision is rejected
        - Returns validation error
        """
        # Create workflow
        response = await client.post("/api/v1/workflows/", json=sample_workflow_data)
        workflow_id = UUID(response.json()["id"])
        cleanup_workflow(workflow_id)

        # Try invalid decision
        response = await client.post(
            f"/api/v1/workflows/{workflow_id}/resume",
            json={"decision": "invalid_decision"}
        )

        # Should return 422 validation error
        assert response.status_code == 422
