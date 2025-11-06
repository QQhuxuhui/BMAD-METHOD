"""Extension Expert Agent Node for BMAD Workflow.

The Extension Expert is part of Phase 3 (P3), responsible for:
- Analyzing code extensibility and modularity
- Identifying extension points and improvement opportunities
- Planning future evolution and roadmap
- Assessing technical debt and providing remediation strategies
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

logger = structlog.get_logger("extension_expert")

# Load prompt template
PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "extension.md"
with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
    EXTENSION_PROMPT = f.read()


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


async def extension_expert_node(state: WorkflowState) -> Dict[str, Any]:
    """Extension Expert agent node - Phase 3 (P3).

    Analyzes code extensibility, identifies improvement opportunities,
    and provides recommendations for future evolution.

    Args:
        state: Current workflow state

    Returns:
        Dict with updated state fields
    """
    logger.info(
        "extension_expert_started",
        thread_id=state.get("thread_id")
    )

    try:
        factory = ModelFactory.get_instance()
        llm = factory.get_langchain_model()

        # Extract code output from previous phase
        code_output = state.get("code_output", {})
        implementation_code = code_output.get("implementation_code", "")
        dependencies = code_output.get("dependencies", [])
        unit_tests = code_output.get("unit_tests", "")
        documentation = code_output.get("documentation", "")

        # Extract context information
        problem_description = state.get("problem_description", "")
        domain = state.get("domain", "Not specified")

        prompt = ChatPromptTemplate.from_messages([
            ("system", EXTENSION_PROMPT),
            ("human", """Implementation Code:
{implementation_code}

Dependencies: {dependencies}

Unit Tests:
{unit_tests}

Documentation:
{documentation}

Problem Description: {problem_description}

Domain: {domain}

Please analyze the extensibility and provide comprehensive recommendations in JSON format.""")
        ])

        chain = prompt | llm

        input_data = {
            "implementation_code": implementation_code,
            "dependencies": json.dumps(dependencies, indent=2) if dependencies else "None",
            "unit_tests": unit_tests if unit_tests else "No unit tests provided",
            "documentation": documentation if documentation else "No documentation provided",
            "problem_description": problem_description,
            "domain": domain
        }

        logger.info("extension_expert_calling_llm", thread_id=state.get("thread_id"))

        response = await _call_llm_with_retry(chain, input_data)

        # Parse JSON response
        try:
            extension_output = json.loads(response.content)
        except json.JSONDecodeError as e:
            logger.error(
                "extension_expert_json_parse_failed",
                error=str(e),
                response=response.content[:500]
            )
            extension_output = {
                "error": "Failed to parse JSON response",
                "raw_response": response.content
            }

        # Validate and calculate extensibility score
        if "extensibility_analysis" in extension_output:
            score = extension_output["extensibility_analysis"].get("current_extensibility_score", "0/10")
            logger.info(
                "extension_expert_analyzed",
                thread_id=state.get("thread_id"),
                extensibility_score=score,
                has_extension_points=bool(extension_output.get("extensibility_analysis", {}).get("extension_points")),
                has_improvements=bool(extension_output.get("modularity_improvements"))
            )

        usage = _extract_token_usage(response)
        tokens = usage["total_tokens"]
        cost = tokens * 0.00001

        logger.info(
            "extension_expert_completed",
            thread_id=state.get("thread_id"),
            tokens=tokens,
            cost=cost
        )

        return {
            "extension_output": extension_output,
            "messages": [
                SystemMessage(content=EXTENSION_PROMPT[:200] + "..."),
                HumanMessage(content=str(input_data)),
                response
            ],
            "total_tokens": state.get("total_tokens", 0) + tokens,
            "total_cost": state.get("total_cost", 0.0) + cost
        }

    except Exception as e:
        logger.error(
            "extension_expert_failed",
            thread_id=state.get("thread_id"),
            error=str(e),
            error_type=type(e).__name__
        )

        errors = state.get("errors", [])
        errors.append(f"Extension Expert failed: {str(e)}")

        return {
            "errors": errors,
            "retry_count": state.get("retry_count", 0) + 1
        }