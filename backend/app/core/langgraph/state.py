"""LangGraph WorkflowState definition for BMAD Eight-Agent System.

This module defines the state structure for the BMAD workflow, which manages
the collaboration of eight specialized agents across five phases (P0-P4).
"""

from typing import Any, Dict, List, Literal, Optional, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages


class WorkflowState(TypedDict, total=False):
    """State structure for BMAD LangGraph workflow.

    This state is shared across all agent nodes and tracks the complete
    workflow execution from problem analysis (P0) to quality assessment (P4).

    Attributes:
        # Input Data
        problem_description: Description of the problem to solve
        domain: Domain context (e.g., "logistics", "e-commerce")
        constraints: List of constraint conditions

        # Workflow Control
        current_phase: Current execution phase (P0-P4)
        thread_id: Unique thread identifier for checkpoint tracking

        # Agent Outputs (one per agent)
        orchestrator_output: Output from Orchestrator (P0)
        algorithm_output: Output from Algorithm Expert (P1)
        constraint_output: Output from Constraint Expert (P1)
        objective_output: Output from Objective Expert (P1)
        domain_output: Output from Domain Expert (P2)
        code_output: Output from Code Implementation Expert (P3)
        extension_output: Output from Extension Expert (P3)
        quality_output: Output from Quality Expert (P4)

        # LLM Interaction History
        messages: List of messages (automatically merged with add_messages)

        # Human-in-the-Loop Control
        pending_approval: Whether workflow is waiting for human approval
        approval_point: Current approval point (P1/P2/P2.5/None)
        approval_decision: User's decision (approved/rejected/modified)
        approval_feedback: User's feedback text

        # Error Handling
        errors: List of error messages during execution
        retry_count: Number of retries for current node

        # Metrics
        total_tokens: Total tokens consumed
        total_cost: Total cost in USD
    """

    # Input Data
    problem_description: str
    domain: Optional[str]
    constraints: List[str]

    # Workflow Control
    current_phase: Literal['P0', 'P1', 'P2', 'P3', 'P4']
    thread_id: str

    # Agent Outputs
    orchestrator_output: Dict[str, Any]
    algorithm_output: Dict[str, Any]
    constraint_output: Dict[str, Any]
    objective_output: Dict[str, Any]
    domain_output: Dict[str, Any]
    code_output: Dict[str, Any]
    extension_output: Dict[str, Any]
    quality_output: Dict[str, Any]

    # LLM Interaction History
    # Using add_messages reducer to automatically merge messages
    messages: list[BaseMessage]

    # HITL Control
    pending_approval: bool
    approval_point: Optional[Literal['P1', 'P2', 'P2.5']]
    approval_decision: Optional[Literal['approved', 'rejected', 'modified']]
    approval_feedback: str

    # Error Handling
    errors: List[str]
    retry_count: int

    # Metrics
    total_tokens: int
    total_cost: float


# Define reducer for messages field
# This tells LangGraph to merge new messages with existing ones
WorkflowState.__annotations__['messages'] = add_messages


def create_initial_state(
    problem_description: str,
    thread_id: str,
    domain: Optional[str] = None,
    constraints: Optional[List[str]] = None
) -> WorkflowState:
    """Create an initial workflow state.

    Args:
        problem_description: Problem to solve
        thread_id: Unique thread ID for this workflow execution
        domain: Optional domain context
        constraints: Optional list of constraints

    Returns:
        WorkflowState: Initial state ready for workflow execution
    """
    return WorkflowState(
        # Input
        problem_description=problem_description,
        domain=domain or "",
        constraints=constraints or [],

        # Control
        current_phase='P0',
        thread_id=thread_id,

        # Agent outputs (empty initially)
        orchestrator_output={},
        algorithm_output={},
        constraint_output={},
        objective_output={},
        domain_output={},
        code_output={},
        extension_output={},
        quality_output={},

        # Messages
        messages=[],

        # HITL
        pending_approval=False,
        approval_point=None,
        approval_decision=None,
        approval_feedback="",

        # Error handling
        errors=[],
        retry_count=0,

        # Metrics
        total_tokens=0,
        total_cost=0.0
    )
