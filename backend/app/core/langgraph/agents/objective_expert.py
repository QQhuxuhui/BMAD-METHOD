"""Objective Expert Agent Node for BMAD Workflow.

The Objective Expert is part of Phase 1 (P1), responsible for:
- Defining optimization objectives
- Identifying KPIs
- Handling multi-objective optimization
- Setting performance metrics
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
PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "objective.md"
with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
    OBJECTIVE_PROMPT = f.read()


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
    """Extract token usage from LLM response metadata."""
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

    if usage["total_tokens"] == 0:
        usage["total_tokens"] = len(response.content) // 4
        usage["output_tokens"] = usage["total_tokens"]

    return usage


async def objective_expert_node(state: WorkflowState) -> Dict[str, Any]:
    """Objective Expert agent node - Phase 1 (P1).

    Defines optimization objectives and KPIs.

    Args:
        state: Current workflow state

    Returns:
        Dict with updated state fields
    """
    logger.info(
        "objective_expert_started",
        thread_id=state.get("thread_id")
    )

    try:
        factory = ModelFactory.get_instance()
        llm = factory.get_langchain_model()

        # Extract previous outputs
        algorithm_output = state.get("algorithm_output", {})
        constraint_output = state.get("constraint_output", {})

        prompt = ChatPromptTemplate.from_messages([
            ("system", OBJECTIVE_PROMPT),
            ("human", """Problem Description: {problem_description}

Domain: {domain}

Algorithm Recommendations:
{algorithm_output}

Constraints:
{constraint_output}

Please define optimization objectives and KPIs in JSON format.""")
        ])

        chain = prompt | llm

        input_data = {
            "problem_description": state.get("problem_description", ""),
            "domain": state.get("domain", "Not specified"),
            "algorithm_output": json.dumps(algorithm_output, indent=2) if algorithm_output else "Not available",
            "constraint_output": json.dumps(constraint_output, indent=2) if constraint_output else "Not available"
        }

        logger.info("objective_expert_calling_llm", thread_id=state.get("thread_id"))

        response = await _call_llm_with_retry(chain, input_data)

        # Parse JSON response
        try:
            objective_output = json.loads(response.content)
        except json.JSONDecodeError as e:
            logger.error(
                "objective_expert_json_parse_failed",
                error=str(e),
                response=response.content[:500]
            )
            objective_output = {
                "error": "Failed to parse JSON response",
                "raw_response": response.content
            }

        usage = _extract_token_usage(response)
        tokens = usage["total_tokens"]
        cost = tokens * 0.00001

        logger.info(
            "objective_expert_completed",
            thread_id=state.get("thread_id"),
            has_objectives=bool(objective_output.get("primary_objectives")),
            tokens=tokens,
            cost=cost
        )

        return {
            "objective_output": objective_output,
            "messages": [
                SystemMessage(content=OBJECTIVE_PROMPT[:200] + "..."),
                HumanMessage(content=str(input_data)),
                response
            ],
            "total_tokens": state.get("total_tokens", 0) + tokens,
            "total_cost": state.get("total_cost", 0.0) + cost
        }

    except Exception as e:
        logger.error(
            "objective_expert_failed",
            thread_id=state.get("thread_id"),
            error=str(e),
            error_type=type(e).__name__
        )

        errors = state.get("errors", [])
        errors.append(f"Objective Expert failed: {str(e)}")

        return {
            "errors": errors,
            "retry_count": state.get("retry_count", 0) + 1
        }
