"""Unit tests for Constraint Expert agent node."""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from langchain_core.messages import AIMessage

from app.core.langgraph.agents.constraint_expert import constraint_expert_node
from app.core.langgraph.state import create_initial_state


@pytest.fixture
def sample_state():
    """Create a sample workflow state."""
    state = create_initial_state(
        problem_description="Optimize delivery routes",
        thread_id="test-123",
        domain="logistics"
    )
    state["orchestrator_output"] = {"workflow_plan": {}}
    state["algorithm_output"] = {"algorithm_recommendations": []}
    return state


@pytest.fixture
def sample_llm_response():
    """Sample LLM response."""
    response_data = {
        "constraint_categories": {
            "hard_constraints": [
                {
                    "constraint_id": "C1",
                    "name": "Battery capacity",
                    "type": "resource",
                    "priority": "critical"
                }
            ],
            "soft_constraints": []
        },
        "summary": {
            "total_hard_constraints": 1,
            "total_soft_constraints": 0
        }
    }
    response = AIMessage(content=json.dumps(response_data))
    response.response_metadata = {'usage': {'total_tokens': 400}}
    return response


@pytest.mark.asyncio
async def test_constraint_expert_success(sample_state, sample_llm_response):
    """Test successful execution."""
    with patch('app.core.langgraph.agents.constraint_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.constraint_expert.ModelFactory.get_instance'):
        mock_llm.return_value = sample_llm_response

        result = await constraint_expert_node(sample_state)

        assert "constraint_output" in result
        assert "constraint_categories" in result["constraint_output"]
        assert "total_tokens" in result


@pytest.mark.asyncio
async def test_constraint_expert_json_error(sample_state):
    """Test handling of JSON parse error."""
    invalid_response = AIMessage(content="Invalid JSON")
    invalid_response.response_metadata = {'usage': {'total_tokens': 100}}

    with patch('app.core.langgraph.agents.constraint_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.constraint_expert.ModelFactory.get_instance'):
        mock_llm.return_value = invalid_response

        result = await constraint_expert_node(sample_state)

        assert "error" in result["constraint_output"]


@pytest.mark.asyncio
async def test_constraint_expert_llm_failure(sample_state):
    """Test LLM call failure."""
    with patch('app.core.langgraph.agents.constraint_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm:
        mock_llm.side_effect = Exception("LLM failed")

        result = await constraint_expert_node(sample_state)

        assert "errors" in result
        assert "Constraint Expert failed" in result["errors"][0]
