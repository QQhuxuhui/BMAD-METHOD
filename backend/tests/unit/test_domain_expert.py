"""Unit tests for Domain Expert agent node."""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
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


@pytest.fixture
def mock_factory():
    """Create a mock ModelFactory."""
    factory = MagicMock()
    return factory


@pytest.mark.asyncio
async def test_domain_expert_token_extraction_fallback(sample_state, mock_factory):
    """Test token extraction falls back to estimation when no metadata."""
    response = AIMessage(content=json.dumps({"domain_knowledge": {}}))

    with patch('app.core.langgraph.agents.domain_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.domain_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = response

        result = await domain_expert_node(sample_state)

        assert "total_tokens" in result
        assert result["total_tokens"] > 0


@pytest.mark.asyncio
async def test_domain_expert_cost_calculation(sample_state, mock_factory):
    """Test accurate cost calculation from token usage."""
    response = AIMessage(content=json.dumps({"domain_knowledge": {}}))
    response.response_metadata = {
        'usage': {
            'prompt_tokens': 2200,
            'completion_tokens': 1800,
            'total_tokens': 4000
        }
    }

    with patch('app.core.langgraph.agents.domain_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.domain_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = response

        result = await domain_expert_node(sample_state)

        # Verify cost calculation: 4000 tokens * 0.00001 = 0.04
        assert result["total_tokens"] == 4000
        assert abs(result["total_cost"] - 0.04) < 0.0001


@pytest.mark.asyncio
async def test_domain_expert_accumulates_metrics(sample_state, sample_llm_response, mock_factory):
    """Test that tokens and cost accumulate across calls."""
    sample_state["total_tokens"] = 1200
    sample_state["total_cost"] = 0.012

    with patch('app.core.langgraph.agents.domain_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.domain_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = sample_llm_response

        result = await domain_expert_node(sample_state)

        # Should accumulate on top of existing metrics
        assert result["total_tokens"] == 1200 + 500  # existing + new
        assert result["total_cost"] > 0.012  # existing + new cost


@pytest.mark.asyncio
async def test_domain_expert_comprehensive_knowledge(mock_factory):
    """Test domain expert with comprehensive domain knowledge."""
    state = create_initial_state(
        problem_description="Complex manufacturing optimization",
        thread_id="test-comprehensive-123",
        domain="manufacturing"
    )
    state["orchestrator_output"] = {"problem_analysis": {"complexity_level": "high"}}
    state["algorithm_output"] = {"algorithm_recommendations": [{"algorithm_name": "Genetic Algorithm"}]}
    state["constraint_output"] = {"constraint_categories": {"hard_constraints": []}}
    state["objective_output"] = {"primary_objectives": [{"objective_id": "O1"}]}

    response_data = {
        "domain_knowledge": {
            "domain_overview": "Manufacturing domain expertise",
            "key_concepts": [
                {"concept": "Production scheduling", "definition": "Scheduling production lines", "relevance": "Critical"}
            ],
            "terminology": {"term1": "definition1"}
        },
        "best_practices": [
            {"practice": "Just-in-time manufacturing", "rationale": "Reduces inventory costs"},
            {"practice": "Quality control gates", "rationale": "Ensures product quality"}
        ],
        "regulatory_requirements": [
            {"regulation": "ISO 9001", "description": "Quality management standard"},
            {"regulation": "OSHA standards", "description": "Safety requirements"}
        ],
        "risks_and_mitigations": [
            {"risk": "Equipment failure", "mitigation": "Preventive maintenance schedule"}
        ],
        "industry_standards": ["Six Sigma", "Lean Manufacturing"],
        "summary": {
            "domain_complexity": "high",
            "key_considerations": ["Quality", "Efficiency", "Safety"]
        }
    }
    response = AIMessage(content=json.dumps(response_data))
    response.response_metadata = {'usage': {'total_tokens': 800}}

    with patch('app.core.langgraph.agents.domain_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.domain_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = response

        result = await domain_expert_node(state)

        assert "domain_output" in result
        output = result["domain_output"]
        assert "domain_knowledge" in output
        assert "best_practices" in output
        assert len(output["best_practices"]) == 2
        assert "regulatory_requirements" in output
        assert len(output["regulatory_requirements"]) == 2


@pytest.mark.asyncio
async def test_domain_expert_minimal_knowledge(sample_state, mock_factory):
    """Test domain expert with minimal domain knowledge."""
    response_data = {
        "domain_knowledge": {},
        "best_practices": [],
        "summary": {
            "note": "Limited domain-specific information available"
        }
    }
    response = AIMessage(content=json.dumps(response_data))
    response.response_metadata = {'usage': {'total_tokens': 200}}

    with patch('app.core.langgraph.agents.domain_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.domain_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = response

        result = await domain_expert_node(sample_state)

        assert "domain_output" in result
        assert result["domain_output"]["domain_knowledge"] == {}


@pytest.mark.asyncio
async def test_domain_expert_without_previous_outputs(mock_factory):
    """Test domain expert with missing previous agent outputs."""
    state = create_initial_state(
        problem_description="Simple problem",
        thread_id="test-simple-456",
        domain="general"
    )
    # No previous agent outputs

    response_data = {
        "domain_knowledge": {
            "domain_overview": "General domain knowledge"
        },
        "summary": {"domain_complexity": "low"}
    }
    response = AIMessage(content=json.dumps(response_data))
    response.response_metadata = {'usage': {'total_tokens': 300}}

    with patch('app.core.langgraph.agents.domain_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.domain_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = response

        result = await domain_expert_node(state)

        # Should still succeed with missing previous outputs
        assert "domain_output" in result
        assert "total_tokens" in result