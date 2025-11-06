"""CRUD operations for workflow-related models."""

import uuid
from typing import List, Optional
from datetime import datetime, UTC

from sqlmodel import Session, select
from sqlalchemy.exc import SQLAlchemyError

from app.core.logging import logger
from app.services.database import database_service
from app.models.workflow_execution import WorkflowExecution
from app.models.agent_execution import AgentExecution
from app.models.human_approval import HumanApproval


class WorkflowCRUD:
    """CRUD operations for WorkflowExecution model.

    Provides low-level database operations for workflow executions.
    """

    def __init__(self):
        """Initialize CRUD service with database connection."""
        self.db_service = database_service

    def create(self, workflow: WorkflowExecution) -> WorkflowExecution:
        """Create a new workflow execution.

        Args:
            workflow: WorkflowExecution instance to create

        Returns:
            WorkflowExecution: The created workflow with assigned ID

        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            with Session(self.db_service.engine) as session:
                session.add(workflow)
                session.commit()
                session.refresh(workflow)
                logger.info("workflow_execution_created", workflow_id=str(workflow.id))
                return workflow
        except SQLAlchemyError as e:
            logger.error("workflow_execution_create_failed", error=str(e))
            raise

    def get(self, workflow_id: uuid.UUID) -> Optional[WorkflowExecution]:
        """Get a workflow execution by ID.

        Args:
            workflow_id: UUID of the workflow to retrieve

        Returns:
            Optional[WorkflowExecution]: The workflow if found, None otherwise
        """
        with Session(self.db_service.engine) as session:
            return session.get(WorkflowExecution, workflow_id)

    def get_by_thread_id(self, thread_id: str) -> Optional[WorkflowExecution]:
        """Get a workflow execution by thread ID.

        Args:
            thread_id: Thread ID of the workflow to retrieve

        Returns:
            Optional[WorkflowExecution]: The workflow if found, None otherwise
        """
        with Session(self.db_service.engine) as session:
            statement = select(WorkflowExecution).where(WorkflowExecution.thread_id == thread_id)
            return session.exec(statement).first()

    def update(self, workflow: WorkflowExecution) -> WorkflowExecution:
        """Update an existing workflow execution.

        Args:
            workflow: WorkflowExecution instance with updated values

        Returns:
            WorkflowExecution: The updated workflow

        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            with Session(self.db_service.engine) as session:
                session.add(workflow)
                session.commit()
                session.refresh(workflow)
                logger.info("workflow_execution_updated", workflow_id=str(workflow.id))
                return workflow
        except SQLAlchemyError as e:
            logger.error("workflow_execution_update_failed", error=str(e), workflow_id=str(workflow.id))
            raise

    def delete(self, workflow_id: uuid.UUID) -> bool:
        """Delete a workflow execution.

        Args:
            workflow_id: UUID of the workflow to delete

        Returns:
            bool: True if deletion was successful, False if workflow not found

        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            with Session(self.db_service.engine) as session:
                workflow = session.get(WorkflowExecution, workflow_id)
                if not workflow:
                    return False

                session.delete(workflow)
                session.commit()
                logger.info("workflow_execution_deleted", workflow_id=str(workflow_id))
                return True
        except SQLAlchemyError as e:
            logger.error("workflow_execution_delete_failed", error=str(e), workflow_id=str(workflow_id))
            raise

    def list_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> List[WorkflowExecution]:
        """List workflow executions for a specific user.

        Args:
            user_id: User ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[WorkflowExecution]: List of workflow executions
        """
        with Session(self.db_service.engine) as session:
            statement = (
                select(WorkflowExecution)
                .where(WorkflowExecution.user_id == user_id)
                .order_by(WorkflowExecution.created_at.desc())
                .offset(skip)
                .limit(limit)
            )
            return session.exec(statement).all()

    def list_by_status(
        self,
        status: str,
        skip: int = 0,
        limit: int = 20,
    ) -> List[WorkflowExecution]:
        """List workflow executions by status.

        Args:
            status: Status to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[WorkflowExecution]: List of workflow executions
        """
        with Session(self.db_service.engine) as session:
            statement = (
                select(WorkflowExecution)
                .where(WorkflowExecution.status == status)
                .order_by(WorkflowExecution.created_at.desc())
                .offset(skip)
                .limit(limit)
            )
            return session.exec(statement).all()


class AgentExecutionCRUD:
    """CRUD operations for AgentExecution model.

    Provides low-level database operations for agent executions.
    """

    def __init__(self):
        """Initialize CRUD service with database connection."""
        self.db_service = database_service

    def create(self, agent_execution: AgentExecution) -> AgentExecution:
        """Create a new agent execution.

        Args:
            agent_execution: AgentExecution instance to create

        Returns:
            AgentExecution: The created agent execution with assigned ID

        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            with Session(self.db_service.engine) as session:
                session.add(agent_execution)
                session.commit()
                session.refresh(agent_execution)
                logger.info("agent_execution_created", agent_execution_id=str(agent_execution.id))
                return agent_execution
        except SQLAlchemyError as e:
            logger.error("agent_execution_create_failed", error=str(e))
            raise

    def get(self, agent_execution_id: uuid.UUID) -> Optional[AgentExecution]:
        """Get an agent execution by ID.

        Args:
            agent_execution_id: UUID of the agent execution to retrieve

        Returns:
            Optional[AgentExecution]: The agent execution if found, None otherwise
        """
        with Session(self.db_service.engine) as session:
            return session.get(AgentExecution, agent_execution_id)

    def list_by_workflow(
        self,
        workflow_id: uuid.UUID,
    ) -> List[AgentExecution]:
        """List agent executions for a specific workflow.

        Args:
            workflow_id: Workflow ID to filter by

        Returns:
            List[AgentExecution]: List of agent executions
        """
        with Session(self.db_service.engine) as session:
            statement = (
                select(AgentExecution)
                .where(AgentExecution.workflow_id == workflow_id)
                .order_by(AgentExecution.started_at)
            )
            return session.exec(statement).all()

    def update(self, agent_execution: AgentExecution) -> AgentExecution:
        """Update an existing agent execution.

        Args:
            agent_execution: AgentExecution instance with updated values

        Returns:
            AgentExecution: The updated agent execution

        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            with Session(self.db_service.engine) as session:
                session.add(agent_execution)
                session.commit()
                session.refresh(agent_execution)
                logger.info("agent_execution_updated", agent_execution_id=str(agent_execution.id))
                return agent_execution
        except SQLAlchemyError as e:
            logger.error("agent_execution_update_failed", error=str(e))
            raise


class HumanApprovalCRUD:
    """CRUD operations for HumanApproval model.

    Provides low-level database operations for human approvals.
    """

    def __init__(self):
        """Initialize CRUD service with database connection."""
        self.db_service = database_service

    def create(self, approval: HumanApproval) -> HumanApproval:
        """Create a new human approval.

        Args:
            approval: HumanApproval instance to create

        Returns:
            HumanApproval: The created approval with assigned ID

        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            with Session(self.db_service.engine) as session:
                session.add(approval)
                session.commit()
                session.refresh(approval)
                logger.info("human_approval_created", approval_id=str(approval.id))
                return approval
        except SQLAlchemyError as e:
            logger.error("human_approval_create_failed", error=str(e))
            raise

    def get(self, approval_id: uuid.UUID) -> Optional[HumanApproval]:
        """Get a human approval by ID.

        Args:
            approval_id: UUID of the approval to retrieve

        Returns:
            Optional[HumanApproval]: The approval if found, None otherwise
        """
        with Session(self.db_service.engine) as session:
            return session.get(HumanApproval, approval_id)

    def list_by_workflow(
        self,
        workflow_id: uuid.UUID,
    ) -> List[HumanApproval]:
        """List human approvals for a specific workflow.

        Args:
            workflow_id: Workflow ID to filter by

        Returns:
            List[HumanApproval]: List of human approvals
        """
        with Session(self.db_service.engine) as session:
            statement = (
                select(HumanApproval)
                .where(HumanApproval.workflow_id == workflow_id)
                .order_by(HumanApproval.created_at)
            )
            return session.exec(statement).all()

    def get_pending_approval(self, workflow_id: uuid.UUID) -> Optional[HumanApproval]:
        """Get the latest pending approval for a workflow.

        Args:
            workflow_id: Workflow ID to search for

        Returns:
            Optional[HumanApproval]: The pending approval if found, None otherwise
        """
        with Session(self.db_service.engine) as session:
            statement = (
                select(HumanApproval)
                .where(
                    HumanApproval.workflow_id == workflow_id,
                    HumanApproval.decision == None  # noqa: E711
                )
                .order_by(HumanApproval.created_at.desc())
            )
            return session.exec(statement).first()

    def update(self, approval: HumanApproval) -> HumanApproval:
        """Update an existing human approval.

        Args:
            approval: HumanApproval instance with updated values

        Returns:
            HumanApproval: The updated approval

        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            with Session(self.db_service.engine) as session:
                session.add(approval)
                session.commit()
                session.refresh(approval)
                logger.info("human_approval_updated", approval_id=str(approval.id))
                return approval
        except SQLAlchemyError as e:
            logger.error("human_approval_update_failed", error=str(e))
            raise


# Create singleton instances
workflow_crud = WorkflowCRUD()
agent_execution_crud = AgentExecutionCRUD()
human_approval_crud = HumanApprovalCRUD()
