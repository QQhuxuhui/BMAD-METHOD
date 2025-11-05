"""Base Agent Node for BMAD Workflow.

Provides common functionality for all agent nodes including:
- LLM calling with retry logic
- Token usage extraction and cost calculation
- Error handling
- Structured logging
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

    def __init__(self, agent_name: str, prompt_file: str):
        """Initialize base agent node.

        Args:
            agent_name: Name of the agent (e.g., "orchestrator", "algorithm_expert")
            prompt_file: Filename of the prompt template (e.g., "orchestrator.md")
        """
        self.agent_name = agent_name
        self.prompt_file = prompt_file
        self.prompt_content = self._load_prompt()

    def _load_prompt(self) -> str:
        """Load prompt template from file."""
        prompt_path = Path(__file__).parent.parent / "prompts" / self.prompt_file
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True
    )
    async def _call_llm_with_retry(self, chain, input_data: Dict[str, Any]) -> AIMessage:
        """Call LLM with retry logic for transient errors."""
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

    def _calculate_cost(self, tokens: int) -> float:
        """Calculate cost based on token count.

        Args:
            tokens: Total token count

        Returns:
            Estimated cost in USD
        """
        # Rough estimate: $0.01 per 1K tokens
        return tokens * 0.00001

    def _parse_json_response(self, response: AIMessage, output_key: str) -> Dict[str, Any]:
        """Parse JSON response with error handling.

        Args:
            response: AI message from LLM
            output_key: Key name for the output (e.g., "orchestrator_output")

        Returns:
            Parsed JSON dict or error dict
        """
        try:
            return json.loads(response.content)
        except json.JSONDecodeError as e:
            logger.error(
                f"{self.agent_name}_json_parse_failed",
                error=str(e),
                response=response.content[:500]
            )
            return {
                "error": "Failed to parse JSON response",
                "raw_response": response.content
            }

    @abstractmethod
    def _build_input_data(self, state: WorkflowState) -> Dict[str, Any]:
        """Build input data for the LLM prompt.

        Must be implemented by subclasses.

        Args:
            state: Current workflow state

        Returns:
            Dict with input data for the prompt
        """
        pass

    @abstractmethod
    def _get_output_key(self) -> str:
        """Get the state key for this agent's output.

        Must be implemented by subclasses.

        Returns:
            State key name (e.g., "orchestrator_output")
        """
        pass

    def _get_human_message_template(self) -> str:
        """Get the human message template.

        Can be overridden by subclasses for custom templates.

        Returns:
            Template string
        """
        return """Problem Description: {problem_description}

Domain: {domain}

Please analyze this problem and provide your output in JSON format."""

    async def execute(self, state: WorkflowState) -> Dict[str, Any]:
        """Execute the agent node.

        Args:
            state: Current workflow state

        Returns:
            Dict with updated state fields
        """
        output_key = self._get_output_key()

        logger.info(
            f"{self.agent_name}_started",
            thread_id=state.get("thread_id")
        )

        try:
            # Get LLM
            factory = ModelFactory.get_instance()
            llm = factory.get_langchain_model()

            # Build prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.prompt_content),
                ("human", self._get_human_message_template())
            ])

            # Prepare input
            chain = prompt | llm
            input_data = self._build_input_data(state)

            # Call LLM
            logger.info(f"{self.agent_name}_calling_llm", thread_id=state.get("thread_id"))
            response = await self._call_llm_with_retry(chain, input_data)

            # Parse response
            output = self._parse_json_response(response, output_key)

            # Extract metrics
            usage = self._extract_token_usage(response)
            tokens = usage["total_tokens"]
            cost = self._calculate_cost(tokens)

            # Log completion
            logger.info(
                f"{self.agent_name}_completed",
                thread_id=state.get("thread_id"),
                tokens=tokens,
                cost=cost
            )

            # Return updated state
            return {
                output_key: output,
                "messages": [
                    SystemMessage(content=self.prompt_content[:200] + "..."),
                    HumanMessage(content=str(input_data)),
                    response
                ],
                "total_tokens": state.get("total_tokens", 0) + tokens,
                "total_cost": state.get("total_cost", 0.0) + cost
            }

        except Exception as e:
            logger.error(
                f"{self.agent_name}_failed",
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
