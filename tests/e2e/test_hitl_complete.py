"""
HITL (Human-in-the-Loop) workflow tests for Phase 1 validation.

Tests human approval points and workflow resume functionality.
"""

import asyncio
from typing import Dict

import httpx
import pytest

from tests.e2e.conftest import (
    TEST_API_PREFIX,
    assert_workflow_structure,
    wait_for_workflow_status,
)


@pytest.mark.asyncio
class TestHITLWorkflow:
    """Test suite for Human-in-the-Loop interactions."""

    @pytest.mark.timeout(180)
    async def test_hitl_approve_workflow(
        self,
        authenticated_client: httpx.AsyncClient,
        sample_problem_medium: Dict
    ):
        """Test complete HITL workflow with approval at each checkpoint."""
        # 1. Create workflow
        response = await authenticated_client.post(
            f"{TEST_API_PREFIX}/workflows/",
            json=sample_problem_medium
        )
        assert response.status_code == 201
        workflow = response.json()
        workflow_id = workflow["id"]

        print(f"\nCreated workflow: {workflow_id}")

        # 2. Wait for first HITL checkpoint (P1 - Algorithm Selection)
        try:
            workflow = await wait_for_workflow_status(
                authenticated_client,
                workflow_id,
                "paused",
                timeout=90
            )
            print(f"Reached first HITL point at phase: {workflow['current_phase']}")

            # 3. Verify we're at algorithm selection phase
            assert "P1" in workflow["current_phase"] or "algorithm" in workflow["current_phase"].lower()

            # 4. Approve and provide feedback
            response = await authenticated_client.post(
                f"{TEST_API_PREFIX}/workflows/{workflow_id}/resume",
                json={
                    "decision": "approve",
                    "feedback": "Algorithm selection looks good, proceed with implementation"
                }
            )
            assert response.status_code == 200
            print("Approved first checkpoint")

            # 5. Wait for second HITL checkpoint or completion
            try:
                workflow = await wait_for_workflow_status(
                    authenticated_client,
                    workflow_id,
                    "paused",
                    timeout=90
                )
                print(f"Reached second HITL point at phase: {workflow['current_phase']}")

                # 6. Approve second checkpoint
                response = await authenticated_client.post(
                    f"{TEST_API_PREFIX}/workflows/{workflow_id}/resume",
                    json={
                        "decision": "approve",
                        "feedback": "Code generation is acceptable"
                    }
                )
                assert response.status_code == 200
                print("Approved second checkpoint")

            except TimeoutError:
                # Workflow might complete after first approval
                print("No second checkpoint, workflow likely completing")

            # 7. Wait for final completion
            workflow = await wait_for_workflow_status(
                authenticated_client,
                workflow_id,
                "completed",
                timeout=90
            )

            # 8. Verify completion
            assert workflow["status"] == "completed"
            assert workflow["output_data"] is not None
            assert workflow["completed_at"] is not None

            print(f"Workflow completed successfully")

        except TimeoutError as e:
            # Get current status for debugging
            response = await authenticated_client.get(
                f"{TEST_API_PREFIX}/workflows/{workflow_id}"
            )
            workflow = response.json()
            pytest.fail(
                f"Workflow did not complete in time. Current status: {workflow['status']}, "
                f"phase: {workflow['current_phase']}, error: {str(e)}"
            )

    @pytest.mark.timeout(120)
    async def test_hitl_reject_workflow(
        self,
        authenticated_client: httpx.AsyncClient,
        sample_problem_simple: Dict
    ):
        """Test HITL workflow with rejection."""
        # Create workflow
        response = await authenticated_client.post(
            f"{TEST_API_PREFIX}/workflows/",
            json=sample_problem_simple
        )
        assert response.status_code == 201
        workflow_id = response.json()["id"]

        # Wait for HITL checkpoint
        try:
            workflow = await wait_for_workflow_status(
                authenticated_client,
                workflow_id,
                "paused",
                timeout=60
            )

            # Reject
            response = await authenticated_client.post(
                f"{TEST_API_PREFIX}/workflows/{workflow_id}/resume",
                json={
                    "decision": "reject",
                    "feedback": "Algorithm not suitable, please choose a different approach"
                }
            )
            assert response.status_code == 200

            # Workflow should either fail, cancel, or go back to previous phase
            await asyncio.sleep(5)

            response = await authenticated_client.get(
                f"{TEST_API_PREFIX}/workflows/{workflow_id}"
            )
            workflow = response.json()

            # Status should change after rejection
            assert workflow["status"] in ["failed", "cancelled", "paused", "running"]
            print(f"Workflow status after rejection: {workflow['status']}")

        except TimeoutError:
            pytest.skip("Workflow did not reach HITL checkpoint")

    @pytest.mark.timeout(120)
    async def test_hitl_modify_workflow(
        self,
        authenticated_client: httpx.AsyncClient,
        sample_problem_simple: Dict
    ):
        """Test HITL workflow with parameter modification."""
        # Create workflow
        response = await authenticated_client.post(
            f"{TEST_API_PREFIX}/workflows/",
            json=sample_problem_simple
        )
        assert response.status_code == 201
        workflow_id = response.json()["id"]

        # Wait for HITL checkpoint
        try:
            workflow = await wait_for_workflow_status(
                authenticated_client,
                workflow_id,
                "paused",
                timeout=60
            )

            # Modify with custom data
            response = await authenticated_client.post(
                f"{TEST_API_PREFIX}/workflows/{workflow_id}/resume",
                json={
                    "decision": "modify",
                    "feedback": "Adjusting algorithm parameters",
                    "modified_data": {
                        "algorithm": "QuickSort",
                        "optimization_level": "high"
                    }
                }
            )
            assert response.status_code == 200

            # Workflow should continue with modifications
            await asyncio.sleep(5)

            response = await authenticated_client.get(
                f"{TEST_API_PREFIX}/workflows/{workflow_id}"
            )
            workflow = response.json()

            # Should be running or completed
            assert workflow["status"] in ["running", "paused", "completed"]

        except TimeoutError:
            pytest.skip("Workflow did not reach HITL checkpoint")

    async def test_resume_non_paused_workflow(
        self,
        authenticated_client: httpx.AsyncClient,
        sample_problem_simple: Dict
    ):
        """Test that resuming a non-paused workflow returns error."""
        # Create workflow
        response = await authenticated_client.post(
            f"{TEST_API_PREFIX}/workflows/",
            json=sample_problem_simple
        )
        assert response.status_code == 201
        workflow_id = response.json()["id"]

        # Try to resume immediately (while still running)
        await asyncio.sleep(1)

        response = await authenticated_client.post(
            f"{TEST_API_PREFIX}/workflows/{workflow_id}/resume",
            json={
                "decision": "approve",
                "feedback": "test"
            }
        )

        # Should return error (400 or 409) because workflow is not paused
        assert response.status_code in [400, 409], \
            f"Expected 400 or 409, got {response.status_code}"

    @pytest.mark.timeout(120)
    async def test_multiple_approval_points(
        self,
        authenticated_client: httpx.AsyncClient,
        sample_problem_medium: Dict
    ):
        """Test workflow with multiple HITL approval points."""
        # Create workflow
        response = await authenticated_client.post(
            f"{TEST_API_PREFIX}/workflows/",
            json=sample_problem_medium
        )
        assert response.status_code == 201
        workflow_id = response.json()["id"]

        approval_count = 0
        max_approvals = 3  # Expect up to 3 approval points

        for i in range(max_approvals):
            try:
                # Wait for pause
                workflow = await wait_for_workflow_status(
                    authenticated_client,
                    workflow_id,
                    "paused",
                    timeout=60
                )

                approval_count += 1
                print(f"Approval point {approval_count} at phase: {workflow['current_phase']}")

                # Approve
                response = await authenticated_client.post(
                    f"{TEST_API_PREFIX}/workflows/{workflow_id}/resume",
                    json={
                        "decision": "approve",
                        "feedback": f"Approved at checkpoint {approval_count}"
                    }
                )
                assert response.status_code == 200

            except TimeoutError:
                # No more approval points, check if completed
                response = await authenticated_client.get(
                    f"{TEST_API_PREFIX}/workflows/{workflow_id}"
                )
                workflow = response.json()

                if workflow["status"] == "completed":
                    break
                else:
                    pytest.fail(
                        f"Workflow not completed after {approval_count} approvals. "
                        f"Status: {workflow['status']}"
                    )

        # Should have at least one approval point
        assert approval_count > 0, "No approval points encountered"
        print(f"Total approval points: {approval_count}")


@pytest.mark.asyncio
class TestConcurrentWorkflows:
    """Test concurrent workflow execution and resource isolation."""

    @pytest.mark.timeout(180)
    async def test_concurrent_workflow_execution(
        self,
        authenticated_client: httpx.AsyncClient,
        sample_problem_simple: Dict
    ):
        """Test multiple workflows can execute concurrently without interference."""
        num_workflows = 5

        # Create workflows concurrently
        print(f"\nCreating {num_workflows} concurrent workflows...")
        create_tasks = []
        for i in range(num_workflows):
            problem = sample_problem_simple.copy()
            problem["problem_description"] = f"{problem['problem_description']} (Concurrent Test {i})"
            create_tasks.append(
                authenticated_client.post(
                    f"{TEST_API_PREFIX}/workflows/",
                    json=problem
                )
            )

        responses = await asyncio.gather(*create_tasks)

        # Collect workflow IDs
        workflow_ids = []
        for response in responses:
            assert response.status_code == 201
            workflow_ids.append(response.json()["id"])

        print(f"Created {len(workflow_ids)} workflows")

        # Monitor all workflows
        await asyncio.sleep(10)  # Let them run for a bit

        # Check status of all workflows
        status_tasks = [
            authenticated_client.get(f"{TEST_API_PREFIX}/workflows/{wf_id}")
            for wf_id in workflow_ids
        ]
        status_responses = await asyncio.gather(*status_tasks)

        statuses = {}
        for response in status_responses:
            assert response.status_code == 200
            workflow = response.json()
            status = workflow["status"]
            statuses[status] = statuses.get(status, 0) + 1

        print(f"Workflow statuses: {statuses}")

        # All workflows should be in valid states
        valid_statuses = ["pending", "running", "paused", "completed", "failed"]
        for response in status_responses:
            workflow = response.json()
            assert workflow["status"] in valid_statuses

        # Verify data isolation - each workflow should have unique thread_id
        thread_ids = [r.json()["thread_id"] for r in status_responses]
        assert len(thread_ids) == len(set(thread_ids)), "Thread IDs not unique - data isolation violated"

    async def test_concurrent_hitl_approvals(
        self,
        authenticated_client: httpx.AsyncClient,
        sample_problem_simple: Dict
    ):
        """Test HITL approvals for multiple workflows don't interfere."""
        # Create 3 workflows
        workflow_ids = []
        for i in range(3):
            problem = sample_problem_simple.copy()
            problem["problem_description"] = f"{problem['problem_description']} (HITL Test {i})"
            response = await authenticated_client.post(
                f"{TEST_API_PREFIX}/workflows/",
                json=problem
            )
            assert response.status_code == 201
            workflow_ids.append(response.json()["id"])

        print(f"\nCreated {len(workflow_ids)} workflows for HITL testing")

        # Wait for at least one to pause
        await asyncio.sleep(15)

        # Check which workflows are paused
        paused_workflows = []
        for wf_id in workflow_ids:
            response = await authenticated_client.get(
                f"{TEST_API_PREFIX}/workflows/{wf_id}"
            )
            workflow = response.json()
            if workflow["status"] == "paused":
                paused_workflows.append(wf_id)

        if len(paused_workflows) == 0:
            pytest.skip("No workflows reached HITL checkpoint")

        print(f"{len(paused_workflows)} workflows paused for approval")

        # Approve paused workflows concurrently
        approval_tasks = []
        for wf_id in paused_workflows:
            approval_tasks.append(
                authenticated_client.post(
                    f"{TEST_API_PREFIX}/workflows/{wf_id}/resume",
                    json={"decision": "approve", "feedback": "Concurrent approval test"}
                )
            )

        approval_responses = await asyncio.gather(*approval_tasks)

        # All approvals should succeed
        for response in approval_responses:
            assert response.status_code == 200

        print("All approvals submitted successfully")
