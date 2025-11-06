"""BMAD Eight-Agent System - Approval Node Implementations (HITL).

This module implements approval checkpoint nodes for the BMAD workflow.
These nodes serve as Human-in-the-Loop (HITL) points where the workflow
pauses to wait for user input/approval before proceeding.

Story 1.5.3 Implementation: Real HITL using LangGraph interrupt().
"""

from typing import Dict, Any, Literal
from uuid import uuid4
from datetime import datetime, UTC

from langgraph.types import interrupt

from app.core.langgraph.state import WorkflowState
from app.core.logging import logger


async def p1_approval_node(state: WorkflowState) -> Dict[str, Any]:
    """P1 Approval checkpoint after Phase 1 (Algorithm/Constraint/Objective).

    This node pauses the workflow to wait for user approval of the algorithm
    selection and approach before proceeding to Phase 2 (Domain Expert).

    Uses LangGraph's interrupt() to pause workflow execution until user provides
    approval decision via the resume API.

    Args:
        state: Current workflow state

    Returns:
        Dict[str, Any]: Updated state with approval checkpoint information
    """
    try:
        logger.info("p1_approval_node_started", thread_id=state.get('thread_id'))

        # Prepare approval context data from Phase 1 outputs
        context_data = {
            'algorithm_output': state.get('algorithm_output'),
            'constraint_output': state.get('constraint_output'),
            'objective_output': state.get('objective_output'),
            'orchestrator_output': state.get('orchestrator_output'),
        }

        # Generate unique approval ID for tracking
        approval_id = str(uuid4())

        logger.info(
            "p1_approval_interrupt_triggered",
            approval_point='P1',
            approval_id=approval_id,
            thread_id=state.get('thread_id')
        )

        # Use LangGraph interrupt() to pause workflow
        # This will save current state to checkpoint and wait for resume
        approval_response = interrupt({
            'approval_id': approval_id,
            'approval_point': 'P1',
            'context_data': context_data,
            'workflow_id': state.get('workflow_id'),
            'user_id': state.get('user_id'),
            'timestamp': datetime.now(UTC).isoformat(),
        })

        # After resume, approval_response will contain user's decision
        # Extract decision from response
        decision = approval_response.get('decision', 'approved') if approval_response else 'approved'
        feedback = approval_response.get('feedback', '') if approval_response else ''
        modified_data = approval_response.get('modified_data') if approval_response else None

        logger.info(
            "p1_approval_resumed",
            approval_point='P1',
            decision=decision,
            approval_id=approval_id,
            thread_id=state.get('thread_id')
        )

        # Return updated state based on user decision
        updated_state = {
            'pending_approval': False,
            'approval_point': 'P1',
            'approval_decision': decision,
            'approval_feedback': feedback,
            'approval_checkpoint_id': approval_id,
            'current_phase': 'P1_Approval_Completed'
        }

        # If user modified data, merge it into state
        if modified_data:
            updated_state['modified_data_p1'] = modified_data

        return updated_state

    except Exception as e:
        logger.error(
            "p1_approval_node_failed",
            error=str(e),
            thread_id=state.get('thread_id')
        )

        # Return error state
        return {
            'pending_approval': False,
            'approval_point': 'P1',
            'approval_decision': 'error',
            'approval_feedback': f'Error during P1 approval: {str(e)}',
            'errors': state.get('errors', []) + [f'P1 approval error: {str(e)}']
        }


async def p2_conflict_node(state: WorkflowState) -> Dict[str, Any]:
    """P2 Conflict resolution checkpoint after Domain Expert.

    This optional node handles conflicts that may arise during domain analysis.
    For now, this is a placeholder that always resolves conflicts automatically.

    Args:
        state: Current workflow state

    Returns:
        Dict[str, Any]: Updated state with conflict resolution information
    """
    try:
        logger.info("p2_conflict_node_started", thread_id=state.get('thread_id'))

        # In Story 1.5.2, we assume no conflicts for simplicity
        # Future versions may implement actual conflict detection

        updated_state = {
            'pending_approval': False,  # No approval needed
            'current_phase': 'P2_Conflict_Resolution',
            'conflict_resolution': 'no_conflicts_detected'
        }

        logger.info(
            "p2_conflict_node_completed",
            resolution='no_conflicts',
            thread_id=state.get('thread_id')
        )

        return updated_state

    except Exception as e:
        logger.error(
            "p2_conflict_node_failed",
            error=str(e),
            thread_id=state.get('thread_id')
        )

        return {
            'errors': state.get('errors', []) + [f'P2 conflict error: {str(e)}'],
            'conflict_resolution': 'error'
        }


async def p25_approval_node(state: WorkflowState) -> Dict[str, Any]:
    """P2.5 Approval checkpoint after Phase 3 (Code Implementation/Extension).

    This node pauses the workflow for code review and approval before
    proceeding to Phase 4 (Quality Expert).

    Uses LangGraph's interrupt() to pause workflow execution until user provides
    code review decision via the resume API.

    Args:
        state: Current workflow state

    Returns:
        Dict[str, Any]: Updated state with approval checkpoint information
    """
    try:
        logger.info("p25_approval_node_started", thread_id=state.get('thread_id'))

        # Prepare approval context data from Phase 3 outputs
        context_data = {
            'code_impl_output': state.get('code_impl_output'),
            'extension_output': state.get('extension_output'),
            'domain_output': state.get('domain_output'),
        }

        # Generate unique approval ID for tracking
        approval_id = str(uuid4())

        logger.info(
            "p25_approval_interrupt_triggered",
            approval_point='P2.5',
            approval_id=approval_id,
            thread_id=state.get('thread_id')
        )

        # Use LangGraph interrupt() to pause workflow
        # This will save current state to checkpoint and wait for resume
        approval_response = interrupt({
            'approval_id': approval_id,
            'approval_point': 'P2.5',
            'context_data': context_data,
            'workflow_id': state.get('workflow_id'),
            'user_id': state.get('user_id'),
            'timestamp': datetime.now(UTC).isoformat(),
        })

        # After resume, approval_response will contain user's decision
        # Extract decision from response
        decision = approval_response.get('decision', 'approved') if approval_response else 'approved'
        feedback = approval_response.get('feedback', '') if approval_response else ''
        modified_data = approval_response.get('modified_data') if approval_response else None

        logger.info(
            "p25_approval_resumed",
            approval_point='P2.5',
            decision=decision,
            approval_id=approval_id,
            thread_id=state.get('thread_id')
        )

        # Return updated state based on user decision
        updated_state = {
            'pending_approval': False,
            'approval_point': 'P2.5',
            'approval_decision': decision,
            'approval_feedback': feedback,
            'approval_checkpoint_id': approval_id,
            'current_phase': 'P2.5_Approval_Completed'
        }

        # If user modified data, merge it into state
        if modified_data:
            updated_state['modified_data_p25'] = modified_data

        return updated_state

    except Exception as e:
        logger.error(
            "p25_approval_node_failed",
            error=str(e),
            thread_id=state.get('thread_id')
        )

        return {
            'pending_approval': False,
            'approval_point': 'P2.5',
            'approval_decision': 'error',
            'approval_feedback': f'Error during P2.5 approval: {str(e)}',
            'errors': state.get('errors', []) + [f'P2.5 approval error: {str(e)}']
        }


# Export all approval nodes
__all__ = [
    'p1_approval_node',
    'p2_conflict_node',
    'p25_approval_node'
]