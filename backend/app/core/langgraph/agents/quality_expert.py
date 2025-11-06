"""Quality Expert Agent Node for BMAD Workflow.

The Quality Expert is part of Phase 3 (P3), responsible for:
- Comprehensive quality assessment of all previous outputs
- Validation against acceptance criteria
- Component-wise quality review
- Final approval or improvement recommendations
- Setting the current phase to P4 (completion)
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

logger = structlog.get_logger("quality_expert")

# Load prompt template
PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "quality.md"
with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
    QUALITY_PROMPT = f.read()


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


async def quality_expert_node(state: WorkflowState) -> Dict[str, Any]:
    """Quality Expert agent node - Phase 3 (P3).

    Performs comprehensive quality assessment of all previous outputs
    and provides final approval or improvement recommendations.

    Args:
        state: Current workflow state

    Returns:
        Dict with updated state fields, including phase transition to P4
    """
    logger.info(
        "quality_expert_started",
        thread_id=state.get("thread_id")
    )

    try:
        factory = ModelFactory.get_instance()
        llm = factory.get_langchain_model()

        # Extract all previous agent outputs for comprehensive review
        problem_description = state.get("problem_description", "")
        domain = state.get("domain", "Not specified")
        orchestrator_output = state.get("orchestrator_output", {})
        algorithm_output = state.get("algorithm_output", {})
        constraint_output = state.get("constraint_output", {})
        objective_output = state.get("objective_output", {})
        domain_output = state.get("domain_output", {})
        code_output = state.get("code_output", {})
        extension_output = state.get("extension_output", {})

        prompt = ChatPromptTemplate.from_messages([
            ("system", QUALITY_PROMPT),
            ("human", """Problem Description: {problem_description}

Domain: {domain}

Orchestrator Output:
{orchestrator_output}

Algorithm Expert Output:
{algorithm_output}

Constraint Expert Output:
{constraint_output}

Objective Expert Output:
{objective_output}

Domain Expert Output:
{domain_output}

Code Implementation Output:
{code_output}

Extension Expert Output:
{extension_output}

Please perform a comprehensive quality assessment and provide your evaluation in JSON format.""")
        ])

        chain = prompt | llm

        input_data = {
            "problem_description": problem_description,
            "domain": domain,
            "orchestrator_output": json.dumps(orchestrator_output, indent=2) if orchestrator_output else "Not available",
            "algorithm_output": json.dumps(algorithm_output, indent=2) if algorithm_output else "Not available",
            "constraint_output": json.dumps(constraint_output, indent=2) if constraint_output else "Not available",
            "objective_output": json.dumps(objective_output, indent=2) if objective_output else "Not available",
            "domain_output": json.dumps(domain_output, indent=2) if domain_output else "Not available",
            "code_output": json.dumps(code_output, indent=2) if code_output else "Not available",
            "extension_output": json.dumps(extension_output, indent=2) if extension_output else "Not available"
        }

        logger.info("quality_expert_calling_llm", thread_id=state.get("thread_id"))

        response = await _call_llm_with_retry(chain, input_data)

        # Parse JSON response
        try:
            quality_output = json.loads(response.content)
        except json.JSONDecodeError as e:
            logger.error(
                "quality_expert_json_parse_failed",
                error=str(e),
                response=response.content[:500]
            )
            quality_output = {
                "error": "Failed to parse JSON response",
                "raw_response": response.content
            }

        # Extract final assessment
        if "final_assessment" in quality_output:
            final_assessment = quality_output["final_assessment"]
            approval_status = final_assessment.get("approval_status", "needs_improvement")
            confidence_level = final_assessment.get("confidence_level", "medium")

            logger.info(
                "quality_expert_completed",
                thread_id=state.get("thread_id"),
                approval_status=approval_status,
                confidence_level=confidence_level,
                overall_quality_score=quality_output.get("quality_assessment", {}).get("overall_quality_score", "Unknown")
            )

        usage = _extract_token_usage(response)
        tokens = usage["total_tokens"]
        cost = tokens * 0.00001

        logger.info(
            "quality_expert_finalized",
            thread_id=state.get("thread_id"),
            tokens=tokens,
            cost=cost
        )

        return {
            "quality_output": quality_output,
            "current_phase": "P4",  # Set to completion phase
            "messages": [
                SystemMessage(content=QUALITY_PROMPT[:200] + "..."),
                HumanMessage(content=str(input_data)),
                response
            ],
            "total_tokens": state.get("total_tokens", 0) + tokens,
            "total_cost": state.get("total_cost", 0.0) + cost
        }

    except Exception as e:
        logger.error(
            "quality_expert_failed",
            thread_id=state.get("thread_id"),
            error=str(e),
            error_type=type(e).__name__
        )

        errors = state.get("errors", [])
        errors.append(f"Quality Expert failed: {str(e)}")

        return {
            "errors": errors,
            "retry_count": state.get("retry_count", 0) + 1
        }