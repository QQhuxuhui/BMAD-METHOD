"""Orchestrator Agent Node for BMAD Workflow.

The Orchestrator is the first agent in Phase 0, responsible for:
- Analyzing the problem description
- Planning the overall workflow
- Assigning tasks to specialized expert agents
- Defining success criteria
"""

import json
from typing import Dict, Any
from pathlib import Path

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
import structlog

from backend.app.core.langgraph.state import WorkflowState
from backend.model_adapters.model_factory import ModelFactory

logger = structlog.get_logger(__name__)

# Load prompt template
PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "orchestrator.md"
with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
    ORCHESTRATOR_PROMPT = f.read()


async def orchestrator_node(state: WorkflowState) -> Dict[str, Any]:
    """Orchestrator agent node - Phase 0.

    Analyzes the problem, plans the workflow, and assigns tasks to expert agents.

    Args:
        state: Current workflow state

    Returns:
        Dict with updated state fields:
            - orchestrator_output: Agent's analysis and plan
            - current_phase: Set to 'P1' to proceed to next phase
            - messages: Updated with agent interaction
            - total_tokens: Updated token count
            - total_cost: Updated cost
            - errors: Any errors encountered

    Raises:
        Exception: If LLM call fails after retries
    """
    logger.info(
        "orchestrator_started",
        thread_id=state.get("thread_id"),
        problem=state.get("problem_description", "")[:100]
    )

    try:
        # Get LangChain-wrapped model from factory
        factory = ModelFactory.get_instance()
        llm = factory.get_langchain_model()  # Gets default model

        # Build prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", ORCHESTRATOR_PROMPT),
            ("human", """Problem Description: {problem_description}

Domain: {domain}

Constraints: {constraints}

Please analyze this problem and provide your orchestration plan in JSON format.""")
        ])

        # Prepare input
        chain = prompt | llm

        input_data = {
            "problem_description": state.get("problem_description", ""),
            "domain": state.get("domain", "Not specified"),
            "constraints": "\n".join(state.get("constraints", [])) or "None specified"
        }

        # Call LLM
        logger.info("orchestrator_calling_llm", thread_id=state.get("thread_id"))

        response = await chain.ainvoke(input_data)

        # Parse JSON response
        try:
            orchestrator_output = json.loads(response.content)
        except json.JSONDecodeError as e:
            logger.error(
                "orchestrator_json_parse_failed",
                error=str(e),
                response=response.content[:500]
            )
            # Fallback: wrap raw response
            orchestrator_output = {
                "error": "Failed to parse JSON response",
                "raw_response": response.content
            }

        # Update state
        logger.info(
            "orchestrator_completed",
            thread_id=state.get("thread_id"),
            has_plan=bool(orchestrator_output.get("workflow_plan"))
        )

        # TODO: Extract token usage from response metadata
        # For now, estimate based on content length
        estimated_tokens = len(response.content) // 4
        estimated_cost = estimated_tokens * 0.00001  # Rough estimate

        return {
            "orchestrator_output": orchestrator_output,
            "current_phase": "P1",
            "messages": [
                SystemMessage(content=ORCHESTRATOR_PROMPT[:200] + "..."),
                HumanMessage(content=str(input_data)),
                response
            ],
            "total_tokens": state.get("total_tokens", 0) + estimated_tokens,
            "total_cost": state.get("total_cost", 0.0) + estimated_cost
        }

    except Exception as e:
        logger.error(
            "orchestrator_failed",
            thread_id=state.get("thread_id"),
            error=str(e),
            error_type=type(e).__name__
        )

        errors = state.get("errors", [])
        errors.append(f"Orchestrator failed: {str(e)}")

        return {
            "errors": errors,
            "retry_count": state.get("retry_count", 0) + 1
        }
