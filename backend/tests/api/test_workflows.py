"""Comprehensive tests for workflow API endpoints.

Tests cover all workflow management operations including:
- Creating workflows
- Retrieving workflow status
- Listing workflows with filters
- Resuming paused workflows (HITL)
- Cancelling workflows
- SSE streaming
- Concurrent access
- Error scenarios
"""

import asyncio
import json
import sys
import uuid
from datetime import datetime, UTC
from pathlib import Path
from typing import Dict, Any

import pytest
from httpx import AsyncClient
from sqlmodel import Session

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from app.models.workflow_execution import WorkflowExecution
from app.models.human_approval import HumanApproval
from app.models.user import User


class TestCreateWorkflow:
    """Test suite for POST /api/v1/workflows endpoint."""

    @pytest.mark.asyncio
    async def test_create_workflow_success(
        self,
        client: AsyncClient,
        test_user: User,
        sample_workflow_data: Dict[str, Any],
    ):
        """Test successful workflow creation."""
        response = await client.post(
            "/api/v1/workflows/",
            json=sample_workflow_data
        )

        assert response.status_code == 201
        data = response.json()

        # Verify response structure
        assert "id" in data
        assert "thread_id" in data
        assert data["status"] == "pending"
        assert data["current_phase"] == "P0"
        assert data["input_data"] == sample_workflow_data
        assert data["output_data"] is None
        assert data["total_tokens"] == 0
        assert data["total_cost"] == 0.0

    @pytest.mark.asyncio
    async def test_create_workflow_minimal_data(
        self,
        client: AsyncClient,
        test_user: User,
    ):
        """Test workflow creation with minimal required data."""
        minimal_data = {
            "problem_description": "这是一个简单的优化问题，需要找到最优解决方案"  # 22 chars - meets min 10 requirement
        }

        response = await client.post(
            "/api/v1/workflows/",
            json=minimal_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data["input_data"]["problem_description"] == "这是一个简单的优化问题，需要找到最优解决方案"
        assert data["input_data"]["domain"] is None
        assert data["input_data"]["constraints"] == []

    @pytest.mark.asyncio
    async def test_create_workflow_missing_required_field(
        self,
        client: AsyncClient,
    ):
        """Test workflow creation fails without required fields."""
        invalid_data = {
            "domain": "logistics"
            # Missing problem_description
        }

        response = await client.post(
            "/api/v1/workflows/",
            json=invalid_data
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_workflow_without_auth(self):
        """Test workflow creation fails without authentication."""
        from httpx import ASGITransport
        from app.main import app

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post(
                "/api/v1/workflows/",
                json={"problem_description": "这是一个测试问题"}
            )

        # FastAPI HTTPBearer returns 403 when no auth provided (not 401)
        # This is FastAPI's design choice, though HTTP standard suggests 401
        assert response.status_code == 403


class TestGetWorkflow:
    """Test suite for GET /api/v1/workflows/{id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_workflow_success(
        self,
        client: AsyncClient,
        test_user: User,
        test_db_engine,
    ):
        """Test successful workflow retrieval."""
        # Create a workflow in database
        workflow_id = uuid.uuid4()
        with Session(test_db_engine) as session:
            workflow = WorkflowExecution(
                id=workflow_id,
                user_id=test_user.id,
                thread_id=f"test_{workflow_id.hex[:12]}",
                status="running",
                current_phase="P1",
                input_data={"problem_description": "test"},
                output_data=None,
                total_tokens=100,
                total_cost=0.05,
            )
            session.add(workflow)
            session.commit()

        # Retrieve workflow
        response = await client.get(f"/api/v1/workflows/{workflow_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(workflow_id)
        assert data["status"] == "running"
        assert data["current_phase"] == "P1"
        assert data["total_tokens"] == 100
        assert data["total_cost"] == 0.05

    @pytest.mark.asyncio
    async def test_get_workflow_not_found(
        self,
        client: AsyncClient,
    ):
        """Test retrieving non-existent workflow."""
        non_existent_id = uuid.uuid4()
        response = await client.get(f"/api/v1/workflows/{non_existent_id}")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_workflow_access_denied(
        self,
        client: AsyncClient,
        test_db_engine,
    ):
        """Test accessing another user's workflow is denied."""
        # Create a workflow owned by a different user
        workflow_id = uuid.uuid4()
        with Session(test_db_engine) as session:
            workflow = WorkflowExecution(
                id=workflow_id,
                user_id=999,  # Different user ID
                thread_id=f"test_{workflow_id.hex[:12]}",
                status="running",
                current_phase="P1",
                input_data={"problem_description": "test"},
            )
            session.add(workflow)
            session.commit()

        # Try to retrieve workflow
        response = await client.get(f"/api/v1/workflows/{workflow_id}")

        assert response.status_code == 403
        assert "access denied" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_workflow_invalid_uuid(
        self,
        client: AsyncClient,
    ):
        """Test invalid UUID format."""
        response = await client.get("/api/v1/workflows/invalid-uuid")

        assert response.status_code == 422


class TestListWorkflows:
    """Test suite for GET /api/v1/workflows endpoint."""

    @pytest.mark.asyncio
    async def test_list_workflows_empty(
        self,
        client: AsyncClient,
    ):
        """Test listing workflows when none exist."""
        response = await client.get("/api/v1/workflows/")

        assert response.status_code == 200
        data = response.json()
        assert data["workflows"] == []
        assert data["total"] == 0
        assert data["skip"] == 0
        assert data["limit"] == 20

    @pytest.mark.asyncio
    async def test_list_workflows_with_data(
        self,
        client: AsyncClient,
        test_user: User,
        test_db_engine,
    ):
        """Test listing workflows with multiple records."""
        # Create 3 workflows
        with Session(test_db_engine) as session:
            for i in range(3):
                workflow = WorkflowExecution(
                    id=uuid.uuid4(),
                    user_id=test_user.id,
                    thread_id=f"test_{i}",
                    status="completed" if i == 0 else "running",
                    current_phase="P4" if i == 0 else "P1",
                    input_data={"problem_description": f"test {i}"},
                )
                session.add(workflow)
            session.commit()

        # List all workflows
        response = await client.get("/api/v1/workflows/")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["workflows"]) == 3

    @pytest.mark.asyncio
    async def test_list_workflows_with_status_filter(
        self,
        client: AsyncClient,
        test_user: User,
        test_db_engine,
    ):
        """Test listing workflows filtered by status."""
        # Create workflows with different statuses
        with Session(test_db_engine) as session:
            for status in ["pending", "running", "completed"]:
                workflow = WorkflowExecution(
                    id=uuid.uuid4(),
                    user_id=test_user.id,
                    thread_id=f"test_{status}",
                    status=status,
                    current_phase="P0",
                    input_data={"problem_description": f"test {status}"},
                )
                session.add(workflow)
            session.commit()

        # Filter by status
        response = await client.get("/api/v1/workflows/?status=running")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["workflows"][0]["status"] == "running"

    @pytest.mark.asyncio
    async def test_list_workflows_pagination(
        self,
        client: AsyncClient,
        test_user: User,
        test_db_engine,
    ):
        """Test workflow list pagination."""
        # Create 25 workflows
        with Session(test_db_engine) as session:
            for i in range(25):
                workflow = WorkflowExecution(
                    id=uuid.uuid4(),
                    user_id=test_user.id,
                    thread_id=f"test_{i}",
                    status="running",
                    current_phase="P1",
                    input_data={"problem_description": f"test {i}"},
                )
                session.add(workflow)
            session.commit()

        # First page (default limit 20)
        response = await client.get("/api/v1/workflows/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["workflows"]) == 20

        # Second page
        response = await client.get("/api/v1/workflows/?skip=20&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["workflows"]) == 5
        assert data["skip"] == 20
        assert data["limit"] == 10

    @pytest.mark.asyncio
    async def test_list_workflows_max_limit(
        self,
        client: AsyncClient,
    ):
        """Test that limit is capped at 100."""
        response = await client.get("/api/v1/workflows/?limit=200")

        # FastAPI validation rejects limit > 100, returns 422
        assert response.status_code == 422


class TestResumeWorkflow:
    """Test suite for POST /api/v1/workflows/{id}/resume endpoint."""

    @pytest.mark.asyncio
    async def test_resume_workflow_approved(
        self,
        client: AsyncClient,
        test_user: User,
        test_db_engine,
        sample_resume_data: Dict[str, Any],
        monkeypatch,
    ):
        """Test resuming a paused workflow with approval."""
        # Mock create_bmad_workflow to avoid LangGraph execution in unit tests
        from unittest.mock import AsyncMock, MagicMock
        from app.core.langgraph import workflow as langgraph_workflow_module

        async def mock_astream(*args, **kwargs):
            # Return empty async generator
            return
            yield  # This makes it a generator

        mock_workflow = MagicMock()
        mock_workflow.aget_state = AsyncMock(return_value=MagicMock(values={"test": "data"}))
        mock_workflow.astream = mock_astream

        async def mock_create_bmad_workflow():
            return mock_workflow

        monkeypatch.setattr(
            langgraph_workflow_module,
            'create_bmad_workflow',
            mock_create_bmad_workflow
        )

        # Create a paused workflow
        workflow_id = uuid.uuid4()
        with Session(test_db_engine) as session:
            workflow = WorkflowExecution(
                id=workflow_id,
                user_id=test_user.id,
                thread_id=f"test_{workflow_id.hex[:12]}",
                status="paused",
                current_phase="P1",
                input_data={"problem_description": "test"},
            )
            session.add(workflow)

            # Create pending approval
            approval = HumanApproval(
                id=uuid.uuid4(),
                workflow_id=workflow_id,
                user_id=test_user.id,
                approval_point="P1",
                context_data={"algorithm_output": {"recommended": "TSP"}},
                decision=None,
                feedback="",
            )
            session.add(approval)
            session.commit()

        # Resume workflow
        response = await client.post(
            f"/api/v1/workflows/{workflow_id}/resume",
            json=sample_resume_data
        )

        assert response.status_code == 200
        data = response.json()
        # Status should not be "paused" anymore (could be "running" or "completed" with mocked workflow)
        assert data["status"] in ["running", "completed"]

    @pytest.mark.asyncio
    async def test_resume_workflow_rejected(
        self,
        client: AsyncClient,
        test_user: User,
        test_db_engine,
    ):
        """Test resuming a workflow with rejection."""
        # Create a paused workflow
        workflow_id = uuid.uuid4()
        with Session(test_db_engine) as session:
            workflow = WorkflowExecution(
                id=workflow_id,
                user_id=test_user.id,
                thread_id=f"test_{workflow_id.hex[:12]}",
                status="paused",
                current_phase="P1",
                input_data={"problem_description": "test"},
            )
            session.add(workflow)

            approval = HumanApproval(
                id=uuid.uuid4(),
                workflow_id=workflow_id,
                user_id=test_user.id,
                approval_point="P1",
                context_data={},
                decision=None,
                feedback="",
            )
            session.add(approval)
            session.commit()

        # Resume with rejection
        reject_data = {
            "decision": "rejected",
            "feedback": "算法选择不合适",
        }
        response = await client.post(
            f"/api/v1/workflows/{workflow_id}/resume",
            json=reject_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "rejected"
        assert "算法选择不合适" in data["error_message"]

    @pytest.mark.asyncio
    async def test_resume_workflow_not_paused(
        self,
        client: AsyncClient,
        test_user: User,
        test_db_engine,
    ):
        """Test resuming a workflow that is not paused."""
        # Create a running workflow
        workflow_id = uuid.uuid4()
        with Session(test_db_engine) as session:
            workflow = WorkflowExecution(
                id=workflow_id,
                user_id=test_user.id,
                thread_id=f"test_{workflow_id.hex[:12]}",
                status="running",  # Not paused
                current_phase="P1",
                input_data={"problem_description": "test"},
            )
            session.add(workflow)
            session.commit()

        # Try to resume
        response = await client.post(
            f"/api/v1/workflows/{workflow_id}/resume",
            json={"decision": "approved"}
        )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_resume_workflow_no_pending_approval(
        self,
        client: AsyncClient,
        test_user: User,
        test_db_engine,
    ):
        """Test resuming a workflow without pending approval."""
        # Create a paused workflow without approval
        workflow_id = uuid.uuid4()
        with Session(test_db_engine) as session:
            workflow = WorkflowExecution(
                id=workflow_id,
                user_id=test_user.id,
                thread_id=f"test_{workflow_id.hex[:12]}",
                status="paused",
                current_phase="P1",
                input_data={"problem_description": "test"},
            )
            session.add(workflow)
            session.commit()

        # Try to resume
        response = await client.post(
            f"/api/v1/workflows/{workflow_id}/resume",
            json={"decision": "approved"}
        )

        assert response.status_code == 400
        assert "no pending approval" in response.json()["detail"].lower()


class TestCancelWorkflow:
    """Test suite for DELETE /api/v1/workflows/{id} endpoint."""

    @pytest.mark.asyncio
    async def test_cancel_workflow_success(
        self,
        client: AsyncClient,
        test_user: User,
        test_db_engine,
    ):
        """Test successful workflow cancellation."""
        # Create a running workflow
        workflow_id = uuid.uuid4()
        with Session(test_db_engine) as session:
            workflow = WorkflowExecution(
                id=workflow_id,
                user_id=test_user.id,
                thread_id=f"test_{workflow_id.hex[:12]}",
                status="running",
                current_phase="P1",
                input_data={"problem_description": "test"},
            )
            session.add(workflow)
            session.commit()

        # Cancel workflow
        response = await client.delete(f"/api/v1/workflows/{workflow_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"
        assert "cancelled by user" in data["error_message"].lower()
        assert data["completed_at"] is not None

    @pytest.mark.asyncio
    async def test_cancel_paused_workflow(
        self,
        client: AsyncClient,
        test_user: User,
        test_db_engine,
    ):
        """Test cancelling a paused workflow."""
        workflow_id = uuid.uuid4()
        with Session(test_db_engine) as session:
            workflow = WorkflowExecution(
                id=workflow_id,
                user_id=test_user.id,
                thread_id=f"test_{workflow_id.hex[:12]}",
                status="paused",
                current_phase="P1",
                input_data={"problem_description": "test"},
            )
            session.add(workflow)
            session.commit()

        response = await client.delete(f"/api/v1/workflows/{workflow_id}")

        assert response.status_code == 200
        assert response.json()["status"] == "cancelled"

    @pytest.mark.asyncio
    async def test_cancel_completed_workflow(
        self,
        client: AsyncClient,
        test_user: User,
        test_db_engine,
    ):
        """Test cancelling an already completed workflow fails."""
        workflow_id = uuid.uuid4()
        with Session(test_db_engine) as session:
            workflow = WorkflowExecution(
                id=workflow_id,
                user_id=test_user.id,
                thread_id=f"test_{workflow_id.hex[:12]}",
                status="completed",
                current_phase="P4",
                input_data={"problem_description": "test"},
            )
            session.add(workflow)
            session.commit()

        response = await client.delete(f"/api/v1/workflows/{workflow_id}")

        assert response.status_code == 400


class TestStreamWorkflow:
    """Test suite for GET /api/v1/workflows/{id}/stream endpoint."""

    @pytest.mark.asyncio
    async def test_stream_workflow_initial_event(
        self,
        client: AsyncClient,
        test_user: User,
        test_db_engine,
    ):
        """Test SSE stream sends initial workflow event."""
        # Create a workflow
        workflow_id = uuid.uuid4()
        with Session(test_db_engine) as session:
            workflow = WorkflowExecution(
                id=workflow_id,
                user_id=test_user.id,
                thread_id=f"test_{workflow_id.hex[:12]}",
                status="running",
                current_phase="P0",
                input_data={"problem_description": "test"},
            )
            session.add(workflow)
            session.commit()

        # Stream workflow
        async with client.stream("GET", f"/api/v1/workflows/{workflow_id}/stream") as response:
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

            # Read first event
            first_chunk = None
            async for chunk in response.aiter_text():
                if chunk.strip():
                    first_chunk = chunk
                    break

            assert first_chunk is not None
            # Parse SSE format: "data: {json}\n\n"
            if first_chunk.startswith("data: "):
                event_json = first_chunk[6:].strip()
                event = json.loads(event_json)
                assert event["event_type"] == "workflow_start"
                assert event["data"]["workflow_id"] == str(workflow_id)
                assert event["data"]["status"] == "running"

    @pytest.mark.asyncio
    async def test_stream_workflow_not_found(
        self,
        client: AsyncClient,
    ):
        """Test streaming a non-existent workflow."""
        non_existent_id = uuid.uuid4()
        response = await client.get(f"/api/v1/workflows/{non_existent_id}/stream")

        assert response.status_code == 404


class TestConcurrentAccess:
    """Test suite for concurrent workflow operations."""

    @pytest.mark.asyncio
    async def test_concurrent_workflow_creation(
        self,
        client: AsyncClient,
        sample_workflow_data: Dict[str, Any],
    ):
        """Test creating multiple workflows concurrently."""
        # Create 5 workflows concurrently
        tasks = []
        for i in range(5):
            data = sample_workflow_data.copy()
            data["problem_description"] = f"这是一个并发测试的优化问题，编号是{i}号"  # Min 10 chars required
            tasks.append(client.post("/api/v1/workflows/", json=data))

        responses = await asyncio.gather(*tasks)

        # All should succeed
        assert all(r.status_code == 201 for r in responses)

        # All should have unique IDs
        workflow_ids = [r.json()["id"] for r in responses]
        assert len(workflow_ids) == len(set(workflow_ids))

    @pytest.mark.asyncio
    async def test_concurrent_workflow_reads(
        self,
        client: AsyncClient,
        test_user: User,
        test_db_engine,
    ):
        """Test reading the same workflow concurrently."""
        # Create a workflow
        workflow_id = uuid.uuid4()
        with Session(test_db_engine) as session:
            workflow = WorkflowExecution(
                id=workflow_id,
                user_id=test_user.id,
                thread_id=f"test_{workflow_id.hex[:12]}",
                status="running",
                current_phase="P1",
                input_data={"problem_description": "test"},
            )
            session.add(workflow)
            session.commit()

        # Read concurrently
        tasks = [
            client.get(f"/api/v1/workflows/{workflow_id}")
            for _ in range(10)
        ]
        responses = await asyncio.gather(*tasks)

        # All should succeed
        assert all(r.status_code == 200 for r in responses)

        # All should return the same data
        data = [r.json() for r in responses]
        assert all(d["id"] == str(workflow_id) for d in data)


class TestErrorScenarios:
    """Test suite for error handling."""

    @pytest.mark.asyncio
    async def test_invalid_json_body(
        self,
        client: AsyncClient,
    ):
        """Test sending invalid JSON."""
        response = await client.post(
            "/api/v1/workflows/",
            content="invalid json",
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_invalid_decision_value(
        self,
        client: AsyncClient,
        test_user: User,
        test_db_engine,
    ):
        """Test resuming with invalid decision value."""
        workflow_id = uuid.uuid4()
        with Session(test_db_engine) as session:
            workflow = WorkflowExecution(
                id=workflow_id,
                user_id=test_user.id,
                thread_id=f"test_{workflow_id.hex[:12]}",
                status="paused",
                current_phase="P1",
                input_data={"problem_description": "test"},
            )
            session.add(workflow)

            approval = HumanApproval(
                id=uuid.uuid4(),
                workflow_id=workflow_id,
                user_id=test_user.id,
                approval_point="P1",
                context_data={},
                decision=None,
                feedback="",
            )
            session.add(approval)
            session.commit()

        # Invalid decision value
        response = await client.post(
            f"/api/v1/workflows/{workflow_id}/resume",
            json={"decision": "invalid_decision"}
        )

        # Should validate and reject
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_extremely_large_payload(
        self,
        client: AsyncClient,
    ):
        """Test handling extremely large request payload."""
        # Create a large constraints list
        large_data = {
            "problem_description": "test",
            "constraints": ["constraint" for _ in range(10000)]
        }

        response = await client.post(
            "/api/v1/workflows/",
            json=large_data
        )

        # Should either succeed or return meaningful error
        assert response.status_code in [201, 413, 422]


class TestHITLWorkflow:
    """Test suite for complete HITL workflow scenarios."""

    @pytest.mark.asyncio
    async def test_complete_hitl_workflow(
        self,
        client: AsyncClient,
        test_user: User,
        test_db_engine,
        sample_workflow_data: Dict[str, Any],
        monkeypatch,
    ):
        """Test complete HITL flow: create → pause → resume → complete."""
        # Mock create_bmad_workflow to avoid LangGraph execution in unit tests
        from unittest.mock import AsyncMock, MagicMock
        from app.core.langgraph import workflow as langgraph_workflow_module

        async def mock_astream(*args, **kwargs):
            # Return empty async generator
            return
            yield  # This makes it a generator

        mock_workflow = MagicMock()
        mock_workflow.aget_state = AsyncMock(return_value=MagicMock(values={"test": "data"}))
        mock_workflow.astream = mock_astream

        async def mock_create_bmad_workflow():
            return mock_workflow

        monkeypatch.setattr(
            langgraph_workflow_module,
            'create_bmad_workflow',
            mock_create_bmad_workflow
        )

        # Step 1: Create workflow
        response = await client.post(
            "/api/v1/workflows/",
            json=sample_workflow_data
        )
        assert response.status_code == 201
        workflow_id = response.json()["id"]

        # Step 2: Simulate workflow reaching HITL point (manually update status)
        with Session(test_db_engine) as session:
            workflow = session.get(WorkflowExecution, uuid.UUID(workflow_id))
            workflow.status = "paused"
            workflow.current_phase = "P1"

            # Create approval request
            approval = HumanApproval(
                id=uuid.uuid4(),
                workflow_id=uuid.UUID(workflow_id),
                user_id=test_user.id,
                approval_point="P1",
                context_data={"algorithm_output": {"recommended": "TSP"}},
                decision=None,
                feedback="",
            )
            session.add(approval)
            session.commit()

        # Step 3: Verify workflow is paused
        response = await client.get(f"/api/v1/workflows/{workflow_id}")
        assert response.status_code == 200
        assert response.json()["status"] == "paused"

        # Step 4: Resume workflow with approval
        resume_data = {
            "decision": "approved",
            "feedback": "Looks good"
        }
        response = await client.post(
            f"/api/v1/workflows/{workflow_id}/resume",
            json=resume_data
        )
        assert response.status_code == 200
        # Status should not be "paused" anymore (could be "running" or "completed" with mocked workflow)
        assert response.json()["status"] in ["running", "completed"]

        # Step 5: Verify approval was recorded
        with Session(test_db_engine) as session:
            approval = session.query(HumanApproval).filter(
                HumanApproval.workflow_id == uuid.UUID(workflow_id)
            ).first()
            assert approval.decision == "approved"
            assert approval.feedback == "Looks good"
            assert approval.decided_at is not None

    @pytest.mark.asyncio
    async def test_hitl_workflow_rejection(
        self,
        client: AsyncClient,
        test_user: User,
        test_db_engine,
        sample_workflow_data: Dict[str, Any],
    ):
        """Test HITL workflow rejection path."""
        # Create and pause workflow
        response = await client.post(
            "/api/v1/workflows/",
            json=sample_workflow_data
        )
        workflow_id = response.json()["id"]

        with Session(test_db_engine) as session:
            workflow = session.get(WorkflowExecution, uuid.UUID(workflow_id))
            workflow.status = "paused"
            workflow.current_phase = "P1"

            approval = HumanApproval(
                id=uuid.uuid4(),
                workflow_id=uuid.UUID(workflow_id),
                user_id=test_user.id,
                approval_point="P1",
                context_data={},
                decision=None,
                feedback="",
            )
            session.add(approval)
            session.commit()

        # Reject workflow
        reject_data = {
            "decision": "rejected",
            "feedback": "算法不适合这个场景"
        }
        response = await client.post(
            f"/api/v1/workflows/{workflow_id}/resume",
            json=reject_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "rejected"
        assert data["completed_at"] is not None
        assert "算法不适合这个场景" in data["error_message"]
