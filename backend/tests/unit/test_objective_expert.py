"""Unit tests for Objective Expert agent node."""

import pytest
import json
from unittest.mock import AsyncMock, patch
from langchain_core.messages import AIMessage

from app.core.langgraph.agents.objective_expert import objective_expert_node
from app.core.langgraph.state import create_initial_state


@pytest.fixture
def sample_state():
    state = create_initial_state(
        problem_description="Optimize delivery routes",
        thread_id="test-123",
        domain="logistics"
    )
    state["algorithm_output"] = {"algorithm_recommendations": []}
    state["constraint_output"] = {"constraint_categories": {}}
    return state


@pytest.fixture
def sample_llm_response():
    response_data = {
        "primary_objectives": [
            {
                "objective_id": "O1",
                "name": "Minimize distance",
                "type": "cost",
                "optimization_direction": "minimize"
            }
        ],
        "summary": {"total_objectives": 1}
    }
    response = AIMessage(content=json.dumps(response_data))
    response.response_metadata = {'usage': {'total_tokens': 400}}
    return response


@pytest.mark.asyncio
async def test_objective_expert_success(sample_state, sample_llm_response):
    """Test successful execution."""
    with patch('app.core.langgraph.agents.objective_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.objective_expert.ModelFactory.get_instance'):
        mock_llm.return_value = sample_llm_response

        result = await objective_expert_node(sample_state)

        assert "objective_output" in result
        assert "primary_objectives" in result["objective_output"]


@pytest.mark.asyncio
async def test_objective_expert_json_error(sample_state):
    """Test JSON parse error handling."""
    invalid_response = AIMessage(content="Invalid JSON")
    invalid_response.response_metadata = {'usage': {'total_tokens': 100}}

    with patch('app.core.langgraph.agents.objective_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.objective_expert.ModelFactory.get_instance'):
        mock_llm.return_value = invalid_response

        result = await objective_expert_node(sample_state)

        assert "error" in result["objective_output"]


@pytest.mark.asyncio
async def test_objective_expert_llm_failure(sample_state):
    """Test LLM call failure."""
    with patch('app.core.langgraph.agents.objective_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm:
        mock_llm.side_effect = Exception("LLM failed")

        result = await objective_expert_node(sample_state)

        assert "errors" in result
        assert "Objective Expert failed" in result["errors"][0]
