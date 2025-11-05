"""Domain Expert Agent Node for BMAD Workflow.

The Domain Expert is part of Phase 1 (P1), responsible for:
- Providing domain-specific knowledge and expertise
- Identifying best practices and industry standards
- Highlighting regulatory requirements and compliance needs
- Assessing domain-specific risks and mitigation strategies
- Offering practical implementation insights
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
PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "domain.md"
with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
    DOMAIN_PROMPT = f.read()


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


async def domain_expert_node(state: WorkflowState) -> Dict[str, Any]:
    """Domain Expert agent node - Phase 1 (P1).

    Provides domain-specific knowledge, best practices, and regulatory requirements.

    Args:
        state: Current workflow state

    Returns:
        Dict with updated state fields
    """
    logger.info(
        "domain_expert_started",
        thread_id=state.get("thread_id")
    )

    try:
        factory = ModelFactory.get_instance()
        llm = factory.get_langchain_model()

        # Extract previous outputs
        orchestrator_output = state.get("orchestrator_output", {})
        algorithm_output = state.get("algorithm_output", {})
        constraint_output = state.get("constraint_output", {})
        objective_output = state.get("objective_output", {})

        prompt = ChatPromptTemplate.from_messages([
            ("system", DOMAIN_PROMPT),
            ("human", """Problem Description: {problem_description}

Domain: {domain}

Orchestrator Analysis:
{orchestrator_output}

Algorithm Recommendations:
{algorithm_output}

Constraints:
{constraint_output}

Objectives:
{objective_output}

Please provide domain expertise and recommendations in JSON format.""")
        ])

        chain = prompt | llm

        input_data = {
            "problem_description": state.get("problem_description", ""),
            "domain": state.get("domain", "Not specified"),
            "orchestrator_output": json.dumps(orchestrator_output, indent=2) if orchestrator_output else "Not available",
            "algorithm_output": json.dumps(algorithm_output, indent=2) if algorithm_output else "Not available",
            "constraint_output": json.dumps(constraint_output, indent=2) if constraint_output else "Not available",
            "objective_output": json.dumps(objective_output, indent=2) if objective_output else "Not available"
        }

        logger.info("domain_expert_calling_llm", thread_id=state.get("thread_id"))

        response = await _call_llm_with_retry(chain, input_data)

        # Parse JSON response
        try:
            domain_output = json.loads(response.content)
        except json.JSONDecodeError as e:
            logger.error(
                "domain_expert_json_parse_failed",
                error=str(e),
                response=response.content[:500]
            )
            domain_output = {
                "error": "Failed to parse JSON response",
                "raw_response": response.content
            }

        usage = _extract_token_usage(response)
        tokens = usage["total_tokens"]
        cost = tokens * 0.00001

        logger.info(
            "domain_expert_completed",
            thread_id=state.get("thread_id"),
            has_domain_knowledge=bool(domain_output.get("domain_knowledge")),
            tokens=tokens,
            cost=cost
        )

        return {
            "domain_output": domain_output,
            "messages": [
                SystemMessage(content=DOMAIN_PROMPT[:200] + "..."),
                HumanMessage(content=str(input_data)),
                response
            ],
            "total_tokens": state.get("total_tokens", 0) + tokens,
            "total_cost": state.get("total_cost", 0.0) + cost
        }

    except Exception as e:
        logger.error(
            "domain_expert_failed",
            thread_id=state.get("thread_id"),
            error=str(e),
            error_type=type(e).__name__
        )

        errors = state.get("errors", [])
        errors.append(f"Domain Expert failed: {str(e)}")

        return {
            "errors": errors,
            "retry_count": state.get("retry_count", 0) + 1
        }