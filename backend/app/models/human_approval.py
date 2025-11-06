"""Human approval model for tracking HITL (Human-in-the-Loop) decisions."""

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
    from app.models.user import User


class HumanApprovalBase(BaseModel):
    """Base model for HumanApproval with common fields."""

    approval_point: str = Field(description="Approval point in workflow (P1/P2/P2.5)")
    context_data: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON), description="Context data for approval decision")
    decision: Optional[str] = Field(default=None, description="User decision (approved/rejected/modified)")
    feedback: str = Field(default="", description="User feedback or comments")
    modified_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON), description="Modified data if decision was 'modified'")
    decided_at: Optional[datetime] = Field(default=None, description="Decision timestamp")


class HumanApproval(HumanApprovalBase, table=True):
    """Database model for human approval tracking."""

    __tablename__ = "human_approvals"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, description="Unique approval ID")
    workflow_id: uuid.UUID = Field(foreign_key="workflow_executions.id", description="Associated workflow execution")
    user_id: int = Field(foreign_key="user.id", description="User making the approval decision")

    # Relationships
    workflow: "WorkflowExecution" = Relationship(back_populates="human_approvals", sa_relationship_kwargs={"foreign_keys": "[HumanApproval.workflow_id]"})
    user: "User" = Relationship(sa_relationship_kwargs={"foreign_keys": "[HumanApproval.user_id]"})


class HumanApprovalCreate(SQLModel):
    """Schema for creating human approval record."""

    workflow_id: uuid.UUID = Field(description="Associated workflow execution ID")
    user_id: int = Field(description="User making the approval decision")
    approval_point: str = Field(description="Approval point in workflow (P1/P2/P2.5)")
    context_data: Dict[str, Any] = Field(default_factory=dict, description="Context data for approval decision")


class HumanApprovalRead(BaseModel):
    """Schema for reading human approval data."""

    id: uuid.UUID
    workflow_id: uuid.UUID
    user_id: int
    approval_point: str
    context_data: Dict[str, Any]
    decision: Optional[str] = None
    feedback: str = ""
    modified_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    decided_at: Optional[datetime] = None


class HumanApprovalUpdate(SQLModel):
    """Schema for updating human approval."""

    decision: Optional[str] = None
    feedback: Optional[str] = None
    modified_data: Optional[Dict[str, Any]] = None
    decided_at: Optional[datetime] = None


class ResumeWorkflowRequest(SQLModel):
    """Schema for resuming workflow after human approval."""

    decision: str = Field(..., description="User decision (approved/rejected/modified)")
    feedback: str = Field(default="", description="User feedback or comments")
    modified_data: Optional[Dict[str, Any]] = Field(default=None, description="Modified data if decision was 'modified'")

    class Config:
        json_schema_extra = {
            "example": {
                "decision": "approved",
                "feedback": "Looks good, proceed with implementation",
                "modified_data": None
            }
        }


# Create indexes for better query performance
__table_args__ = (
    Index("idx_approval_workflow_id", "workflow_id"),
    Index("idx_approval_user_id", "user_id"),
    Index("idx_approval_point", "approval_point"),
    Index("idx_approval_decision", "decision"),
    Index("idx_approval_created_at", "created_at"),
)