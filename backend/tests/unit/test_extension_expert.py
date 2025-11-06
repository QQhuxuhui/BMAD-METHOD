"""Unit tests for Extension Expert Agent Node."""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from langchain_core.messages import AIMessage

from app.core.langgraph.agents.extension_expert import extension_expert_node
from app.core.langgraph.state import create_initial_state


@pytest.fixture
def sample_state():
    """Create sample workflow state for testing."""
    state = create_initial_state(
        problem_description="Optimize production scheduling for manufacturing plant",
        thread_id="test-thread-123",
        domain="manufacturing"
    )
    state["code_output"] = {
        "implementation_code": """
class ProductionScheduler:
    def __init__(self):
        self.jobs = []
        self.resources = []

    def add_job(self, job):
        self.jobs.append(job)

    def optimize_schedule(self):
        # Simple optimization logic
        return {"schedule": [], "objective": 1000}
""",
        "dependencies": ["numpy", "pandas"],
        "unit_tests": """
def test_production_scheduler():
    scheduler = ProductionScheduler()
    result = scheduler.optimize_schedule()
    assert result is not None
""",
        "documentation": "Simple production scheduler for manufacturing optimization."
    }
    state["total_tokens"] = 1000
    state["total_cost"] = 0.01
    return state


@pytest.fixture
def mock_factory():
    """Create a mock ModelFactory."""
    factory = MagicMock()
    return factory


@pytest.fixture
def sample_llm_response():
    """Sample LLM response with extension analysis."""
    response_data = {
        "extensibility_analysis": {
            "current_extensibility_score": "5/10",
            "extension_points": [
                {
                    "component": "optimize_schedule method",
                    "extension_type": "strategy pattern",
                    "ease_of_extension": "medium",
                    "description": "Replace with pluggable optimization algorithms"
                }
            ],
            "limitations": [
                {
                    "area": "algorithm selection",
                    "impact": "high",
                    "description": "Hardcoded optimization limits algorithm choice"
                }
            ]
        },
        "modularity_improvements": [
            {
                "current_structure": "Monolithic scheduler class",
                "suggested_refactor": "Separate Model, Solver, and Result classes",
                "benefits": ["separation of concerns", "better testability"],
                "implementation_effort": "medium"
            }
        ],
        "future_evolution": {
            "short_term_enhancements": [
                {
                    "feature": "Add support for multiple optimization algorithms",
                    "priority": "high",
                    "estimated_effort": "3 person-days",
                    "dependencies": ["algorithm interface"]
                }
            ],
            "long_term_vision": {
                "direction": "Evolve into comprehensive manufacturing optimization framework",
                "potential_features": ["real-time scheduling", "resource optimization", "predictive analytics"],
                "architecture_evolution": "Microservices architecture with specialized optimization services"
            }
        },
        "technical_debt_assessment": {
            "current_debt_items": [
                {
                    "category": "code",
                    "description": "No input validation",
                    "severity": "medium",
                    "remediation_cost": "1 person-day"
                }
            ],
            "prevention_strategies": [
                "Add comprehensive input validation",
                "Implement proper error handling"
            ]
        },
        "recommendations": {
            "immediate_actions": ["Add validation", "Improve error handling"],
            "architectural_changes": ["Implement strategy pattern", "Separate concerns"],
            "best_practices": ["Use dependency injection", "Add comprehensive testing"]
        }
    }
    response = AIMessage(content=json.dumps(response_data))
    response.response_metadata = {'usage': {'total_tokens': 1300}}
    return response


@pytest.mark.asyncio
async def test_extension_expert_node_success(sample_state, sample_llm_response, mock_factory):
    """Test extension expert node successful execution."""
    with patch('app.core.langgraph.agents.extension_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.extension_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = sample_llm_response

        result = await extension_expert_node(sample_state)

        assert "extension_output" in result
        assert "messages" in result
        assert "total_tokens" in result
        assert "total_cost" in result

        extension_output = result["extension_output"]
        assert "extensibility_analysis" in extension_output
        assert "modularity_improvements" in extension_output
        assert "future_evolution" in extension_output
        assert "technical_debt_assessment" in extension_output
        assert "recommendations" in extension_output

        # Verify extensibility analysis structure
        analysis = extension_output["extensibility_analysis"]
        assert "current_extensibility_score" in analysis
        assert "extension_points" in analysis
        assert "limitations" in analysis
        assert analysis["current_extensibility_score"] == "5/10"
        assert len(analysis["extension_points"]) > 0

        # Verify token counting
        assert result["total_tokens"] > sample_state["total_tokens"]
        assert result["total_cost"] > sample_state["total_cost"]


@pytest.mark.asyncio
async def test_extension_expert_node_json_parse_error(sample_state, mock_factory):
    """Test extension expert node with JSON parsing error."""
    invalid_response = AIMessage(content="Invalid JSON response")
    invalid_response.response_metadata = {"usage": {"total_tokens": 100}}

    with patch('app.core.langgraph.agents.extension_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.extension_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = invalid_response

        result = await extension_expert_node(sample_state)

        assert "extension_output" in result
        extension_output = result["extension_output"]
        assert "error" in extension_output
        assert "raw_response" in extension_output
        assert extension_output["error"] == "Failed to parse JSON response"


@pytest.mark.asyncio
async def test_extension_expert_node_llm_failure(sample_state):
    """Test extension expert node with LLM call failure."""
    with patch('app.core.langgraph.agents.extension_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm:
        mock_llm.side_effect = Exception("LLM failed")

        result = await extension_expert_node(sample_state)

        assert "errors" in result
        assert "retry_count" in result
        assert len(result["errors"]) > 0
        assert "Extension Expert failed" in result["errors"][0]
        assert result["retry_count"] == 1


@pytest.mark.asyncio
async def test_extension_expert_node_empty_code_output(sample_state, mock_factory):
    """Test extension expert node with empty code output."""
    sample_state["code_output"] = {}

    mock_response = AIMessage(
        content=json.dumps({
            "extensibility_analysis": {
                "current_extensibility_score": "2/10",
                "extension_points": [],
                "limitations": []
            },
            "modularity_improvements": [],
            "future_evolution": {
                "short_term_enhancements": [],
                "long_term_vision": {}
            },
            "technical_debt_assessment": {
                "current_debt_items": [],
                "prevention_strategies": []
            },
            "recommendations": {
                "immediate_actions": [],
                "architectural_changes": [],
                "best_practices": []
            }
        }),
        response_metadata={"usage": {"total_tokens": 200}}
    )

    with patch('app.core.langgraph.agents.extension_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.extension_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = mock_response

        result = await extension_expert_node(sample_state)

        assert "extension_output" in result
        extension_output = result["extension_output"]
        assert "extensibility_analysis" in extension_output
        assert extension_output["extensibility_analysis"]["current_extensibility_score"] == "2/10"


@pytest.mark.asyncio
async def test_extension_expert_node_token_extraction_fallback(sample_state, mock_factory):
    """Test token extraction fallback when metadata is missing."""
    mock_response = AIMessage(content='{"extensibility_analysis": {"current_extensibility_score": "5/10"}}')
    # No response_metadata to test fallback

    with patch('app.core.langgraph.agents.extension_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.extension_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = mock_response

        result = await extension_expert_node(sample_state)

        assert "total_tokens" in result
        # Should use fallback calculation (content length // 4)
        assert result["total_tokens"] > sample_state["total_tokens"]


@pytest.mark.asyncio
async def test_extension_expert_node_cost_calculation(sample_state, mock_factory):
    """Test accurate cost calculation."""
    mock_response = AIMessage(
        content='{"extensibility_analysis": {"current_extensibility_score": "7/10"}}',
        response_metadata={"usage": {"total_tokens": 1500}}
    )

    with patch('app.core.langgraph.agents.extension_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.extension_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = mock_response

        result = await extension_expert_node(sample_state)

        expected_cost = 1500 * 0.00001  # 0.015
        assert abs(result["total_cost"] - (sample_state["total_cost"] + expected_cost)) < 0.0001


@pytest.mark.asyncio
async def test_extension_expert_node_metrics_accumulation(sample_state, mock_factory):
    """Test proper accumulation of tokens and cost metrics."""
    sample_state["total_tokens"] = 500
    sample_state["total_cost"] = 0.005

    mock_response = AIMessage(
        content='{"extensibility_analysis": {"current_extensibility_score": "6/10"}}',
        response_metadata={"usage": {"total_tokens": 800}}
    )

    with patch('app.core.langgraph.agents.extension_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.extension_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = mock_response

        result = await extension_expert_node(sample_state)

        assert result["total_tokens"] == 1300  # 500 + 800
        assert abs(result["total_cost"] - 0.013) < 0.0001  # 0.005 + 0.008


@pytest.mark.asyncio
async def test_extension_expert_node_comprehensive_analysis_structure(sample_state, mock_factory):
    """Test that the extension output has comprehensive analysis structure."""
    response_data = {
        "extensibility_analysis": {
            "current_extensibility_score": "8/10",
            "extension_points": [
                {
                    "component": "scheduling_engine",
                    "extension_type": "plugin",
                    "ease_of_extension": "easy",
                    "description": "Support for custom scheduling algorithms"
                }
            ],
            "limitations": []
        },
        "modularity_improvements": [
            {
                "current_structure": "tightly coupled components",
                "suggested_refactor": "dependency injection",
                "benefits": ["testability", "flexibility"],
                "implementation_effort": "medium"
            }
        ],
        "future_evolution": {
            "short_term_enhancements": [
                {
                    "feature": "real-time monitoring",
                    "priority": "medium",
                    "estimated_effort": "5 days",
                    "dependencies": ["monitoring_lib"]
                }
            ],
            "long_term_vision": {
                "direction": "AI-powered optimization",
                "potential_features": ["ml_integration", "auto_tuning"],
                "architecture_evolution": "microservices"
            }
        },
        "technical_debt_assessment": {
            "current_debt_items": [
                {
                    "category": "performance",
                    "description": "inefficient algorithm",
                    "severity": "low",
                    "remediation_cost": "2 days"
                }
            ],
            "prevention_strategies": ["code_reviews", "automated_testing"]
        },
        "recommendations": {
            "immediate_actions": ["refactor_core"],
            "architectural_changes": ["add_abstraction_layer"],
            "best_practices": ["solid_principles", "clean_code"]
        }
    }

    mock_response = AIMessage(content=json.dumps(response_data))
    mock_response.response_metadata = {"usage": {"total_tokens": 1000}}

    with patch('app.core.langgraph.agents.extension_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.extension_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = mock_response

        result = await extension_expert_node(sample_state)

        extension_output = result["extension_output"]

        # Verify comprehensive structure
        assert "extensibility_analysis" in extension_output
        assert "modularity_improvements" in extension_output
        assert "future_evolution" in extension_output
        assert "technical_debt_assessment" in extension_output
        assert "recommendations" in extension_output

        # Verify detailed analysis
        analysis = extension_output["extensibility_analysis"]
        assert len(analysis["extension_points"]) > 0
        assert "component" in analysis["extension_points"][0]
        assert "extension_type" in analysis["extension_points"][0]
        assert "ease_of_extension" in analysis["extension_points"][0]

        # Verify improvement suggestions
        improvements = extension_output["modularity_improvements"]
        assert len(improvements) > 0
        assert "suggested_refactor" in improvements[0]
        assert "benefits" in improvements[0]
        assert "implementation_effort" in improvements[0]

        # Verify future evolution
        evolution = extension_output["future_evolution"]
        assert "short_term_enhancements" in evolution
        assert "long_term_vision" in evolution
        assert len(evolution["short_term_enhancements"]) > 0

        # Verify technical debt assessment
        debt = extension_output["technical_debt_assessment"]
        assert "current_debt_items" in debt
        assert "prevention_strategies" in debt
        assert len(debt["prevention_strategies"]) > 0

        # Verify recommendations
        recommendations = extension_output["recommendations"]
        assert "immediate_actions" in recommendations
        assert "architectural_changes" in recommendations
        assert "best_practices" in recommendations
        assert len(recommendations["best_practices"]) > 0