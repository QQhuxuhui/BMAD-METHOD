"""BMAD Eight-Agent System - StateGraph Workflow Orchestrator.

This module implements the complete BMAD workflow using LangGraph StateGraph,
connecting all eight agent nodes with proper routing logic and checkpoint persistence.

Phase Flow:
    P0 (Orchestrator) → P1 (Algorithm/Constraint/Objective) → P1 Approval
    → P2 (Domain) → P3 (Code Implementation/Extension) → P2.5 Approval
    → P4 (Quality) → END
"""

from typing import Dict, List, Optional
from urllib.parse import quote_plus

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph
from psycopg_pool import AsyncConnectionPool

from app.core.config import settings
from app.core.langgraph.agents import (
    algorithm_expert_node,
    code_impl_expert_node,
    constraint_expert_node,
    domain_expert_node,
    extension_expert_node,
    objective_expert_node,
    orchestrator_node,
    quality_expert_node,
)
from app.core.langgraph.agents.approval_nodes import (
    p1_approval_node,
    p2_conflict_node,
    p25_approval_node,
)
from app.core.langgraph.routers.phase_routers import (
    route_after_domain,
    route_after_extension,
    route_after_objective,
    route_after_orchestrator,
    route_after_p1_approval,
    route_after_p25_approval,
    route_after_quality,
    route_p2_conflict,
)
from app.core.langgraph.state import WorkflowState
from app.core.logging import logger


async def create_checkpointer() -> AsyncPostgresSaver:
    """Create PostgreSQL checkpointer for workflow state persistence.

    This function creates and configures the PostgreSQL checkpointer that
    automatically saves workflow state after each node execution.

    Returns:
        AsyncPostgresSaver: Configured checkpointer instance

    Raises:
        Exception: If connection pool creation fails in non-production environments
    """
    try:
        # Configure connection URL with proper escaping
        connection_url = (
            f"postgresql://"
            f"{quote_plus(settings.POSTGRES_USER)}:{quote_plus(settings.POSTGRES_PASSWORD)}"
            f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
        )

        # Create async connection pool
        pool = AsyncConnectionPool(
            connection_url,
            open=False,
            max_size=settings.POSTGRES_POOL_SIZE,
            kwargs={
                "autocommit": True,
                "connect_timeout": 10,
                "prepare_threshold": None,
            }
        )

        # Open the connection pool
        await pool.open()
        logger.info(
            "checkpoint_connection_pool_created",
            host=settings.POSTGRES_HOST,
            database=settings.POSTGRES_DB,
            max_size=settings.POSTGRES_POOL_SIZE
        )

        # Create and configure checkpointer
        checkpointer = AsyncPostgresSaver(pool)
        await checkpointer.setup()  # Create necessary tables

        logger.info("checkpoint_setup_completed")
        return checkpointer

    except Exception as e:
        logger.error("checkpoint_setup_failed", error=str(e))
        # In production, we might want to degrade gracefully
        if settings.ENVIRONMENT.value == "production":
            logger.warning("continuing_without_checkpoint", environment="production")
            raise Exception("Checkpoint setup failed in production")
        raise e


def add_all_nodes(workflow: StateGraph) -> StateGraph:
    """Add all eight agent nodes and approval checkpoints to the StateGraph.

    Args:
        workflow: StateGraph instance to add nodes to

    Returns:
        StateGraph: Workflow instance with all nodes added
    """
    # Phase 0: Orchestrator
    workflow.add_node("orchestrator", orchestrator_node)

    # Phase 1: Algorithm, Constraint, Objective
    workflow.add_node("algorithm", algorithm_expert_node)
    workflow.add_node("constraint", constraint_expert_node)
    workflow.add_node("objective", objective_expert_node)

    # Phase 2: Domain
    workflow.add_node("domain", domain_expert_node)

    # Phase 3: Code Implementation, Extension
    workflow.add_node("code_impl", code_impl_expert_node)
    workflow.add_node("extension", extension_expert_node)

    # Phase 4: Quality
    workflow.add_node("quality", quality_expert_node)

    # Approval Checkpoints (HITL placeholders)
    workflow.add_node("p1_approval", p1_approval_node)
    workflow.add_node("p2_conflict", p2_conflict_node)
    workflow.add_node("p25_approval", p25_approval_node)

    logger.info("workflow_nodes_added", node_count=11)  # 8 agents + 3 approvals
    return workflow


def add_all_edges(workflow: StateGraph) -> StateGraph:
    """Add all sequential and conditional edges to the StateGraph.

    This method configures the complete workflow flow including:
    - Entry point
    - Sequential edges within phases
    - Conditional edges between phases

    Args:
        workflow: StateGraph instance to add edges to

    Returns:
        StateGraph: Workflow instance with all edges configured
    """
    # Set entry point (Phase 0 starts here)
    workflow.set_entry_point("orchestrator")

    # === Sequential Edges (within phases) ===

    # Phase 0 → Phase 1
    workflow.add_edge("orchestrator", "algorithm")

    # Phase 1: Algorithm → Constraint → Objective
    workflow.add_edge("algorithm", "constraint")
    workflow.add_edge("constraint", "objective")

    # Phase 2 → Phase 3
    workflow.add_edge("domain", "code_impl")
    workflow.add_edge("code_impl", "extension")

    # Phase 4 → END
    workflow.add_edge("quality", END)

    # === Conditional Edges (between phases) ===

    # Phase 0 Orchestrator → Phase 1 Algorithm
    workflow.add_conditional_edges(
        "orchestrator",
        route_after_orchestrator,
        {"algorithm": "algorithm"}
    )

    # Phase 1 Objective → P1 Approval
    workflow.add_conditional_edges(
        "objective",
        route_after_objective,
        {"p1_approval": "p1_approval"}
    )

    # P1 Approval → Phase 2 Domain or back to Algorithm
    workflow.add_conditional_edges(
        "p1_approval",
        route_after_p1_approval,
        {
            "approved": "domain",
            "rejected": "algorithm",
            "__end__": END
        }
    )

    # Phase 2 Domain → Phase 3 Code Implementation or P2 Conflict
    workflow.add_conditional_edges(
        "domain",
        route_after_domain,
        {
            "code_impl": "code_impl",
            "p2_conflict": "p2_conflict"
        }
    )

    # P2 Conflict → Code Implementation or END
    workflow.add_conditional_edges(
        "p2_conflict",
        route_p2_conflict,
        {
            "code_impl": "code_impl",
            "__end__": END
        }
    )

    # Phase 3 Extension → P2.5 Approval
    workflow.add_conditional_edges(
        "extension",
        route_after_extension,
        {"p25_approval": "p25_approval"}
    )

    # P2.5 Approval → Phase 4 Quality or back to Code Implementation
    workflow.add_conditional_edges(
        "p25_approval",
        route_after_p25_approval,
        {
            "approved": "quality",
            "rejected": "code_impl",
            "__end__": END
        }
    )

    # Phase 4 Quality → END
    workflow.add_conditional_edges(
        "quality",
        route_after_quality,
        {"__end__": END}
    )

    logger.info("workflow_edges_configured", sequential_edges=7, conditional_edges=7)
    return workflow


async def create_bmad_workflow(
    config_path: Optional[str] = None
) -> CompiledStateGraph:
    """Create the complete BMAD workflow with all agents and routing.

    This function creates and compiles the full BMAD workflow including:
    - All eight agent nodes
    - Sequential and conditional routing logic
    - PostgreSQL checkpoint persistence
    - Error handling and logging

    Args:
        config_path: Optional path to YAML configuration file (future use)

    Returns:
        CompiledStateGraph: Ready-to-use BMAD workflow

    Raises:
        Exception: If workflow creation fails
    """
    try:
        logger.info("bmad_workflow_creation_started")

        # Create StateGraph instance with WorkflowState schema
        workflow = StateGraph(WorkflowState)

        # Add all agent nodes
        workflow = add_all_nodes(workflow)

        # Add all edges (sequential and conditional)
        workflow = add_all_edges(workflow)

        # Create and configure checkpointer
        checkpointer = await create_checkpointer()

        # Compile the workflow with checkpointer
        app = workflow.compile(
            checkpointer=checkpointer,
            name="BMAD Eight-Agent Workflow"
        )

        logger.info(
            "bmad_workflow_created_successfully",
            name="BMAD Eight-Agent Workflow",
            has_checkpoint=True,
            node_count=8
        )

        return app

    except Exception as e:
        logger.error("bmad_workflow_creation_failed", error=str(e))
        raise Exception(f"Failed to create BMAD workflow: {str(e)}")


async def get_workflow_state(
    app: CompiledStateGraph,
    thread_id: str
) -> Dict:
    """Get current workflow state from checkpoint.

    Args:
        app: Compiled workflow instance
        thread_id: Thread identifier for the workflow

    Returns:
        Dict: Current workflow state
    """
    try:
        config = {"configurable": {"thread_id": thread_id}}
        state_snapshot = await app.aget_state(config)

        if state_snapshot.values:
            return state_snapshot.values
        else:
            logger.warning("no_workflow_state_found", thread_id=thread_id)
            return {}

    except Exception as e:
        logger.error("get_workflow_state_failed", thread_id=thread_id, error=str(e))
        return {}


async def run_workflow(
    problem_description: str,
    domain: Optional[str] = None,
    constraints: Optional[List[str]] = None,
    thread_id: Optional[str] = None
) -> WorkflowState:
    """Execute the BMAD workflow with the given input.

    This is a convenience function that combines workflow creation and execution
    in a single call for simple use cases.

    Args:
        problem_description: Description of the problem to solve
        domain: Optional domain context
        constraints: Optional list of constraint conditions
        thread_id: Unique thread identifier for checkpoint tracking

    Returns:
        WorkflowState: Final workflow state with all results
    """
    # Import here to avoid circular imports
    from app.core.langgraph.executor import run_workflow as execute_workflow

    return await execute_workflow(
        problem_description=problem_description,
        domain=domain,
        constraints=constraints,
        thread_id=thread_id
    )


# Backward compatibility alias
create_bmad_state_graph = create_bmad_workflow