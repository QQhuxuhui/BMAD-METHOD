"""Agent execution model for tracking individual agent performance within workflows."""

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
    from app.models.workflow_execution import WorkflowExecution


class AgentExecutionBase(BaseModel):
    """Base model for AgentExecution with common fields."""

    agent_name: str = Field(description="Name of the agent (orchestrator/algorithm/constraint/objective)")
    input_data: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON), description="Input data provided to agent")
    output_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON), description="Output data from agent")
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Agent execution start time")
    completed_at: Optional[datetime] = Field(default=None, description="Agent execution completion time")
    duration_ms: int = Field(default=0, description="Execution duration in milliseconds")
    token_count: int = Field(default=0, description="Tokens consumed by this agent")
    model_used: str = Field(description="LLM model used by this agent")
    status: str = Field(description="Execution status (success/failed/skipped)")
    error_message: Optional[str] = Field(default=None, description="Error message if execution failed")


class AgentExecution(AgentExecutionBase, table=True):
    """Database model for agent execution tracking."""

    __tablename__ = "agent_executions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="Unique agent execution ID")
    workflow_id: uuid.UUID = Field(foreign_key="workflow_executions.id", description="Associated workflow execution")

    # Relationships
    workflow: "WorkflowExecution" = Relationship(back_populates="agent_executions", sa_relationship_kwargs={"foreign_keys": "[AgentExecution.workflow_id]"})


class AgentExecutionCreate(SQLModel):
    """Schema for creating agent execution record."""

    workflow_id: uuid.UUID = Field(description="Associated workflow execution ID")
    agent_name: str = Field(description="Name of the agent")
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Input data provided to agent")
    model_used: str = Field(description="LLM model used by this agent")


class AgentExecutionRead(BaseModel):
    """Schema for reading agent execution data."""

    id: uuid.UUID
    workflow_id: uuid.UUID
    agent_name: str
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: int
    token_count: int
    model_used: str
    status: str
    error_message: Optional[str] = None


class AgentExecutionUpdate(SQLModel):
    """Schema for updating agent execution."""

    output_data: Optional[Dict[str, Any]] = None
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    token_count: Optional[int] = None
    status: Optional[str] = None
    error_message: Optional[str] = None


# Create indexes for better query performance
__table_args__ = (
    Index("idx_agent_workflow_id", "workflow_id"),
    Index("idx_agent_name", "agent_name"),
    Index("idx_agent_status", "status"),
    Index("idx_agent_started_at", "started_at"),
)