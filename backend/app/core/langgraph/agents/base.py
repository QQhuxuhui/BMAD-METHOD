"""Base class for BMAD Agent Nodes.

Provides common functionality for all agent nodes:
- LLM calling with retry
- Token tracking
- Error handling
- JSON parsing
"""

import json
from typing import Dict, Any, Optional
from pathlib import Path
from abc import ABC, abstractmethod

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import structlog

from app.core.langgraph.state import WorkflowState
from model_adapters.model_factory import ModelFactory

logger = structlog.get_logger(__name__)


class BaseAgentNode(ABC):
    """Base class for all BMAD agent nodes."""

    def __init__(self, prompt_file: str):
        """Initialize agent node.

        Args:
            prompt_file: Path to prompt markdown file relative to prompts/ directory
        """
        self.agent_name = self.__class__.__name__.replace("AgentNode", "").replace("Agent", "")
        prompt_path = Path(__file__).parent.parent / "prompts" / prompt_file
        with open(prompt_path, 'r', encoding='utf-8') as f:
            self.prompt_template = f.read()

    @abstractmethod
    def get_agent_input(self, state: WorkflowState) -> Dict[str, Any]:
        """Extract input data for this agent from workflow state.

        Args:
            state: Current workflow state

        Returns:
            Dict of input variables for prompt template
        """
        pass

    @abstractmethod
    def get_state_update_key(self) -> str:
        """Return the state key to update with agent output.

        Returns:
            Key name like 'algorithm_output', 'constraint_output', etc.
        """
        pass

    @abstractmethod
    def get_next_phase(self, state: WorkflowState) -> Optional[str]:
        """Determine next phase after this agent completes.

        Args:
            state: Current workflow state

        Returns:
            Next phase ID ('P1', 'P2', etc.) or None to keep current phase
        """
        pass

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True
    )
    async def _call_llm(self, chain, input_data: Dict[str, Any]) -> AIMessage:
        """Call LLM with retry logic."""
        return await chain.ainvoke(input_data)

    def _extract_token_usage(self, response: AIMessage) -> Dict[str, int]:
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

        # Fallback: estimate from content length
        if usage["total_tokens"] == 0:
            usage["total_tokens"] = len(response.content) // 4
            usage["output_tokens"] = usage["total_tokens"]

        return usage

    async def __call__(self, state: WorkflowState) -> Dict[str, Any]:
        """Execute the agent node.

        Args:
            state: Current workflow state

        Returns:
            Dict with updated state fields
        """
        logger.info(
            f"{self.agent_name.lower()}_started",
            thread_id=state.get("thread_id"),
            current_phase=state.get("current_phase")
        )

        try:
            # Get LLM
            factory = ModelFactory.get_instance()
            llm = factory.get_langchain_model()

            # Build prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.prompt_template),
                ("human", "{agent_input}")
            ])

            # Prepare input
            chain = prompt | llm
            agent_input = self.get_agent_input(state)

            # Call LLM with retry
            logger.info(
                f"{self.agent_name.lower()}_calling_llm",
                thread_id=state.get("thread_id")
            )

            response = await self._call_llm(chain, {"agent_input": json.dumps(agent_input, indent=2)})

            # Parse JSON response
            try:
                agent_output = json.loads(response.content)
            except json.JSONDecodeError as e:
                logger.error(
                    f"{self.agent_name.lower()}_json_parse_failed",
                    error=str(e),
                    response=response.content[:500]
                )
                agent_output = {
                    "error": "Failed to parse JSON response",
                    "raw_response": response.content
                }

            # Extract token usage
            usage = _extract_token_usage(response)
            tokens = usage["total_tokens"]
            cost = tokens * 0.00001  # Rough estimate

            # Determine next phase
            next_phase = self.get_next_phase(state)

            # Build state update
            state_update = {
                self.get_state_update_key(): agent_output,
                "messages": [
                    SystemMessage(content=self.prompt_template[:200] + "..."),
                    HumanMessage(content=str(agent_input)),
                    response
                ],
                "total_tokens": state.get("total_tokens", 0) + tokens,
                "total_cost": state.get("total_cost", 0.0) + cost
            }

            if next_phase:
                state_update["current_phase"] = next_phase

            logger.info(
                f"{self.agent_name.lower()}_completed",
                thread_id=state.get("thread_id"),
                tokens=tokens,
                cost=cost
            )

            return state_update

        except Exception as e:
            logger.error(
                f"{self.agent_name.lower()}_failed",
                thread_id=state.get("thread_id"),
                error=str(e),
                error_type=type(e).__name__
            )

            errors = state.get("errors", [])
            errors.append(f"{self.agent_name} failed: {str(e)}")

            return {
                "errors": errors,
                "retry_count": state.get("retry_count", 0) + 1
            }


# Helper function for token extraction (used in orchestrator.py too)
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
