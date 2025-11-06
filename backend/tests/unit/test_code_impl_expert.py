"""Unit tests for Code Implementation Expert agent node."""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from langchain_core.messages import AIMessage

from app.core.langgraph.agents.code_impl_expert import code_impl_expert_node
from app.core.langgraph.state import create_initial_state


@pytest.fixture
def sample_state():
    """Create a sample workflow state with P1 outputs."""
    state = create_initial_state(
        problem_description="Optimize delivery routes",
        thread_id="test-123",
        domain="logistics"
    )
    state["orchestrator_output"] = {"problem_analysis": {}}
    state["algorithm_output"] = {"algorithm_recommendations": []}
    state["constraint_output"] = {"constraint_categories": {}}
    state["objective_output"] = {"primary_objectives": []}
    state["domain_output"] = {"domain_knowledge": {}}
    return state


@pytest.fixture
def sample_llm_response():
    """Sample LLM response with code implementation."""
    response_data = {
        "implementation_code": {
            "main_code": "def optimize_routes():\n    pass",
            "helper_functions": []
        },
        "dependencies": ["numpy", "scipy"],
        "unit_tests": {
            "test_code": "def test_optimize_routes():\n    assert True"
        },
        "usage_example": "optimize_routes()",
        "summary": {"implementation_complexity": "moderate"}
    }
    response = AIMessage(content=json.dumps(response_data))
    response.response_metadata = {'usage': {'total_tokens': 600}}
    return response


@pytest.fixture
def mock_factory():
    """Create a mock ModelFactory."""
    factory = MagicMock()
    return factory


@pytest.mark.asyncio
async def test_code_impl_expert_success(sample_state, sample_llm_response, mock_factory):
    """Test successful code generation."""
    with patch('app.core.langgraph.agents.code_impl_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.code_impl_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = sample_llm_response

        result = await code_impl_expert_node(sample_state)

        assert "code_output" in result
        assert "implementation_code" in result["code_output"]
        assert "dependencies" in result["code_output"]
        assert "unit_tests" in result["code_output"]


@pytest.mark.asyncio
async def test_code_impl_expert_json_error(sample_state, mock_factory):
    """Test JSON parse error handling."""
    invalid_response = AIMessage(content="Invalid JSON")
    invalid_response.response_metadata = {'usage': {'total_tokens': 100}}

    with patch('app.core.langgraph.agents.code_impl_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.code_impl_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = invalid_response

        result = await code_impl_expert_node(sample_state)

        assert "error" in result["code_output"]


@pytest.mark.asyncio
async def test_code_impl_expert_llm_failure(sample_state):
    """Test LLM call failure."""
    with patch('app.core.langgraph.agents.code_impl_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm:
        mock_llm.side_effect = Exception("LLM failed")

        result = await code_impl_expert_node(sample_state)

        assert "errors" in result
        assert "Code Implementation Expert failed" in result["errors"][0]


@pytest.mark.asyncio
async def test_code_impl_expert_token_extraction_fallback(sample_state, mock_factory):
    """Test token extraction falls back to estimation when no metadata."""
    response = AIMessage(content=json.dumps({"implementation_code": {}}))

    with patch('app.core.langgraph.agents.code_impl_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.code_impl_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = response

        result = await code_impl_expert_node(sample_state)

        assert "total_tokens" in result
        assert result["total_tokens"] > 0


@pytest.mark.asyncio
async def test_code_impl_expert_cost_calculation(sample_state, mock_factory):
    """Test accurate cost calculation from token usage."""
    response = AIMessage(content=json.dumps({"implementation_code": {}}))
    response.response_metadata = {
        'usage': {
            'prompt_tokens': 3000,
            'completion_tokens': 2000,
            'total_tokens': 5000
        }
    }

    with patch('app.core.langgraph.agents.code_impl_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.code_impl_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = response

        result = await code_impl_expert_node(sample_state)

        # Verify cost calculation: 5000 tokens * 0.00001 = 0.05
        assert result["total_tokens"] == 5000
        assert abs(result["total_cost"] - 0.05) < 0.0001


@pytest.mark.asyncio
async def test_code_impl_expert_accumulates_metrics(sample_state, sample_llm_response, mock_factory):
    """Test that tokens and cost accumulate across calls."""
    sample_state["total_tokens"] = 2000
    sample_state["total_cost"] = 0.02

    with patch('app.core.langgraph.agents.code_impl_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.code_impl_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = sample_llm_response

        result = await code_impl_expert_node(sample_state)

        # Should accumulate on top of existing metrics
        assert result["total_tokens"] == 2000 + 600  # existing + new
        assert result["total_cost"] > 0.02  # existing + new cost


@pytest.mark.asyncio
async def test_code_impl_expert_comprehensive_output(mock_factory):
    """Test code implementation expert with comprehensive output."""
    state = create_initial_state(
        problem_description="Complex optimization with multiple constraints",
        thread_id="test-comprehensive-789",
        domain="manufacturing"
    )
    # Include all P1 agent outputs
    state["orchestrator_output"] = {"problem_analysis": {"complexity_level": "high"}}
    state["algorithm_output"] = {"algorithm_recommendations": [{"algorithm_name": "GA"}]}
    state["constraint_output"] = {"constraint_categories": {"hard_constraints": []}}
    state["objective_output"] = {"primary_objectives": [{"objective_id": "O1"}]}
    state["domain_output"] = {"best_practices": ["Practice 1"]}

    response_data = {
        "implementation_code": {
            "main_code": "class OptimizationModel:\n    def __init__(self):\n        pass",
            "helper_functions": [
                {"name": "validate_constraints", "code": "def validate_constraints():\n    pass"}
            ],
            "data_structures": ["decision_variables", "parameters"]
        },
        "dependencies": ["numpy>=1.20", "scipy>=1.7", "ortools>=9.0"],
        "unit_tests": {
            "test_code": "import pytest\n\ndef test_model_initialization():\n    pass",
            "coverage_note": "Tests cover main functionality"
        },
        "usage_example": "model = OptimizationModel()\nresult = model.solve()",
        "documentation": {
            "overview": "Implementation of BMAD ten-element modeling",
            "key_components": ["Model", "Solver", "Validator"]
        },
        "performance_considerations": ["Use vectorized operations", "Cache results"],
        "summary": {
            "implementation_complexity": "high",
            "estimated_loc": 500,
            "key_features": ["Constraint handling", "Multi-objective optimization"]
        }
    }
    response = AIMessage(content=json.dumps(response_data))
    response.response_metadata = {'usage': {'total_tokens': 1200}}

    with patch('app.core.langgraph.agents.code_impl_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.code_impl_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = response

        result = await code_impl_expert_node(state)

        assert "code_output" in result
        output = result["code_output"]
        assert "implementation_code" in output
        assert "helper_functions" in output["implementation_code"]
        assert len(output["dependencies"]) == 3
        assert "unit_tests" in output
        assert "documentation" in output


@pytest.mark.asyncio
async def test_code_impl_expert_minimal_output(sample_state, mock_factory):
    """Test code implementation expert with minimal output."""
    response_data = {
        "implementation_code": {
            "main_code": "# Placeholder implementation"
        },
        "dependencies": [],
        "summary": {"note": "Minimal implementation provided"}
    }
    response = AIMessage(content=json.dumps(response_data))
    response.response_metadata = {'usage': {'total_tokens': 300}}

    with patch('app.core.langgraph.agents.code_impl_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.code_impl_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = response

        result = await code_impl_expert_node(sample_state)

        assert "code_output" in result
        assert result["code_output"]["dependencies"] == []


@pytest.mark.asyncio
async def test_code_impl_expert_without_p1_outputs(mock_factory):
    """Test code implementation expert with missing P1 agent outputs."""
    state = create_initial_state(
        problem_description="Simple problem",
        thread_id="test-simple-456",
        domain="general"
    )
    # No P1 agent outputs

    response_data = {
        "implementation_code": {
            "main_code": "def solve_problem():\n    pass"
        },
        "dependencies": ["numpy"],
        "summary": {"note": "Basic implementation without detailed specifications"}
    }
    response = AIMessage(content=json.dumps(response_data))
    response.response_metadata = {'usage': {'total_tokens': 400}}

    with patch('app.core.langgraph.agents.code_impl_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.code_impl_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = response

        result = await code_impl_expert_node(state)

        # Should still succeed with missing P1 outputs
        assert "code_output" in result
        assert "total_tokens" in result
