"""Workflow API endpoints for creating and managing BMAD workflows."""

import uuid
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    BackgroundTasks,
)
from fastapi.security import HTTPBearer

from app.api.v1.auth import get_current_user
from app.core.logging import logger
from app.models.user import User
from app.schemas.workflow import (
    CreateWorkflowRequest,
    WorkflowResponse,
    WorkflowListResponse,
    ResumeWorkflowRequest,
)
from app.services.workflow_service import workflow_service

router = APIRouter()
security = HTTPBearer()


@router.post("/", response_model=WorkflowResponse, status_code=201)
async def create_workflow(
    request: CreateWorkflowRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
):
    """Create a new workflow execution.

    Creates a new BMAD workflow to solve an optimization problem.
    The workflow will be executed asynchronously in the background.

    Args:
        request: Workflow creation request with problem description and constraints
        background_tasks: FastAPI background tasks for async execution
        current_user: Current authenticated user

    Returns:
        WorkflowResponse: Created workflow execution details

    Raises:
        HTTPException: If workflow creation fails
    """
    try:
        workflow = await workflow_service.create_workflow(
            user_id=current_user.id,
            problem_description=request.problem_description,
            domain=request.domain,
            constraints=request.constraints,
            background_tasks=background_tasks,
        )

        logger.info(
            "workflow_created_via_api",
            workflow_id=str(workflow.id),
            user_id=current_user.id,
        )

        return WorkflowResponse(
            id=workflow.id,
            thread_id=workflow.thread_id,
            status=workflow.status,
            current_phase=workflow.current_phase,
            input_data=workflow.input_data,
            output_data=workflow.output_data,
            created_at=workflow.created_at,
            completed_at=workflow.completed_at,
            error_message=workflow.error_message,
            total_tokens=workflow.total_tokens,
            total_cost=workflow.total_cost,
        )

    except Exception as e:
        logger.error(
            "workflow_creation_api_error",
            error=str(e),
            user_id=current_user.id,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create workflow: {str(e)}"
        )


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
):
    """Get workflow execution details by ID.

    Args:
        workflow_id: UUID of the workflow to retrieve
        current_user: Current authenticated user

    Returns:
        WorkflowResponse: Workflow execution details

    Raises:
        HTTPException: If workflow not found or access denied
    """
    workflow = await workflow_service.get_workflow(workflow_id)

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # Check if user has access to this workflow
    if workflow.user_id != current_user.id:
        logger.warning(
            "unauthorized_workflow_access",
            workflow_id=str(workflow_id),
            user_id=current_user.id,
            owner_id=workflow.user_id,
        )
        raise HTTPException(status_code=403, detail="Access denied")

    return WorkflowResponse(
        id=workflow.id,
        thread_id=workflow.thread_id,
        status=workflow.status,
        current_phase=workflow.current_phase,
        input_data=workflow.input_data,
        output_data=workflow.output_data,
        created_at=workflow.created_at,
        completed_at=workflow.completed_at,
        error_message=workflow.error_message,
        total_tokens=workflow.total_tokens,
        total_cost=workflow.total_cost,
    )


@router.get("/", response_model=WorkflowListResponse)
async def list_workflows(
    status: Optional[str] = Query(
        None,
        description="Filter by status (pending/running/paused/completed/failed/cancelled)"
    ),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    current_user: User = Depends(get_current_user),
):
    """List workflow executions for the current user.

    Supports pagination and filtering by status.

    Args:
        status: Optional status filter
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return (max 100)
        current_user: Current authenticated user

    Returns:
        WorkflowListResponse: List of workflow executions with pagination metadata
    """
    workflows = await workflow_service.list_workflows(
        user_id=current_user.id,
        status_filter=status,
        skip=skip,
        limit=limit,
    )

    # Convert to response models
    workflow_responses = [
        WorkflowResponse(
            id=w.id,
            thread_id=w.thread_id,
            status=w.status,
            current_phase=w.current_phase,
            input_data=w.input_data,
            output_data=w.output_data,
            created_at=w.created_at,
            completed_at=w.completed_at,
            error_message=w.error_message,
            total_tokens=w.total_tokens,
            total_cost=w.total_cost,
        )
        for w in workflows
    ]

    return WorkflowListResponse(
        workflows=workflow_responses,
        total=len(workflows),  # TODO: Add count query for accurate total
        skip=skip,
        limit=limit,
    )


@router.post("/{workflow_id}/resume", response_model=WorkflowResponse)
async def resume_workflow(
    workflow_id: uuid.UUID,
    request: ResumeWorkflowRequest,
    current_user: User = Depends(get_current_user),
):
    """Resume a paused workflow after human approval.

    Used to provide feedback and decision for HITL (Human-in-the-Loop) approval points.

    Args:
        workflow_id: UUID of the workflow to resume
        request: Resume request with user decision and feedback
        current_user: Current authenticated user

    Returns:
        WorkflowResponse: Updated workflow execution details

    Raises:
        HTTPException: If workflow not found, access denied, or cannot be resumed
    """
    # First check if workflow exists and user has access
    workflow = await workflow_service.get_workflow(workflow_id)

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    if workflow.user_id != current_user.id:
        logger.warning(
            "unauthorized_workflow_resume",
            workflow_id=str(workflow_id),
            user_id=current_user.id,
            owner_id=workflow.user_id,
        )
        raise HTTPException(status_code=403, detail="Access denied")

    # Resume the workflow
    try:
        updated_workflow = await workflow_service.resume_workflow(
            workflow_id=workflow_id,
            user_decision=request.decision,
            feedback=request.feedback,
            modified_data=request.modified_data,
        )

        logger.info(
            "workflow_resumed_via_api",
            workflow_id=str(workflow_id),
            decision=request.decision,
            user_id=current_user.id,
        )

        return WorkflowResponse(
            id=updated_workflow.id,
            thread_id=updated_workflow.thread_id,
            status=updated_workflow.status,
            current_phase=updated_workflow.current_phase,
            input_data=updated_workflow.input_data,
            output_data=updated_workflow.output_data,
            created_at=updated_workflow.created_at,
            completed_at=updated_workflow.completed_at,
            error_message=updated_workflow.error_message,
            total_tokens=updated_workflow.total_tokens,
            total_cost=updated_workflow.total_cost,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "workflow_resume_api_error",
            error=str(e),
            workflow_id=str(workflow_id),
            user_id=current_user.id,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to resume workflow: {str(e)}"
        )


@router.delete("/{workflow_id}", response_model=WorkflowResponse)
async def cancel_workflow(
    workflow_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
):
    """Cancel a running or paused workflow.

    Args:
        workflow_id: UUID of the workflow to cancel
        current_user: Current authenticated user

    Returns:
        WorkflowResponse: Updated workflow execution details

    Raises:
        HTTPException: If workflow not found, access denied, or cannot be cancelled
    """
    # First check if workflow exists and user has access
    workflow = await workflow_service.get_workflow(workflow_id)

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    if workflow.user_id != current_user.id:
        logger.warning(
            "unauthorized_workflow_cancel",
            workflow_id=str(workflow_id),
            user_id=current_user.id,
            owner_id=workflow.user_id,
        )
        raise HTTPException(status_code=403, detail="Access denied")

    # Cancel the workflow
    try:
        updated_workflow = await workflow_service.cancel_workflow(workflow_id)

        logger.info(
            "workflow_cancelled_via_api",
            workflow_id=str(workflow_id),
            user_id=current_user.id,
        )

        return WorkflowResponse(
            id=updated_workflow.id,
            thread_id=updated_workflow.thread_id,
            status=updated_workflow.status,
            current_phase=updated_workflow.current_phase,
            input_data=updated_workflow.input_data,
            output_data=updated_workflow.output_data,
            created_at=updated_workflow.created_at,
            completed_at=updated_workflow.completed_at,
            error_message=updated_workflow.error_message,
            total_tokens=updated_workflow.total_tokens,
            total_cost=updated_workflow.total_cost,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "workflow_cancel_api_error",
            error=str(e),
            workflow_id=str(workflow_id),
            user_id=current_user.id,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel workflow: {str(e)}"
        )
