"""Workflow service for managing BMAD workflow executions."""

import uuid
from datetime import datetime, UTC
from typing import List, Optional, Dict, Any

from fastapi import BackgroundTasks, HTTPException
from sqlmodel import Session, select, and_
from sqlalchemy.exc import SQLAlchemyError

from app.core.logging import logger
from app.services.database import database_service
from app.models.workflow_execution import (
    WorkflowExecution,
    WorkflowExecutionCreate,
    WorkflowExecutionUpdate,
)
from app.models.agent_execution import (
    AgentExecution,
    AgentExecutionCreate,
)
from app.models.human_approval import (
    HumanApproval,
    HumanApprovalCreate,
    HumanApprovalUpdate,
)


class WorkflowService:
    """Service class for workflow execution operations.

    This service handles workflow lifecycle management including:
    - Creating and initializing workflows
    - Managing workflow state transitions
    - Handling HITL (Human-in-the-Loop) approvals
    - Querying workflow status and history
    """

    def __init__(self):
        """Initialize workflow service with database connection."""
        self.db_service = database_service

    async def create_workflow(
        self,
        user_id: int,
        problem_description: str,
        domain: Optional[str] = None,
        constraints: Optional[List[str]] = None,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> WorkflowExecution:
        """Create a new workflow execution.

        Args:
            user_id: ID of the user initiating the workflow
            problem_description: Description of the problem to solve
            domain: Optional application domain (e.g., "logistics", "scheduling")
            constraints: Optional list of constraints
            background_tasks: Optional FastAPI background tasks for async execution

        Returns:
            WorkflowExecution: The created workflow execution record

        Raises:
            HTTPException: If workflow creation fails
        """
        try:
            # Generate unique thread_id for LangGraph checkpoint
            thread_id = f"workflow_{uuid.uuid4().hex[:12]}_{int(datetime.now(UTC).timestamp())}"

            # Prepare input data
            input_data = {
                "problem_description": problem_description,
                "domain": domain,
                "constraints": constraints or [],
            }

            # Create workflow execution record
            with Session(self.db_service.engine) as session:
                workflow = WorkflowExecution(
                    user_id=user_id,
                    thread_id=thread_id,
                    status="pending",
                    current_phase="P0",
                    input_data=input_data,
                    output_data=None,
                    completed_at=None,
                    error_message=None,
                    total_tokens=0,
                    total_cost=0.0,
                )

                session.add(workflow)
                session.commit()
                session.refresh(workflow)

                logger.info(
                    "workflow_created",
                    workflow_id=str(workflow.id),
                    thread_id=thread_id,
                    user_id=user_id,
                )

                # TODO: Add background task to execute workflow asynchronously
                # if background_tasks:
                #     background_tasks.add_task(
                #         self._execute_workflow_async,
                #         workflow.id,
                #         thread_id
                #     )

                return workflow

        except SQLAlchemyError as e:
            logger.error("workflow_creation_failed", error=str(e), user_id=user_id)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create workflow: {str(e)}"
            )

    async def get_workflow(self, workflow_id: uuid.UUID) -> Optional[WorkflowExecution]:
        """Get a workflow execution by ID.

        Args:
            workflow_id: UUID of the workflow to retrieve

        Returns:
            Optional[WorkflowExecution]: The workflow if found, None otherwise
        """
        with Session(self.db_service.engine) as session:
            workflow = session.get(WorkflowExecution, workflow_id)
            return workflow

    async def list_workflows(
        self,
        user_id: Optional[int] = None,
        status_filter: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[WorkflowExecution]:
        """List workflow executions with optional filtering.

        Args:
            user_id: Optional user ID to filter by
            status_filter: Optional status to filter by (pending/running/paused/completed/failed)
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return (max 100)

        Returns:
            List[WorkflowExecution]: List of workflow executions
        """
        # Limit max page size to 100
        limit = min(limit, 100)

        with Session(self.db_service.engine) as session:
            # Build query with optional filters
            statement = select(WorkflowExecution)

            if user_id is not None:
                statement = statement.where(WorkflowExecution.user_id == user_id)

            if status_filter is not None:
                statement = statement.where(WorkflowExecution.status == status_filter)

            # Order by creation time (newest first) and apply pagination
            statement = statement.order_by(WorkflowExecution.created_at.desc())
            statement = statement.offset(skip).limit(limit)

            workflows = session.exec(statement).all()
            return workflows

    async def cancel_workflow(self, workflow_id: uuid.UUID) -> WorkflowExecution:
        """Cancel a running or paused workflow.

        Args:
            workflow_id: UUID of the workflow to cancel

        Returns:
            WorkflowExecution: The updated workflow execution

        Raises:
            HTTPException: If workflow not found or cannot be cancelled
        """
        with Session(self.db_service.engine) as session:
            workflow = session.get(WorkflowExecution, workflow_id)

            if not workflow:
                raise HTTPException(status_code=404, detail="Workflow not found")

            if workflow.status in ["completed", "failed", "cancelled"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot cancel workflow with status: {workflow.status}"
                )

            workflow.status = "cancelled"
            workflow.completed_at = datetime.now(UTC)
            workflow.error_message = "Workflow cancelled by user"

            session.add(workflow)
            session.commit()
            session.refresh(workflow)

            logger.info("workflow_cancelled", workflow_id=str(workflow_id))

            return workflow

    async def resume_workflow(
        self,
        workflow_id: uuid.UUID,
        user_decision: str,
        feedback: str = "",
        modified_data: Optional[Dict[str, Any]] = None,
    ) -> WorkflowExecution:
        """Resume a paused workflow after human approval.

        Args:
            workflow_id: UUID of the workflow to resume
            user_decision: User decision (approved/rejected/modified)
            feedback: Optional user feedback or comments
            modified_data: Optional modified data if decision was 'modified'

        Returns:
            WorkflowExecution: The updated workflow execution

        Raises:
            HTTPException: If workflow not found, not paused, or no pending approval
        """
        with Session(self.db_service.engine) as session:
            workflow = session.get(WorkflowExecution, workflow_id)

            if not workflow:
                raise HTTPException(status_code=404, detail="Workflow not found")

            if workflow.status != "paused":
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot resume workflow with status: {workflow.status}"
                )

            # Find the pending approval
            statement = select(HumanApproval).where(
                and_(
                    HumanApproval.workflow_id == workflow_id,
                    HumanApproval.decision == None  # noqa: E711
                )
            ).order_by(HumanApproval.created_at.desc())

            approval = session.exec(statement).first()

            if not approval:
                raise HTTPException(
                    status_code=400,
                    detail="No pending approval found for this workflow"
                )

            # Update the approval record
            approval.decision = user_decision
            approval.feedback = feedback
            approval.modified_data = modified_data
            approval.decided_at = datetime.now(UTC)

            # Update workflow status
            if user_decision == "rejected":
                workflow.status = "rejected"
                workflow.completed_at = datetime.now(UTC)
                workflow.error_message = f"Rejected at {approval.approval_point}: {feedback}"
            else:
                workflow.status = "running"
                # TODO: Resume LangGraph workflow execution from checkpoint

            session.add(approval)
            session.add(workflow)
            session.commit()
            session.refresh(workflow)

            logger.info(
                "workflow_resumed",
                workflow_id=str(workflow_id),
                decision=user_decision,
                approval_point=approval.approval_point,
            )

            return workflow

    async def update_workflow_status(
        self,
        workflow_id: uuid.UUID,
        status: str,
        current_phase: Optional[str] = None,
        output_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        total_tokens: Optional[int] = None,
        total_cost: Optional[float] = None,
    ) -> WorkflowExecution:
        """Update workflow execution status and metrics.

        This is an internal method used during workflow execution.

        Args:
            workflow_id: UUID of the workflow to update
            status: New workflow status
            current_phase: Optional current phase
            output_data: Optional output data
            error_message: Optional error message
            total_tokens: Optional total tokens consumed
            total_cost: Optional total cost incurred

        Returns:
            WorkflowExecution: The updated workflow execution

        Raises:
            HTTPException: If workflow not found
        """
        with Session(self.db_service.engine) as session:
            workflow = session.get(WorkflowExecution, workflow_id)

            if not workflow:
                raise HTTPException(status_code=404, detail="Workflow not found")

            workflow.status = status

            if current_phase is not None:
                workflow.current_phase = current_phase

            if output_data is not None:
                workflow.output_data = output_data

            if error_message is not None:
                workflow.error_message = error_message

            if total_tokens is not None:
                workflow.total_tokens = total_tokens

            if total_cost is not None:
                workflow.total_cost = total_cost

            if status in ["completed", "failed", "cancelled", "rejected"]:
                workflow.completed_at = datetime.now(UTC)

            session.add(workflow)
            session.commit()
            session.refresh(workflow)

            return workflow


# Create a singleton instance
workflow_service = WorkflowService()
