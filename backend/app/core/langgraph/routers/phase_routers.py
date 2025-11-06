"""Phase routing logic for BMAD workflow.

This module defines conditional routing functions that determine the flow
between phases based on the current state and approval decisions.

Phase Flow:
    P0 (Orchestrator) → P1 (Algorithm/Constraint/Objective)
    P1 → P1 Approval → P2 (Domain)
    P2 → P2.5 (Optional Conflict Resolution) → P3 (Code Implementation/Extension)
    P3 → P2.5 Approval (Code Review) → P4 (Quality)
    P4 → END
"""

from typing import Literal

from app.core.langgraph.state import WorkflowState


def route_after_orchestrator(state: WorkflowState) -> Literal['algorithm']:
    """Route from Orchestrator (P0) to Algorithm Expert (P1).

    Args:
        state: Current workflow state

    Returns:
        Next node name: always 'algorithm'
    """
    # Always proceed to Phase 1 (Algorithm Expert)
    return 'algorithm'


def route_after_objective(state: WorkflowState) -> Literal['p1_approval']:
    """Route from Objective Expert to P1 approval checkpoint.

    After all P1 agents (Algorithm, Constraint, Objective) complete,
    we enter P1 approval checkpoint where user confirms algorithm selection.

    Args:
        state: Current workflow state

    Returns:
        Next node name: always 'p1_approval'
    """
    return 'p1_approval'


def route_after_p1_approval(state: WorkflowState) -> Literal['domain', 'algorithm', '__end__']:
    """Route after P1 approval checkpoint.

    Based on user's approval decision:
    - approved: Continue to P2 (Domain Expert)
    - rejected: Go back to P1 (Algorithm Expert) to regenerate
    - pending: Interrupt workflow (return __end__ to pause)

    Args:
        state: Current workflow state

    Returns:
        Next node name based on approval decision
    """
    if state.get('pending_approval', False):
        # Workflow is paused, waiting for user input
        return '__end__'

    approval_decision = state.get('approval_decision')

    if approval_decision == 'approved':
        # User approved, continue to Phase 2
        return 'domain'
    elif approval_decision == 'rejected':
        # User rejected, regenerate algorithm
        return 'algorithm'
    else:
        # No decision yet, interrupt and wait
        return '__end__'


def route_after_domain(state: WorkflowState) -> Literal['p2_conflict', 'code_impl']:
    """Route from Domain Expert (P2).

    Check if there's a conflict that needs resolution (P2 checkpoint).
    For now, we auto-proceed to P3. In future, conflict detection logic
    can be added here.

    Args:
        state: Current workflow state

    Returns:
        Next node name: 'p2_conflict' if conflicts detected, else 'code_impl'
    """
    # TODO: Add conflict detection logic
    # For now, always proceed to Code Implementation
    return 'code_impl'


def route_after_extension(state: WorkflowState) -> Literal['p25_approval']:
    """Route from Extension Expert to P2.5 approval checkpoint.

    After Code Implementation and Extension Expert complete,
    we enter P2.5 approval for code review.

    Args:
        state: Current workflow state

    Returns:
        Next node name: always 'p25_approval'
    """
    return 'p25_approval'


def route_after_p25_approval(state: WorkflowState) -> Literal['quality', 'code_impl', '__end__']:
    """Route after P2.5 approval checkpoint (code review).

    Based on user's code review decision:
    - approved: Continue to P4 (Quality Expert)
    - rejected: Go back to P3 (Code Implementation) to regenerate
    - pending: Interrupt workflow

    Args:
        state: Current workflow state

    Returns:
        Next node name based on approval decision
    """
    if state.get('pending_approval', False):
        return '__end__'

    approval_decision = state.get('approval_decision')

    if approval_decision == 'approved':
        # Code approved, proceed to quality assessment
        return 'quality'
    elif approval_decision == 'rejected':
        # Code rejected, regenerate
        return 'code_impl'
    else:
        # No decision yet, interrupt
        return '__end__'


def route_after_quality(state: WorkflowState) -> Literal['__end__']:
    """Route after Quality Expert (P4).

    Quality Expert is the final phase, so we always end the workflow.

    Args:
        state: Current workflow state

    Returns:
        Always returns '__end__' to complete workflow
    """
    # Workflow complete
    return '__end__'


def route_p2_conflict(state: WorkflowState) -> Literal['code_impl', '__end__']:
    """Route after P2 conflict resolution.

    If conflicts are resolved, continue to P3.
    If user needs to intervene, interrupt workflow.

    Args:
        state: Current workflow state

    Returns:
        Next node name based on conflict resolution
    """
    if state.get('pending_approval', False):
        return '__end__'

    # Conflicts resolved, proceed to code implementation
    return 'code_impl'
