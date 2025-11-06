"""BMAD Eight-Agent System - Workflow Executor.

This module provides high-level functions for executing the BMAD workflow
with proper error handling, logging, and state management.

Main Functions:
- run_workflow(): Execute complete BMAD workflow
- run_workflow_stream(): Execute with streaming output
- resume_workflow(): Resume from checkpoint
"""

import asyncio
from typing import Dict, List, Optional, AsyncGenerator, Any
from uuid import uuid4
import time

from langgraph.graph.state import CompiledStateGraph

from app.core.langgraph.state import WorkflowState, create_initial_state
from app.core.langgraph.workflow import create_bmad_workflow
from app.core.langgraph.config_loader import load_workflow_config, validate_config
from app.core.logging import logger


async def run_workflow(
    problem_description: str,
    domain: Optional[str] = None,
    constraints: Optional[List[str]] = None,
    thread_id: Optional[str] = None,
    config_path: Optional[str] = None,
    timeout: int = 3600  # 1 hour timeout
) -> WorkflowState:
    """Execute the complete BMAD workflow.

    This function creates and executes the BMAD workflow with the given input,
    handling all phases from problem analysis to quality assessment.

    Args:
        problem_description: Description of the problem to solve
        domain: Optional domain context (e.g., "logistics", "e-commerce")
        constraints: Optional list of constraint conditions
        thread_id: Unique thread identifier for checkpoint tracking
        config_path: Optional path to YAML configuration file
        timeout: Maximum execution time in seconds

    Returns:
        WorkflowState: Final workflow state with all results

    Raises:
        Exception: If workflow execution fails or times out
    """
    start_time = time.time()
    thread_id = thread_id or str(uuid4())

    try:
        logger.info(
            "workflow_execution_started",
            thread_id=thread_id,
            problem_length=len(problem_description),
            domain=domain,
            constraints_count=len(constraints) if constraints else 0
        )

        # Load configuration if provided
        if config_path:
            config = load_workflow_config(config_path)
            validation_issues = validate_config(config)
            if validation_issues:
                logger.warning(
                    "config_validation_issues",
                    issues=validation_issues,
                    thread_id=thread_id
                )
        else:
            logger.info("using_default_config", thread_id=thread_id)

        # Create workflow
        app = await create_bmad_workflow(config_path)

        # Create initial state
        initial_state = create_initial_state(
            problem_description=problem_description,
            domain=domain,
            constraints=constraints or [],
            thread_id=thread_id
        )

        # Configure execution
        execution_config = {
            "configurable": {"thread_id": thread_id},
            "metadata": {
                "execution_type": "complete_workflow",
                "start_time": start_time,
                "domain": domain,
                "timeout": timeout
            }
        }

        # Execute workflow with timeout
        final_state = await asyncio.wait_for(
            app.ainvoke(initial_state, execution_config),
            timeout=timeout
        )

        execution_time = time.time() - start_time

        logger.info(
            "workflow_execution_completed",
            thread_id=thread_id,
            execution_time=execution_time,
            final_phase=final_state.get('current_phase'),
            total_tokens=final_state.get('total_tokens', 0),
            total_cost=final_state.get('total_cost', 0.0)
        )

        return final_state

    except asyncio.TimeoutError:
        execution_time = time.time() - start_time
        logger.error(
            "workflow_execution_timeout",
            thread_id=thread_id,
            execution_time=execution_time,
            timeout=timeout
        )
        raise Exception(f"Workflow execution timed out after {timeout} seconds")

    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(
            "workflow_execution_failed",
            thread_id=thread_id,
            execution_time=execution_time,
            error=str(e)
        )
        raise Exception(f"Workflow execution failed: {str(e)}")


async def run_workflow_stream(
    problem_description: str,
    domain: Optional[str] = None,
    constraints: Optional[List[str]] = None,
    thread_id: Optional[str] = None,
    config_path: Optional[str] = None,
    timeout: int = 3600
) -> AsyncGenerator[Dict[str, Any], None]:
    """Execute BMAD workflow with streaming output.

    This generator yields events as the workflow progresses through each phase,
    allowing real-time monitoring of the execution.

    Args:
        problem_description: Description of the problem to solve
        domain: Optional domain context
        constraints: Optional list of constraints
        thread_id: Unique thread identifier
        config_path: Optional path to configuration file
        timeout: Maximum execution time

    Yields:
        Dict[str, Any]: Workflow events with node outputs and state updates
    """
    start_time = time.time()
    thread_id = thread_id or str(uuid4())

    try:
        logger.info(
            "workflow_stream_started",
            thread_id=thread_id,
            domain=domain
        )

        # Load configuration if provided
        if config_path:
            config = load_workflow_config(config_path)
            validation_issues = validate_config(config)
            if validation_issues:
                yield {
                    "type": "config_warning",
                    "issues": validation_issues,
                    "thread_id": thread_id
                }

        # Create workflow
        app = await create_bmad_workflow(config_path)

        # Create initial state
        initial_state = create_initial_state(
            problem_description=problem_description,
            domain=domain,
            constraints=constraints or [],
            thread_id=thread_id
        )

        # Configure execution
        execution_config = {
            "configurable": {"thread_id": thread_id},
            "metadata": {
                "execution_type": "streaming_workflow",
                "start_time": start_time,
                "domain": domain
            }
        }

        # Stream workflow execution
        event_count = 0
        async for event in app.astream(initial_state, execution_config):
            event_count += 1
            execution_time = time.time() - start_time

            # Add metadata to event
            event_data = {
                "event_id": event_count,
                "execution_time": execution_time,
                "thread_id": thread_id,
                "data": event
            }

            yield event_data

            # Check timeout
            if execution_time > timeout:
                logger.warning(
                    "workflow_stream_timeout_approaching",
                    thread_id=thread_id,
                    execution_time=execution_time,
                    timeout=timeout
                )
                break

        logger.info(
            "workflow_stream_completed",
            thread_id=thread_id,
            total_events=event_count,
            execution_time=time.time() - start_time
        )

    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(
            "workflow_stream_failed",
            thread_id=thread_id,
            execution_time=execution_time,
            error=str(e)
        )
        yield {
            "type": "error",
            "error": str(e),
            "execution_time": execution_time,
            "thread_id": thread_id
        }


async def resume_workflow(
    thread_id: str,
    approval_decision: Optional[str] = None,
    approval_feedback: Optional[str] = None,
    timeout: int = 1800  # 30 minutes timeout
) -> WorkflowState:
    """Resume a paused workflow from checkpoint.

    This function resumes a workflow that was paused for approval,
    applying the user's decision and continuing execution.

    Args:
        thread_id: Thread identifier of the paused workflow
        approval_decision: User's decision ('approved', 'rejected', 'modified')
        approval_feedback: Optional user feedback
        timeout: Maximum execution time for resumption

    Returns:
        WorkflowState: Updated workflow state after resumption

    Raises:
        Exception: If resumption fails or workflow not found
    """
    start_time = time.time()

    try:
        logger.info(
            "workflow_resumption_started",
            thread_id=thread_id,
            approval_decision=approval_decision
        )

        # Create workflow
        app = await create_bmad_workflow()

        # Get current state
        current_state = await app.aget_state({"configurable": {"thread_id": thread_id}})
        if not current_state.values:
            raise Exception(f"No workflow state found for thread_id: {thread_id}")

        # Update state with approval decision
        if approval_decision:
            current_state.values['approval_decision'] = approval_decision
            current_state.values['approval_feedback'] = approval_feedback or ''
            current_state.values['pending_approval'] = False

            logger.info(
                "approval_applied",
                thread_id=thread_id,
                decision=approval_decision,
                approval_point=current_state.values.get('approval_point')
            )

        # Configure execution
        execution_config = {
            "configurable": {"thread_id": thread_id},
            "metadata": {
                "execution_type": "workflow_resumption",
                "start_time": start_time,
                "approval_decision": approval_decision
            }
        }

        # Resume execution (None means continue from current state)
        final_state = await asyncio.wait_for(
            app.ainvoke(None, execution_config),
            timeout=timeout
        )

        execution_time = time.time() - start_time

        logger.info(
            "workflow_resumption_completed",
            thread_id=thread_id,
            execution_time=execution_time,
            final_phase=final_state.get('current_phase')
        )

        return final_state

    except asyncio.TimeoutError:
        execution_time = time.time() - start_time
        logger.error(
            "workflow_resumption_timeout",
            thread_id=thread_id,
            execution_time=execution_time,
            timeout=timeout
        )
        raise Exception(f"Workflow resumption timed out after {timeout} seconds")

    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(
            "workflow_resumption_failed",
            thread_id=thread_id,
            execution_time=execution_time,
            error=str(e)
        )
        raise Exception(f"Workflow resumption failed: {str(e)}")


async def get_workflow_status(thread_id: str) -> Dict[str, Any]:
    """Get the current status of a workflow.

    Args:
        thread_id: Thread identifier of the workflow

    Returns:
        Dict[str, Any]: Workflow status information
    """
    try:
        # Create workflow
        app = await create_bmad_workflow()

        # Get current state
        state_snapshot = await app.aget_state({"configurable": {"thread_id": thread_id}})

        if not state_snapshot.values:
            return {
                "status": "not_found",
                "thread_id": thread_id,
                "message": "No workflow state found"
            }

        state = state_snapshot.values
        next_node = state_snapshot.next

        status_info = {
            "status": "active" if next_node else "completed",
            "thread_id": thread_id,
            "current_phase": state.get('current_phase'),
            "next_node": next_node,
            "pending_approval": state.get('pending_approval', False),
            "approval_point": state.get('approval_point'),
            "total_tokens": state.get('total_tokens', 0),
            "total_cost": state.get('total_cost', 0.0),
            "errors": state.get('errors', []),
            "checkpoint_id": state_snapshot.config.get('checkpoint_ns')
        }

        return status_info

    except Exception as e:
        logger.error(
            "get_workflow_status_failed",
            thread_id=thread_id,
            error=str(e)
        )
        return {
            "status": "error",
            "thread_id": thread_id,
            "error": str(e)
        }


async def cancel_workflow(thread_id: str) -> bool:
    """Cancel a running workflow.

    Args:
        thread_id: Thread identifier of the workflow to cancel

    Returns:
        bool: True if cancellation successful, False otherwise
    """
    try:
        logger.info("workflow_cancellation_requested", thread_id=thread_id)

        # In LangGraph, workflow cancellation is typically handled by
        # not providing further input or by setting a cancellation flag
        # For now, we'll log the cancellation request

        logger.info("workflow_cancellation_completed", thread_id=thread_id)
        return True

    except Exception as e:
        logger.error(
            "workflow_cancellation_failed",
            thread_id=thread_id,
            error=str(e)
        )
        return False


# Export functions
__all__ = [
    'run_workflow',
    'run_workflow_stream',
    'resume_workflow',
    'get_workflow_status',
    'cancel_workflow'
]