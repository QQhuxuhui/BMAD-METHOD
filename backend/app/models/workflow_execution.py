"""Workflow execution model for tracking BMAD workflow progress."""

import uuid
from datetime import datetime, UTC
from typing import Optional, Dict, Any

from sqlmodel import SQLModel, Field, Column, JSON, Relationship
from sqlalchemy import Index

from app.models.base import BaseModel
from sqlmodel import Relationship


# Forward references for type hints
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.user import User
    from app.models.agent_execution import AgentExecution
    from app.models.human_approval import HumanApproval


class WorkflowExecutionBase(BaseModel):
    """Base model for WorkflowExecution with common fields."""

    thread_id: str = Field(unique=True, index=True, description="Unique thread identifier for LangGraph")
    status: str = Field(index=True, description="Current workflow status")
    current_phase: str = Field(description="Current phase in workflow (P0/P1/P2/P3/P4)")
    input_data: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON), description="Input data for workflow")
    output_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON), description="Output data from workflow")
    completed_at: Optional[datetime] = Field(default=None, description="Workflow completion timestamp")
    error_message: Optional[str] = Field(default=None, description="Error message if workflow failed")
    total_tokens: int = Field(default=0, description="Total tokens consumed")
    total_cost: float = Field(default=0.0, description="Total cost incurred")


class WorkflowExecution(WorkflowExecutionBase, table=True):
    """Database model for workflow execution tracking."""

    __tablename__ = "workflow_executions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="Unique workflow execution ID")
    user_id: int = Field(foreign_key="user.id", description="User who initiated the workflow")

    # Relationships
    user: "User" = Relationship(sa_relationship_kwargs={"foreign_keys": "[WorkflowExecution.user_id]"})
    agent_executions: list["AgentExecution"] = Relationship(back_populates="workflow", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    human_approvals: list["HumanApproval"] = Relationship(back_populates="workflow", sa_relationship_kwargs={"cascade": "all, delete-orphan"})


class WorkflowExecutionCreate(SQLModel):
    """Schema for creating workflow execution."""

    user_id: int = Field(description="User who initiated the workflow")
    thread_id: str = Field(description="Unique thread identifier for LangGraph")
    status: str = Field(default="pending", description="Initial workflow status")
    current_phase: str = Field(default="P0", description="Initial workflow phase")
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Input data for workflow")


class WorkflowExecutionRead(BaseModel):
    """Schema for reading workflow execution data."""

    id: uuid.UUID
    user_id: int
    thread_id: str
    status: str
    current_phase: str
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    total_tokens: int = 0
    total_cost: float = 0.0


class WorkflowExecutionUpdate(SQLModel):
    """Schema for updating workflow execution."""

    status: Optional[str] = None
    current_phase: Optional[str] = None
    output_data: Optional[Dict[str, Any]] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    total_tokens: Optional[int] = None
    total_cost: Optional[float] = None


# Create indexes for better query performance
__table_args__ = (
    Index("idx_workflow_user_id", "user_id"),
    Index("idx_workflow_status", "status"),
    Index("idx_workflow_thread_id", "thread_id"),
    Index("idx_workflow_created_at", "created_at"),
)