"""Workflow service for managing BMAD workflow executions."""

import uuid
import asyncio
import json
from datetime import datetime, UTC
from typing import List, Optional, Dict, Any, AsyncGenerator

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
from app.services.workflow_crud import agent_execution_crud, human_approval_crud


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

                # Add background task to execute workflow asynchronously
                if background_tasks:
                    background_tasks.add_task(
                        self._execute_workflow_async,
                        workflow.id,
                        thread_id,
                        input_data
                    )

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

            session.add(approval)
            session.commit()
            session.refresh(approval)

            # Update workflow status based on decision
            if user_decision == "rejected":
                workflow.status = "rejected"
                workflow.completed_at = datetime.now(UTC)
                workflow.error_message = f"Rejected at {approval.approval_point}: {feedback}"

                session.add(workflow)
                session.commit()
                session.refresh(workflow)

                logger.info(
                    "workflow_rejected",
                    workflow_id=str(workflow_id),
                    approval_point=approval.approval_point,
                )

                return workflow
            else:
                # Update to running status
                workflow.status = "running"
                session.add(workflow)
                session.commit()
                session.refresh(workflow)

                logger.info(
                    "workflow_resuming",
                    workflow_id=str(workflow_id),
                    decision=user_decision,
                    approval_point=approval.approval_point,
                )

        # Resume LangGraph workflow execution from checkpoint
        # This runs outside the session context to avoid blocking
        try:
            from app.core.langgraph.workflow import create_bmad_workflow

            # Create workflow instance
            bmad_workflow = await create_bmad_workflow()

            # Configure with original thread_id
            config = {"configurable": {"thread_id": workflow.thread_id}}

            # Prepare resume input with user decision
            resume_input = {
                'decision': user_decision,
                'feedback': feedback,
                'modified_data': modified_data,
            }

            logger.info(
                "workflow_resume_from_checkpoint",
                workflow_id=str(workflow_id),
                thread_id=workflow.thread_id,
            )

            # Get current state to verify checkpoint exists
            current_state = await bmad_workflow.aget_state(config)
            if not current_state:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to load workflow checkpoint"
                )

            # Resume execution from checkpoint with user's decision
            total_tokens = workflow.total_tokens
            total_cost = workflow.total_cost

            async for event in bmad_workflow.astream(resume_input, config):
                logger.debug(
                    "workflow_resume_event",
                    workflow_id=str(workflow_id),
                    event_type=type(event).__name__,
                )

                # Process events similar to _execute_workflow_async
                if isinstance(event, dict):
                    # Update current phase if changed
                    if "current_phase" in event:
                        await self.update_workflow_status(
                            workflow_id, "running", current_phase=event["current_phase"]
                        )

                    # Track token usage
                    if "token_count" in event:
                        total_tokens += event.get("token_count", 0)
                    if "cost" in event:
                        total_cost += event.get("cost", 0.0)

                    # Check for another HITL interrupt
                    if event.get("pending_approval"):
                        approval_point = event.get("approval_point", "unknown")
                        context_data = event.get("context_data", {})

                        # Create new HumanApproval record
                        with Session(self.db_service.engine) as session:
                            new_approval = HumanApprovalCreate(
                                workflow_id=workflow_id,
                                user_id=workflow.user_id,
                                approval_point=approval_point,
                                context_data=context_data,
                            )
                            human_approval_crud.create(new_approval)

                        # Update workflow to paused
                        await self.update_workflow_status(
                            workflow_id,
                            "paused",
                            current_phase=f"{approval_point}_Approval",
                            total_tokens=total_tokens,
                            total_cost=total_cost,
                        )

                        logger.info(
                            "workflow_paused_again",
                            workflow_id=str(workflow_id),
                            approval_point=approval_point,
                        )
                        return workflow

                    # Record agent execution if present
                    if "agent_name" in event and event.get("output_data"):
                        agent_execution = AgentExecutionCreate(
                            workflow_id=workflow_id,
                            agent_name=event["agent_name"],
                            input_data=event.get("input_data", {}),
                            output_data=event.get("output_data", {}),
                            status="completed",
                            duration_ms=event.get("duration_ms", 0),
                            token_count=event.get("token_count", 0),
                            cost=event.get("cost", 0.0),
                        )
                        agent_execution_crud.create(agent_execution)

            # Workflow completed successfully
            final_state = await bmad_workflow.aget_state(config)
            output_data = final_state.values if final_state else {}

            await self.update_workflow_status(
                workflow_id,
                "completed",
                current_phase="P4_Completed",
                output_data=output_data,
                total_tokens=total_tokens,
                total_cost=total_cost,
            )

            logger.info(
                "workflow_resumed_and_completed",
                workflow_id=str(workflow_id),
            )

        except Exception as e:
            logger.error(
                "workflow_resume_failed",
                workflow_id=str(workflow_id),
                error=str(e),
                exc_info=True,
            )

            # Update workflow to failed
            await self.update_workflow_status(
                workflow_id, "failed", error_message=f"Resume failed: {str(e)}"
            )

            raise HTTPException(
                status_code=500,
                detail=f"Failed to resume workflow: {str(e)}"
            )

        # Return updated workflow
        return await self.get_workflow(workflow_id)

    async def _execute_workflow_async(
        self,
        workflow_id: uuid.UUID,
        thread_id: str,
        input_data: Dict[str, Any],
    ) -> None:
        """Execute BMAD workflow asynchronously in background.

        This method runs the actual LangGraph workflow, handling:
        - Workflow state streaming
        - Agent execution recording
        - HITL interrupt detection
        - Status updates
        - Error handling

        Args:
            workflow_id: UUID of the workflow execution
            thread_id: LangGraph thread identifier
            input_data: Input data for the workflow
        """
        try:
            from app.core.langgraph.workflow import create_bmad_workflow

            logger.info(
                "workflow_execution_started",
                workflow_id=str(workflow_id),
                thread_id=thread_id,
            )

            # Update workflow status to running
            await self.update_workflow_status(workflow_id, "running", current_phase="P0")

            # Create BMAD workflow instance
            workflow = await create_bmad_workflow()

            # Prepare initial state
            initial_state = {
                "workflow_id": str(workflow_id),
                "thread_id": thread_id,
                "problem_description": input_data.get("problem_description", ""),
                "domain": input_data.get("domain"),
                "constraints": input_data.get("constraints", []),
                "user_id": None,  # Will be set from workflow record
                "errors": [],
            }

            # Get user_id from workflow record
            workflow_record = await self.get_workflow(workflow_id)
            if workflow_record:
                initial_state["user_id"] = workflow_record.user_id

            # Configure LangGraph with thread_id for checkpoint persistence
            config = {"configurable": {"thread_id": thread_id}}

            # Execute workflow with streaming
            total_tokens = 0
            total_cost = 0.0
            current_phase = "P0"

            async for event in workflow.astream(initial_state, config):
                logger.debug(
                    "workflow_event_received",
                    workflow_id=str(workflow_id),
                    event_type=type(event).__name__,
                )

                # Extract phase and state updates from event
                if isinstance(event, dict):
                    # Update current phase if changed
                    if "current_phase" in event:
                        current_phase = event["current_phase"]
                        await self.update_workflow_status(
                            workflow_id, "running", current_phase=current_phase
                        )

                    # Track token usage
                    if "token_count" in event:
                        total_tokens += event.get("token_count", 0)
                    if "cost" in event:
                        total_cost += event.get("cost", 0.0)

                    # Detect HITL interrupt
                    if event.get("pending_approval"):
                        approval_point = event.get("approval_point", "unknown")
                        context_data = event.get("context_data", {})

                        logger.info(
                            "workflow_interrupt_detected",
                            workflow_id=str(workflow_id),
                            approval_point=approval_point,
                        )

                        # Create HumanApproval record
                        if workflow_record:
                            approval = HumanApprovalCreate(
                                workflow_id=workflow_id,
                                user_id=workflow_record.user_id,
                                approval_point=approval_point,
                                context_data=context_data,
                            )
                            human_approval_crud.create(approval)

                        # Update workflow status to paused
                        await self.update_workflow_status(
                            workflow_id,
                            "paused",
                            current_phase=f"{approval_point}_Approval",
                            total_tokens=total_tokens,
                            total_cost=total_cost,
                        )

                        # Workflow will pause here until resume_workflow is called
                        logger.info(
                            "workflow_paused_for_approval",
                            workflow_id=str(workflow_id),
                            approval_point=approval_point,
                        )
                        return  # Exit background task, will resume later

                    # Record agent execution if present
                    if "agent_name" in event and event.get("output_data"):
                        agent_execution = AgentExecutionCreate(
                            workflow_id=workflow_id,
                            agent_name=event["agent_name"],
                            input_data=event.get("input_data", {}),
                            output_data=event.get("output_data", {}),
                            status="completed",
                            duration_ms=event.get("duration_ms", 0),
                            token_count=event.get("token_count", 0),
                            cost=event.get("cost", 0.0),
                        )
                        agent_execution_crud.create(agent_execution)

            # Workflow completed successfully
            # Get final state to extract output
            final_state = await workflow.aget_state(config)
            output_data = final_state.values if final_state else {}

            await self.update_workflow_status(
                workflow_id,
                "completed",
                current_phase="P4_Completed",
                output_data=output_data,
                total_tokens=total_tokens,
                total_cost=total_cost,
            )

            logger.info(
                "workflow_execution_completed",
                workflow_id=str(workflow_id),
                total_tokens=total_tokens,
                total_cost=total_cost,
            )

        except Exception as e:
            logger.error(
                "workflow_execution_failed",
                workflow_id=str(workflow_id),
                error=str(e),
                exc_info=True,
            )

            # Update workflow to failed status
            await self.update_workflow_status(
                workflow_id, "failed", error_message=str(e)
            )

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
            # NOTE: Removed session.refresh() as it causes psycopg.InterfaceError
            # "row must be included between 0 and 0" in async environment.
            # The workflow object already has the latest values after commit.

            return workflow

    async def stream_workflow(
        self,
        workflow_id: uuid.UUID,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream workflow execution progress via Server-Sent Events.

        This method generates a stream of events representing workflow progress,
        including agent execution, phase changes, and HITL interrupts.

        Args:
            workflow_id: UUID of the workflow to stream

        Yields:
            Dict[str, Any]: SSE event data

        Raises:
            HTTPException: If workflow not found
        """
        # Verify workflow exists
        workflow = await self.get_workflow(workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")

        logger.info("workflow_stream_started", workflow_id=str(workflow_id))

        try:
            # Send initial workflow status event
            yield {
                "event_type": "workflow_start",
                "data": {
                    "workflow_id": str(workflow.id),
                    "status": workflow.status,
                    "current_phase": workflow.current_phase,
                },
                "timestamp": datetime.now(UTC).isoformat(),
            }

            # TODO: Integrate with LangGraph workflow.astream()
            # For now, simulate streaming by polling workflow status
            last_status = workflow.status
            last_phase = workflow.current_phase
            last_agent_count = 0

            # Poll for updates (simulated streaming)
            max_iterations = 300  # 5 minutes max (300 * 1 second)
            for _ in range(max_iterations):
                await asyncio.sleep(1)  # Poll every second

                # Refresh workflow status
                workflow = await self.get_workflow(workflow_id)
                if not workflow:
                    break

                # Check for phase changes
                if workflow.current_phase != last_phase:
                    yield {
                        "event_type": "phase_change",
                        "phase": workflow.current_phase,
                        "data": {
                            "old_phase": last_phase,
                            "new_phase": workflow.current_phase,
                        },
                        "timestamp": datetime.now(UTC).isoformat(),
                    }
                    last_phase = workflow.current_phase

                # Check for new agent executions
                agent_executions = agent_execution_crud.list_by_workflow(workflow_id)
                if len(agent_executions) > last_agent_count:
                    # New agent execution detected
                    new_execution = agent_executions[last_agent_count]
                    yield {
                        "event_type": "agent_output",
                        "agent_name": new_execution.agent_name,
                        "data": {
                            "input_data": new_execution.input_data,
                            "output_data": new_execution.output_data,
                            "status": new_execution.status,
                            "duration_ms": new_execution.duration_ms,
                            "token_count": new_execution.token_count,
                        },
                        "timestamp": datetime.now(UTC).isoformat(),
                    }
                    last_agent_count = len(agent_executions)

                # Check for HITL interrupts
                if workflow.status == "paused":
                    pending_approval = human_approval_crud.get_pending_approval(workflow_id)
                    if pending_approval:
                        yield {
                            "event_type": "interrupt",
                            "data": {
                                "approval_point": pending_approval.approval_point,
                                "context_data": pending_approval.context_data,
                                "approval_id": str(pending_approval.id),
                            },
                            "timestamp": datetime.now(UTC).isoformat(),
                        }

                # Check for status changes
                if workflow.status != last_status:
                    yield {
                        "event_type": "status_change",
                        "data": {
                            "old_status": last_status,
                            "new_status": workflow.status,
                        },
                        "timestamp": datetime.now(UTC).isoformat(),
                    }
                    last_status = workflow.status

                # Check for completion or failure
                if workflow.status in ["completed", "failed", "cancelled", "rejected"]:
                    yield {
                        "event_type": "complete" if workflow.status == "completed" else "error",
                        "data": {
                            "status": workflow.status,
                            "output_data": workflow.output_data,
                            "error_message": workflow.error_message,
                            "total_tokens": workflow.total_tokens,
                            "total_cost": workflow.total_cost,
                        },
                        "timestamp": datetime.now(UTC).isoformat(),
                    }
                    logger.info(
                        "workflow_stream_completed",
                        workflow_id=str(workflow_id),
                        status=workflow.status,
                    )
                    break

        except Exception as e:
            logger.error(
                "workflow_stream_error",
                workflow_id=str(workflow_id),
                error=str(e),
            )
            yield {
                "event_type": "error",
                "data": {
                    "error": str(e),
                },
                "timestamp": datetime.now(UTC).isoformat(),
            }


# Create a singleton instance
workflow_service = WorkflowService()
