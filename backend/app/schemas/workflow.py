"""Workflow schemas for API request/response models."""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field


class CreateWorkflowRequest(BaseModel):
    """Request schema for creating a new workflow.

    Attributes:
        problem_description: Description of the optimization problem
        domain: Optional application domain (e.g., "logistics", "scheduling")
        constraints: Optional list of constraint descriptions
    """

    problem_description: str = Field(
        ...,
        description="Problem description to solve",
        min_length=10,
        max_length=5000,
    )
    domain: Optional[str] = Field(
        None,
        description="Application domain (e.g., logistics, scheduling)",
        max_length=100,
    )
    constraints: List[str] = Field(
        default_factory=list,
        description="List of constraint conditions",
        max_length=50,
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "problem_description": "优化100辆车的配送路线，最小化总行驶距离",
                "domain": "logistics",
                "constraints": ["实时交通限制", "电动车电池容量限制", "时间窗口约束"]
            }
        }
    }


class WorkflowResponse(BaseModel):
    """Response schema for workflow execution data.

    Attributes:
        id: Unique workflow execution ID
        thread_id: LangGraph thread identifier
        status: Current workflow status
        current_phase: Current workflow phase
        input_data: Input data provided to workflow
        output_data: Output data from workflow (if completed)
        created_at: Workflow creation timestamp
        completed_at: Workflow completion timestamp (if completed)
        error_message: Error message (if failed)
        total_tokens: Total tokens consumed
        total_cost: Total cost incurred
    """

    id: uuid.UUID = Field(..., description="Unique workflow execution ID")
    thread_id: str = Field(..., description="LangGraph thread identifier")
    status: str = Field(..., description="Workflow status (pending/running/paused/completed/failed/cancelled)")
    current_phase: str = Field(..., description="Current workflow phase (P0/P1/P2/P3/P4)")
    input_data: Dict[str, Any] = Field(..., description="Input data provided to workflow")
    output_data: Optional[Dict[str, Any]] = Field(None, description="Output data from workflow")
    created_at: datetime = Field(..., description="Workflow creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Workflow completion timestamp")
    error_message: Optional[str] = Field(None, description="Error message if workflow failed")
    total_tokens: int = Field(0, description="Total tokens consumed")
    total_cost: float = Field(0.0, description="Total cost incurred")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "thread_id": "workflow_abc123_1699900000",
                "status": "running",
                "current_phase": "P1",
                "input_data": {
                    "problem_description": "优化配送路线",
                    "domain": "logistics",
                    "constraints": ["时间窗口", "车辆容量"]
                },
                "output_data": None,
                "created_at": "2025-11-06T10:00:00Z",
                "completed_at": None,
                "error_message": None,
                "total_tokens": 1500,
                "total_cost": 0.025
            }
        }
    }


class ResumeWorkflowRequest(BaseModel):
    """Request schema for resuming a paused workflow.

    Attributes:
        decision: User decision (approved/rejected/modified)
        feedback: User feedback or comments
        modified_data: Modified data if decision was 'modified'
    """

    decision: str = Field(
        ...,
        description="User decision (approved/rejected/modified)",
    )
    feedback: str = Field(
        default="",
        description="User feedback or comments",
        max_length=2000,
    )
    modified_data: Optional[Dict[str, Any]] = Field(
        None,
        description="Modified data if decision was 'modified'",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "decision": "approved",
                "feedback": "Looks good, proceed with implementation",
                "modified_data": None
            }
        }
    }


class WorkflowListResponse(BaseModel):
    """Response schema for workflow list with pagination.

    Attributes:
        workflows: List of workflow executions
        total: Total number of workflows (for pagination)
        skip: Number of records skipped
        limit: Maximum number of records returned
    """

    workflows: List[WorkflowResponse] = Field(..., description="List of workflow executions")
    total: int = Field(..., description="Total number of workflows matching filters")
    skip: int = Field(..., description="Number of records skipped")
    limit: int = Field(..., description="Maximum number of records returned")


class SSEEvent(BaseModel):
    """Server-Sent Event data schema.

    Attributes:
        event_type: Type of event (agent_start/agent_output/phase_change/interrupt/complete/error)
        agent_name: Name of the agent (if applicable)
        phase: Current workflow phase (if applicable)
        data: Event data payload
        timestamp: Event timestamp
    """

    event_type: str = Field(..., description="Event type")
    agent_name: Optional[str] = Field(None, description="Agent name if applicable")
    phase: Optional[str] = Field(None, description="Workflow phase if applicable")
    data: Dict[str, Any] = Field(default_factory=dict, description="Event data payload")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")

    model_config = {
        "json_schema_extra": {
            "example": {
                "event_type": "agent_output",
                "agent_name": "algorithm",
                "phase": "P1",
                "data": {
                    "recommended_algorithms": ["TSP", "VRP"],
                    "reasoning": "基于问题特征推荐"
                },
                "timestamp": "2025-11-06T10:00:05Z"
            }
        }
    }
