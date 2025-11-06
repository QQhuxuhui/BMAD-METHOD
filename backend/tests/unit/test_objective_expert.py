"""Unit tests for Objective Expert agent node."""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
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


@pytest.fixture
def mock_factory():
    """Create a mock ModelFactory."""
    factory = MagicMock()
    return factory


@pytest.mark.asyncio
async def test_objective_expert_token_extraction_fallback(sample_state, mock_factory):
    """Test token extraction falls back to estimation when no metadata."""
    response = AIMessage(content=json.dumps({"primary_objectives": []}))

    with patch('app.core.langgraph.agents.objective_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.objective_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = response

        result = await objective_expert_node(sample_state)

        assert "total_tokens" in result
        assert result["total_tokens"] > 0


@pytest.mark.asyncio
async def test_objective_expert_cost_calculation(sample_state, mock_factory):
    """Test accurate cost calculation from token usage."""
    response = AIMessage(content=json.dumps({"primary_objectives": []}))
    response.response_metadata = {
        'usage': {
            'prompt_tokens': 1800,
            'completion_tokens': 1200,
            'total_tokens': 3000
        }
    }

    with patch('app.core.langgraph.agents.objective_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.objective_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = response

        result = await objective_expert_node(sample_state)

        # Verify cost calculation: 3000 tokens * 0.00001 = 0.03
        assert result["total_tokens"] == 3000
        assert abs(result["total_cost"] - 0.03) < 0.0001


@pytest.mark.asyncio
async def test_objective_expert_accumulates_metrics(sample_state, sample_llm_response, mock_factory):
    """Test that tokens and cost accumulate across calls."""
    sample_state["total_tokens"] = 800
    sample_state["total_cost"] = 0.008

    with patch('app.core.langgraph.agents.objective_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.objective_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = sample_llm_response

        result = await objective_expert_node(sample_state)

        # Should accumulate on top of existing metrics
        assert result["total_tokens"] == 800 + 400  # existing + new
        assert result["total_cost"] > 0.008  # existing + new cost


@pytest.mark.asyncio
async def test_objective_expert_multi_objectives(mock_factory):
    """Test objective expert with multiple objectives."""
    state = create_initial_state(
        problem_description="Multi-objective optimization problem",
        thread_id="test-multi-789",
        domain="manufacturing"
    )
    state["algorithm_output"] = {
        "algorithm_recommendations": [{"algorithm_name": "NSGA-II"}]
    }
    state["constraint_output"] = {
        "constraint_categories": {
            "hard_constraints": [{"constraint_id": "C1"}]
        }
    }

    response_data = {
        "primary_objectives": [
            {
                "objective_id": "O1",
                "name": "Minimize cost",
                "type": "cost",
                "optimization_direction": "minimize",
                "weight": 0.4
            },
            {
                "objective_id": "O2",
                "name": "Maximize quality",
                "type": "quality",
                "optimization_direction": "maximize",
                "weight": 0.6
            }
        ],
        "secondary_objectives": [
            {
                "objective_id": "O3",
                "name": "Minimize time",
                "type": "time",
                "optimization_direction": "minimize"
            }
        ],
        "trade_offs": {
            "cost_vs_quality": "Higher quality typically increases cost"
        },
        "summary": {
            "total_objectives": 3,
            "optimization_approach": "weighted_sum"
        }
    }
    response = AIMessage(content=json.dumps(response_data))
    response.response_metadata = {'usage': {'total_tokens': 600}}

    with patch('app.core.langgraph.agents.objective_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.objective_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = response

        result = await objective_expert_node(state)

        assert "objective_output" in result
        output = result["objective_output"]
        assert len(output["primary_objectives"]) == 2
        assert len(output["secondary_objectives"]) == 1
        assert "trade_offs" in output


@pytest.mark.asyncio
async def test_objective_expert_empty_objectives(sample_state, mock_factory):
    """Test objective expert with no objectives identified."""
    response_data = {
        "primary_objectives": [],
        "summary": {
            "total_objectives": 0,
            "note": "Unable to identify clear objectives"
        }
    }
    response = AIMessage(content=json.dumps(response_data))
    response.response_metadata = {'usage': {'total_tokens': 150}}

    with patch('app.core.langgraph.agents.objective_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.objective_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = response

        result = await objective_expert_node(sample_state)

        assert "objective_output" in result
        assert result["objective_output"]["primary_objectives"] == []


@pytest.mark.asyncio
async def test_objective_expert_without_previous_outputs(mock_factory):
    """Test objective expert with missing previous agent outputs."""
    state = create_initial_state(
        problem_description="Simple optimization",
        thread_id="test-simple-456"
    )
    # No algorithm_output or constraint_output

    response_data = {
        "primary_objectives": [
            {"objective_id": "O1", "name": "Maximize profit"}
        ],
        "summary": {"total_objectives": 1}
    }
    response = AIMessage(content=json.dumps(response_data))
    response.response_metadata = {'usage': {'total_tokens': 250}}

    with patch('app.core.langgraph.agents.objective_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.objective_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = response

        result = await objective_expert_node(state)

        # Should still succeed with missing previous outputs
        assert "objective_output" in result
        assert "total_tokens" in result
