"""Unit tests for Algorithm Expert agent node."""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from langchain_core.messages import AIMessage

from app.core.langgraph.agents.algorithm_expert import algorithm_expert_node
from app.core.langgraph.state import WorkflowState, create_initial_state


@pytest.fixture
def mock_factory():
    """Create a mock ModelFactory."""
    factory = MagicMock()
    return factory


@pytest.fixture
def sample_state():
    """Create a sample workflow state with orchestrator output."""
    state = create_initial_state(
        problem_description="Optimize delivery routes for 100 vehicles",
        thread_id="test-thread-123",
        domain="logistics",
        constraints=["Real-time traffic", "Electric vehicles"]
    )
    # Add orchestrator output
    state["orchestrator_output"] = {
        "problem_analysis": {
            "summary": "Vehicle routing optimization",
            "complexity_level": "high"
        },
        "workflow_plan": {
            "approach": "Multi-objective optimization",
            "phases": [{"phase": "P1", "description": "Algorithm selection"}]
        }
    }
    return state


@pytest.fixture
def sample_llm_response():
    """Sample LLM response in JSON format."""
    response_data = {
        "problem_characteristics": {
            "problem_type": "combinatorial",
            "scale": "large",
            "dynamic_nature": "static",
            "key_features": ["Vehicle routing", "Battery constraints"]
        },
        "algorithm_recommendations": [
            {
                "algorithm_name": "EVRP-TW",
                "algorithm_family": "Vehicle Routing Problem",
                "recommendation_priority": "primary",
                "rationale": "Designed for electric vehicle routing",
                "applicable_scenarios": ["Large fleet optimization"],
                "limitations": ["Requires specialized solver"],
                "complexity_analysis": {
                    "time_complexity": "O(n^2)",
                    "space_complexity": "O(n*m)",
                    "scalability": "good"
                },
                "expected_performance": {
                    "solution_quality": "near_optimal",
                    "convergence_speed": "medium",
                    "robustness": "high"
                }
            }
        ],
        "implementation_approaches": {
            "exact_methods": {
                "recommended": ["OR-Tools"],
                "use_when": "Small problems",
                "libraries": ["ortools"]
            },
            "heuristic_methods": {
                "recommended": ["ALNS"],
                "use_when": "Large problems",
                "libraries": ["pymhlib"]
            },
            "hybrid_approaches": {
                "recommended": ["MILP + ALNS"],
                "description": "Combine exact and heuristic"
            }
        },
        "trade_offs": {
            "accuracy_vs_speed": "MILP optimal but slow",
            "scalability_vs_optimality": "Heuristics scale better",
            "complexity_vs_maintainability": "OR-Tools easier to maintain"
        },
        "recommendations_summary": {
            "primary_recommendation": "EVRP-TW with OR-Tools",
            "justification": "Balances quality and practicality",
            "fallback_options": ["ALNS", "MILP"]
        }
    }
    response = AIMessage(content=json.dumps(response_data))
    # Add token usage metadata
    response.response_metadata = {
        'usage': {
            'prompt_tokens': 300,
            'completion_tokens': 200,
            'total_tokens': 500
        }
    }
    return response


@pytest.mark.asyncio
async def test_algorithm_expert_success(
    sample_state,
    sample_llm_response,
    mock_factory
):
    """Test successful algorithm expert node execution."""
    with patch('app.core.langgraph.agents.algorithm_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.algorithm_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = sample_llm_response

        # Execute node
        result = await algorithm_expert_node(sample_state)

        # Verify results
        assert "algorithm_output" in result
        assert "messages" in result
        assert len(result["messages"]) > 0

        # Verify output structure
        output = result["algorithm_output"]
        assert "problem_characteristics" in output
        assert "algorithm_recommendations" in output
        assert "implementation_approaches" in output
        assert "trade_offs" in output
        assert "recommendations_summary" in output

        # Verify recommendations structure
        assert len(output["algorithm_recommendations"]) > 0
        first_rec = output["algorithm_recommendations"][0]
        assert "algorithm_name" in first_rec
        assert "complexity_analysis" in first_rec

        # Verify metrics
        assert "total_tokens" in result
        assert result["total_tokens"] == 500
        assert "total_cost" in result
        assert result["total_cost"] > 0.0

        # Verify LLM was called
        assert mock_llm.called


@pytest.mark.asyncio
async def test_algorithm_expert_json_parse_error(sample_state, mock_factory):
    """Test algorithm expert handling of invalid JSON response."""
    invalid_response = AIMessage(content="This is not valid JSON")
    invalid_response.response_metadata = {'usage': {'total_tokens': 100}}

    with patch('app.core.langgraph.agents.algorithm_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.algorithm_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = invalid_response

        # Execute node
        result = await algorithm_expert_node(sample_state)

        # Should still return result with error handling
        assert "algorithm_output" in result
        assert "error" in result["algorithm_output"]
        assert "raw_response" in result["algorithm_output"]


@pytest.mark.asyncio
async def test_algorithm_expert_llm_failure(sample_state):
    """Test algorithm expert handling of LLM call failure."""
    with patch('app.core.langgraph.agents.algorithm_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm:
        mock_llm.side_effect = Exception("LLM call failed")

        # Execute node
        result = await algorithm_expert_node(sample_state)

        # Should return error information
        assert "errors" in result
        assert len(result["errors"]) > 0
        assert "Algorithm Expert failed" in result["errors"][0]
        assert "retry_count" in result


@pytest.mark.asyncio
async def test_algorithm_expert_without_orchestrator_output(mock_factory):
    """Test algorithm expert with missing orchestrator output."""
    state = create_initial_state(
        problem_description="Test problem",
        thread_id="test-123"
    )
    # No orchestrator_output in state

    response_data = {"algorithm_recommendations": []}
    response = AIMessage(content=json.dumps(response_data))
    response.response_metadata = {'usage': {'total_tokens': 50}}

    with patch('app.core.langgraph.agents.algorithm_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.algorithm_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = response

        # Should still execute successfully
        result = await algorithm_expert_node(state)

        assert "algorithm_output" in result
        assert "total_tokens" in result


@pytest.mark.asyncio
async def test_algorithm_expert_token_extraction_fallback(sample_state, mock_factory):
    """Test token extraction falls back to estimation when no metadata."""
    response = AIMessage(content=json.dumps({"test": "data"}))

    with patch('app.core.langgraph.agents.algorithm_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.algorithm_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = response

        # Execute node
        result = await algorithm_expert_node(sample_state)

        # Should have estimated tokens
        assert "total_tokens" in result
        assert result["total_tokens"] > 0


@pytest.mark.asyncio
async def test_algorithm_expert_cost_calculation(sample_state, mock_factory):
    """Test accurate cost calculation from token usage."""
    # Create response with known token count
    response = AIMessage(content=json.dumps({"algorithm_recommendations": []}))
    response.response_metadata = {
        'usage': {
            'prompt_tokens': 2000,
            'completion_tokens': 1000,
            'total_tokens': 3000
        }
    }

    with patch('app.core.langgraph.agents.algorithm_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.algorithm_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = response

        result = await algorithm_expert_node(sample_state)

        # Verify cost calculation: 3000 tokens * 0.00001 = 0.03
        assert result["total_tokens"] == 3000
        assert abs(result["total_cost"] - 0.03) < 0.0001


@pytest.mark.asyncio
async def test_algorithm_expert_accumulates_metrics(sample_state, sample_llm_response, mock_factory):
    """Test that tokens and cost accumulate across calls."""
    # Set initial state with existing metrics
    sample_state["total_tokens"] = 1000
    sample_state["total_cost"] = 0.01

    with patch('app.core.langgraph.agents.algorithm_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.algorithm_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = sample_llm_response

        result = await algorithm_expert_node(sample_state)

        # Should accumulate on top of existing metrics
        assert result["total_tokens"] == 1000 + 500  # existing + new
        assert result["total_cost"] > 0.01  # existing + new cost


@pytest.mark.asyncio
async def test_algorithm_expert_complex_orchestrator_output(mock_factory):
    """Test algorithm expert with complex orchestrator output."""
    state = create_initial_state(
        problem_description="Complex multi-objective optimization problem",
        thread_id="test-complex-123",
        domain="manufacturing"
    )
    # Complex orchestrator output with nested structures
    state["orchestrator_output"] = {
        "problem_analysis": {
            "summary": "Multi-stage production scheduling",
            "key_challenges": ["Multiple objectives", "Resource constraints", "Time windows"],
            "complexity_level": "high"
        },
        "workflow_plan": {
            "approach": "Hybrid optimization",
            "phases": [
                {"phase": "P1", "description": "Algorithm selection and constraint modeling"},
                {"phase": "P2", "description": "Domain knowledge integration"}
            ]
        },
        "task_assignments": {
            "algorithm_expert": "Recommend multi-objective optimization algorithms",
            "constraint_expert": "Model production constraints"
        }
    }

    response_data = {
        "problem_characteristics": {
            "problem_type": "optimization",
            "scale": "large"
        },
        "algorithm_recommendations": [
            {"algorithm_name": "NSGA-II", "recommendation_priority": "primary"}
        ]
    }
    response = AIMessage(content=json.dumps(response_data))
    response.response_metadata = {'usage': {'total_tokens': 600}}

    with patch('app.core.langgraph.agents.algorithm_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.algorithm_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = response

        result = await algorithm_expert_node(state)

        # Should handle complex orchestrator output successfully
        assert "algorithm_output" in result
        assert "algorithm_recommendations" in result["algorithm_output"]
        assert len(result["algorithm_output"]["algorithm_recommendations"]) > 0


@pytest.mark.asyncio
async def test_algorithm_expert_empty_recommendations(sample_state, mock_factory):
    """Test algorithm expert with empty recommendations list."""
    response_data = {
        "problem_characteristics": {
            "problem_type": "unknown",
            "scale": "unknown"
        },
        "algorithm_recommendations": [],  # Empty list
        "recommendations_summary": {
            "primary_recommendation": "Unable to recommend",
            "justification": "Insufficient information"
        }
    }
    response = AIMessage(content=json.dumps(response_data))
    response.response_metadata = {'usage': {'total_tokens': 100}}

    with patch('app.core.langgraph.agents.algorithm_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.algorithm_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = response

        result = await algorithm_expert_node(sample_state)

        # Should handle empty recommendations gracefully
        assert "algorithm_output" in result
        assert "algorithm_recommendations" in result["algorithm_output"]
        assert result["algorithm_output"]["algorithm_recommendations"] == []
