"""Unit tests for Orchestrator agent node."""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
from langchain_core.messages import AIMessage

from backend.app.core.langgraph.agents.orchestrator import orchestrator_node
from backend.app.core.langgraph.state import WorkflowState, create_initial_state


@pytest.fixture
def mock_model_adapter():
    """Create a mock model adapter."""
    adapter = MagicMock()
    adapter.model_name = "test-model"
    return adapter


@pytest.fixture
def mock_factory(mock_model_adapter):
    """Create a mock ModelFactory."""
    factory = MagicMock()
    factory.get_model.return_value = mock_model_adapter
    return factory


@pytest.fixture
def sample_state():
    """Create a sample workflow state."""
    return create_initial_state(
        problem_description="Optimize delivery routes for 100 vehicles",
        thread_id="test-thread-123",
        domain="logistics",
        constraints=["Real-time traffic", "Electric vehicles"]
    )


@pytest.fixture
def sample_llm_response():
    """Sample LLM response in JSON format."""
    response_data = {
        "problem_analysis": {
            "summary": "Vehicle routing optimization for electric fleet",
            "key_challenges": [
                "Large-scale optimization",
                "Real-time traffic integration",
                "Battery range constraints"
            ],
            "domain": "logistics",
            "complexity_level": "high"
        },
        "workflow_plan": {
            "approach": "Multi-objective optimization",
            "phases": [
                {
                    "phase": "P1",
                    "description": "Algorithm selection",
                    "expected_outputs": ["Selected routing algorithm"]
                }
            ]
        },
        "task_assignments": {
            "algorithm_expert": "Recommend VRP variants",
            "constraint_expert": "Model battery range constraints",
            "objective_expert": "Define multi-objective optimization"
        },
        "success_criteria": {
            "functional_requirements": ["Handle 100+ vehicles"],
            "performance_targets": ["Route computation < 30 seconds"],
            "quality_standards": ["Test coverage > 80%"]
        },
        "estimated_complexity": {
            "algorithm_complexity": "NP-hard combinatorial optimization",
            "implementation_complexity": "Medium-high",
            "estimated_time": "2-3 weeks"
        }
    }
    return AIMessage(content=json.dumps(response_data))


@pytest.mark.asyncio
async def test_orchestrator_node_success(
    sample_state,
    sample_llm_response,
    mock_factory,
    mock_model_adapter
):
    """Test successful orchestrator node execution."""
    # Mock the file read for prompt
    mock_prompt = "You are an Orchestrator Agent..."

    # Mock LangChain components
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = sample_llm_response

    with patch('backend.app.core.langgraph.agents.orchestrator.ModelFactory.get_instance', return_value=mock_factory), \
         patch('backend.app.core.langgraph.agents.orchestrator.open', mock_open(read_data=mock_prompt)), \
         patch('backend.app.core.langgraph.agents.orchestrator.ChatPromptTemplate') as mock_prompt_template:

        # Configure mock prompt template
        mock_prompt_instance = MagicMock()
        mock_prompt_template.from_messages.return_value = mock_prompt_instance
        mock_prompt_instance.__or__ = lambda self, other: mock_chain

        # Execute node
        result = await orchestrator_node(sample_state)

        # Verify results
        assert "orchestrator_output" in result
        assert result["current_phase"] == "P1"
        assert "messages" in result
        assert len(result["messages"]) > 0

        # Verify output structure
        output = result["orchestrator_output"]
        assert "problem_analysis" in output
        assert "workflow_plan" in output
        assert "task_assignments" in output

        # Verify metrics
        assert "total_tokens" in result
        assert result["total_tokens"] > 0
        assert "total_cost" in result
        assert result["total_cost"] > 0.0


@pytest.mark.asyncio
async def test_orchestrator_node_json_parse_error(
    sample_state,
    mock_factory,
    mock_model_adapter
):
    """Test orchestrator handling of invalid JSON response."""
    # Mock invalid JSON response
    invalid_response = AIMessage(content="This is not valid JSON")

    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = invalid_response

    mock_prompt = "You are an Orchestrator Agent..."

    with patch('backend.app.core.langgraph.agents.orchestrator.ModelFactory.get_instance', return_value=mock_factory), \
         patch('backend.app.core.langgraph.agents.orchestrator.open', mock_open(read_data=mock_prompt)), \
         patch('backend.app.core.langgraph.agents.orchestrator.ChatPromptTemplate') as mock_prompt_template:

        mock_prompt_instance = MagicMock()
        mock_prompt_template.from_messages.return_value = mock_prompt_instance
        mock_prompt_instance.__or__ = lambda self, other: mock_chain

        # Execute node
        result = await orchestrator_node(sample_state)

        # Should still return result with error handling
        assert "orchestrator_output" in result
        assert "error" in result["orchestrator_output"]
        assert "raw_response" in result["orchestrator_output"]


@pytest.mark.asyncio
async def test_orchestrator_node_llm_failure(sample_state, mock_factory):
    """Test orchestrator handling of LLM call failure."""
    mock_factory.get_model.side_effect = Exception("LLM call failed")

    mock_prompt = "You are an Orchestrator Agent..."

    with patch('backend.app.core.langgraph.agents.orchestrator.ModelFactory.get_instance', return_value=mock_factory), \
         patch('backend.app.core.langgraph.agents.orchestrator.open', mock_open(read_data=mock_prompt)):

        # Execute node
        result = await orchestrator_node(sample_state)

        # Should return error information
        assert "errors" in result
        assert len(result["errors"]) > 0
        assert "Orchestrator failed" in result["errors"][0]
        assert "retry_count" in result


@pytest.mark.asyncio
async def test_orchestrator_node_no_model(sample_state):
    """Test orchestrator when no model adapter is available."""
    mock_factory = MagicMock()
    mock_factory.get_model.return_value = None

    mock_prompt = "You are an Orchestrator Agent..."

    with patch('backend.app.core.langgraph.agents.orchestrator.ModelFactory.get_instance', return_value=mock_factory), \
         patch('backend.app.core.langgraph.agents.orchestrator.open', mock_open(read_data=mock_prompt)):

        # Execute node
        result = await orchestrator_node(sample_state)

        # Should return error
        assert "errors" in result
        assert any("No model adapter available" in err for err in result["errors"])


def test_create_initial_state():
    """Test initial state creation."""
    state = create_initial_state(
        problem_description="Test problem",
        thread_id="test-123",
        domain="test-domain",
        constraints=["constraint1", "constraint2"]
    )

    assert state["problem_description"] == "Test problem"
    assert state["thread_id"] == "test-123"
    assert state["domain"] == "test-domain"
    assert state["constraints"] == ["constraint1", "constraint2"]
    assert state["current_phase"] == "P0"
    assert state["total_tokens"] == 0
    assert state["total_cost"] == 0.0
    assert state["errors"] == []
