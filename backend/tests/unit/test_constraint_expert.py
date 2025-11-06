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


@pytest.fixture
def mock_factory():
    """Create a mock ModelFactory."""
    factory = MagicMock()
    return factory


@pytest.mark.asyncio
async def test_constraint_expert_token_extraction_fallback(sample_state, mock_factory):
    """Test token extraction falls back to estimation when no metadata."""
    response = AIMessage(content=json.dumps({"constraint_categories": {}}))

    with patch('app.core.langgraph.agents.constraint_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.constraint_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = response

        result = await constraint_expert_node(sample_state)

        assert "total_tokens" in result
        assert result["total_tokens"] > 0


@pytest.mark.asyncio
async def test_constraint_expert_cost_calculation(sample_state, mock_factory):
    """Test accurate cost calculation from token usage."""
    response = AIMessage(content=json.dumps({"constraint_categories": {}}))
    response.response_metadata = {
        'usage': {
            'prompt_tokens': 2500,
            'completion_tokens': 1500,
            'total_tokens': 4000
        }
    }

    with patch('app.core.langgraph.agents.constraint_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.constraint_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = response

        result = await constraint_expert_node(sample_state)

        # Verify cost calculation: 4000 tokens * 0.00001 = 0.04
        assert result["total_tokens"] == 4000
        assert abs(result["total_cost"] - 0.04) < 0.0001


@pytest.mark.asyncio
async def test_constraint_expert_accumulates_metrics(sample_state, sample_llm_response, mock_factory):
    """Test that tokens and cost accumulate across calls."""
    sample_state["total_tokens"] = 1500
    sample_state["total_cost"] = 0.015

    with patch('app.core.langgraph.agents.constraint_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.constraint_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = sample_llm_response

        result = await constraint_expert_node(sample_state)

        # Should accumulate on top of existing metrics
        assert result["total_tokens"] == 1500 + 400  # existing + new
        assert result["total_cost"] > 0.015  # existing + new cost


@pytest.mark.asyncio
async def test_constraint_expert_complex_constraints(mock_factory):
    """Test constraint expert with complex constraint structure."""
    state = create_initial_state(
        problem_description="Multi-objective optimization with many constraints",
        thread_id="test-complex-456",
        domain="manufacturing"
    )
    state["orchestrator_output"] = {
        "problem_analysis": {"complexity_level": "high"},
        "workflow_plan": {"phases": [{"phase": "P1"}]}
    }
    state["algorithm_output"] = {
        "algorithm_recommendations": [
            {"algorithm_name": "NSGA-II"},
            {"algorithm_name": "MOEA/D"}
        ]
    }

    response_data = {
        "constraint_categories": {
            "hard_constraints": [
                {"constraint_id": "C1", "name": "Capacity", "type": "resource", "priority": "critical"},
                {"constraint_id": "C2", "name": "Time", "type": "time", "priority": "critical"},
                {"constraint_id": "C3", "name": "Budget", "type": "resource", "priority": "high"}
            ],
            "soft_constraints": [
                {"constraint_id": "S1", "name": "Quality", "type": "quality", "priority": "medium"},
                {"constraint_id": "S2", "name": "Preference", "type": "preference", "priority": "low"}
            ]
        },
        "constraint_relationships": {
            "dependencies": [{"constraint_ids": ["C1", "C2"]}],
            "conflicts": [{"constraint_ids": ["C2", "S1"]}]
        },
        "summary": {
            "total_hard_constraints": 3,
            "total_soft_constraints": 2,
            "complexity_assessment": "high"
        }
    }
    response = AIMessage(content=json.dumps(response_data))
    response.response_metadata = {'usage': {'total_tokens': 800}}

    with patch('app.core.langgraph.agents.constraint_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.constraint_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = response

        result = await constraint_expert_node(state)

        assert "constraint_output" in result
        output = result["constraint_output"]
        assert "constraint_categories" in output
        assert len(output["constraint_categories"]["hard_constraints"]) == 3
        assert len(output["constraint_categories"]["soft_constraints"]) == 2
        assert "constraint_relationships" in output


@pytest.mark.asyncio
async def test_constraint_expert_empty_constraints(sample_state, mock_factory):
    """Test constraint expert with no identified constraints."""
    response_data = {
        "constraint_categories": {
            "hard_constraints": [],
            "soft_constraints": []
        },
        "summary": {
            "total_hard_constraints": 0,
            "total_soft_constraints": 0
        }
    }
    response = AIMessage(content=json.dumps(response_data))
    response.response_metadata = {'usage': {'total_tokens': 150}}

    with patch('app.core.langgraph.agents.constraint_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.constraint_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = response

        result = await constraint_expert_node(sample_state)

        assert "constraint_output" in result
        assert result["constraint_output"]["constraint_categories"]["hard_constraints"] == []
        assert result["constraint_output"]["constraint_categories"]["soft_constraints"] == []


@pytest.mark.asyncio
async def test_constraint_expert_without_previous_outputs(mock_factory):
    """Test constraint expert with missing previous agent outputs."""
    state = create_initial_state(
        problem_description="Simple optimization",
        thread_id="test-789"
    )
    # No orchestrator_output or algorithm_output

    response_data = {
        "constraint_categories": {
            "hard_constraints": [{"constraint_id": "C1"}]
        },
        "summary": {"total_hard_constraints": 1}
    }
    response = AIMessage(content=json.dumps(response_data))
    response.response_metadata = {'usage': {'total_tokens': 200}}

    with patch('app.core.langgraph.agents.constraint_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.constraint_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = response

        result = await constraint_expert_node(state)

        # Should still succeed with missing previous outputs
        assert "constraint_output" in result
        assert "total_tokens" in result
