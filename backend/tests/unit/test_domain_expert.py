"""Unit tests for Domain Expert agent node."""

import pytest
import json
from unittest.mock import AsyncMock, patch
from langchain_core.messages import AIMessage

from app.core.langgraph.agents.domain_expert import domain_expert_node
from app.core.langgraph.state import create_initial_state


@pytest.fixture
def sample_state():
    state = create_initial_state(
        problem_description="Optimize delivery routes",
        thread_id="test-123",
        domain="logistics"
    )
    state["orchestrator_output"] = {"problem_analysis": {}}
    state["algorithm_output"] = {"algorithm_recommendations": []}
    state["constraint_output"] = {"constraint_categories": {}}
    state["objective_output"] = {"primary_objectives": []}
    return state


@pytest.fixture
def sample_llm_response():
    response_data = {
        "domain_knowledge": {
            "domain_overview": "Logistics domain",
            "key_concepts": [
                {
                    "concept": "Route optimization",
                    "definition": "Finding optimal paths",
                    "relevance": "Critical for efficiency"
                }
            ]
        },
        "summary": {"domain_complexity": "moderate"}
    }
    response = AIMessage(content=json.dumps(response_data))
    response.response_metadata = {'usage': {'total_tokens': 500}}
    return response


@pytest.mark.asyncio
async def test_domain_expert_success(sample_state, sample_llm_response):
    """Test successful execution."""
    with patch('app.core.langgraph.agents.domain_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.domain_expert.ModelFactory.get_instance'):
        mock_llm.return_value = sample_llm_response

        result = await domain_expert_node(sample_state)

        assert "domain_output" in result
        assert "domain_knowledge" in result["domain_output"]


@pytest.mark.asyncio
async def test_domain_expert_json_error(sample_state):
    """Test JSON parse error handling."""
    invalid_response = AIMessage(content="Invalid JSON")
    invalid_response.response_metadata = {'usage': {'total_tokens': 100}}

    with patch('app.core.langgraph.agents.domain_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.domain_expert.ModelFactory.get_instance'):
        mock_llm.return_value = invalid_response

        result = await domain_expert_node(sample_state)

        assert "error" in result["domain_output"]


@pytest.mark.asyncio
async def test_domain_expert_llm_failure(sample_state):
    """Test LLM call failure."""
    with patch('app.core.langgraph.agents.domain_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm:
        mock_llm.side_effect = Exception("LLM failed")

        result = await domain_expert_node(sample_state)

        assert "errors" in result
        assert "Domain Expert failed" in result["errors"][0]