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

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import structlog

from app.core.langgraph.state import WorkflowState
from model_adapters.model_factory import ModelFactory

logger = structlog.get_logger(__name__)

# Load prompt template
PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "orchestrator.md"
with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
    ORCHESTRATOR_PROMPT = f.read()


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((ConnectionError, TimeoutError)),
    reraise=True
)
async def _call_llm_with_retry(chain, input_data: Dict[str, Any]) -> AIMessage:
    """Call LLM with retry logic for transient errors."""
    return await chain.ainvoke(input_data)


def _extract_token_usage(response: AIMessage) -> Dict[str, int]:
    """Extract token usage from LLM response metadata.

    Args:
        response: AI message from LLM

    Returns:
        Dict with 'input_tokens', 'output_tokens', 'total_tokens'
    """
    usage = {
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0
    }

    if hasattr(response, 'response_metadata'):
        metadata = response.response_metadata
        if 'usage' in metadata:
            usage_data = metadata['usage']
            usage["input_tokens"] = usage_data.get('prompt_tokens', 0)
            usage["output_tokens"] = usage_data.get('completion_tokens', 0)
            usage["total_tokens"] = usage_data.get('total_tokens', 0)

    # Fallback: estimate from content length
    if usage["total_tokens"] == 0:
        usage["total_tokens"] = len(response.content) // 4
        usage["output_tokens"] = usage["total_tokens"]

    return usage


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

        # Call LLM with retry
        logger.info("orchestrator_calling_llm", thread_id=state.get("thread_id"))

        response = await _call_llm_with_retry(chain, input_data)

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

        # Extract token usage
        usage = _extract_token_usage(response)

        # Calculate cost (rough estimate: $0.01 per 1K tokens)
        tokens = usage["total_tokens"]
        cost = tokens * 0.00001

        # Update state
        logger.info(
            "orchestrator_completed",
            thread_id=state.get("thread_id"),
            has_plan=bool(orchestrator_output.get("workflow_plan")),
            tokens=tokens,
            cost=cost
        )

        return {
            "orchestrator_output": orchestrator_output,
            "current_phase": "P1",
            "messages": [
                SystemMessage(content=ORCHESTRATOR_PROMPT[:200] + "..."),
                HumanMessage(content=str(input_data)),
                response
            ],
            "total_tokens": state.get("total_tokens", 0) + tokens,
            "total_cost": state.get("total_cost", 0.0) + cost
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
