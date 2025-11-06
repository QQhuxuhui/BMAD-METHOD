"""Unit tests for Quality Expert Agent Node."""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from langchain_core.messages import AIMessage

from app.core.langgraph.agents.quality_expert import quality_expert_node
from app.core.langgraph.state import create_initial_state


@pytest.fixture
def sample_state():
    """Create sample workflow state for testing."""
    state = create_initial_state(
        problem_description="Optimize production scheduling for manufacturing plant",
        thread_id="test-thread-123",
        domain="manufacturing"
    )
    # Add all previous agent outputs
    state["orchestrator_output"] = {
        "problem_analysis": {"complexity": "medium", "approach": "optimization"}
    }
    state["algorithm_output"] = {
        "algorithm_recommendations": [{"name": "genetic_algorithm", "suitability": "high"}]
    }
    state["constraint_output"] = {
        "constraint_categories": {"hard_constraints": ["capacity"], "soft_constraints": ["preferences"]}
    }
    state["objective_output"] = {
        "primary_objectives": [{"name": "minimize_cost", "weight": 0.7}]
    }
    state["domain_output"] = {
        "domain_knowledge": {"best_practices": ["just_in_time"], "standards": ["ISO_9001"]}
    }
    state["code_output"] = {
        "implementation_code": "class Scheduler: pass",
        "dependencies": ["numpy"],
        "unit_tests": "def test_scheduler(): pass"
    }
    state["extension_output"] = {
        "extensibility_analysis": {"current_extensibility_score": "7/10"}
    }
    state["total_tokens"] = 2000
    state["total_cost"] = 0.02
    return state


@pytest.fixture
def mock_factory():
    """Create a mock ModelFactory."""
    factory = MagicMock()
    return factory


@pytest.fixture
def sample_llm_response():
    """Sample LLM response with quality assessment."""
    response_data = {
        "quality_assessment": {
            "overall_quality_score": "8/10",
            "solution_completeness": "85%",
            "problem_alignment_score": "9/10",
            "implementation_quality_score": "7/10",
            "readability_score": "8/10",
            "maintainability_score": "7/10"
        },
        "component_review": {
            "orchestrator": {
                "quality_score": "9/10",
                "strengths": ["Clear problem decomposition", "Well-structured analysis"],
                "weaknesses": ["Could benefit from more detailed risk assessment"],
                "status": "excellent"
            },
            "algorithm_expert": {
                "quality_score": "8/10",
                "strengths": ["Good algorithm selection", "Thorough analysis"],
                "weaknesses": ["Limited performance benchmarks"],
                "status": "good"
            },
            "constraint_expert": {
                "quality_score": "7/10",
                "strengths": ["Comprehensive constraint identification"],
                "weaknesses": ["Could be more detailed"],
                "status": "good"
            },
            "objective_expert": {
                "quality_score": "8/10",
                "strengths": ["Clear objective definition"],
                "weaknesses": ["Limited multi-objective analysis"],
                "status": "good"
            },
            "domain_expert": {
                "quality_score": "9/10",
                "strengths": ["Strong domain knowledge", "Practical recommendations"],
                "weaknesses": ["None significant"],
                "status": "excellent"
            },
            "code_implementation": {
                "quality_score": "7/10",
                "strengths": ["Functional implementation", "Good structure"],
                "weaknesses": ["Limited error handling"],
                "status": "good"
            },
            "extension_analysis": {
                "quality_score": "8/10",
                "strengths": ["Thorough extensibility analysis"],
                "weaknesses": ["Could include more specific examples"],
                "status": "good"
            }
        },
        "acceptance_criteria_check": {
            "criteria_1": {
                "description": "8个智能体节点全部实现，包含完整的异步函数逻辑",
                "status": "met",
                "evidence": "All 8 agent nodes implemented with async functions",
                "gaps": []
            },
            "criteria_2": {
                "description": "每个节点有对应的Prompt模板（markdown格式，包含清晰的输出规范）",
                "status": "met",
                "evidence": "All prompt templates created in markdown format",
                "gaps": []
            },
            "criteria_3": {
                "description": "每个节点能正确调用Model Adapter并解析LLM JSON输出",
                "status": "met",
                "evidence": "All nodes use ModelFactory and JSON parsing",
                "gaps": []
            },
            "criteria_4": {
                "description": "每个节点有单元测试，覆盖率>80%",
                "status": "met",
                "evidence": "Comprehensive unit tests created for all nodes",
                "gaps": []
            },
            "criteria_5": {
                "description": "所有节点正确更新WorkflowState",
                "status": "met",
                "evidence": "All nodes update WorkflowState correctly",
                "gaps": []
            },
            "criteria_6": {
                "description": "错误处理和重试机制健全",
                "status": "met",
                "evidence": "Robust error handling and retry mechanisms implemented",
                "gaps": []
            }
        },
        "quality_issues": [
            {
                "severity": "medium",
                "category": "maintainability",
                "description": "Limited error handling in implementation code",
                "impact": "May cause runtime issues in production",
                "recommendation": "Add comprehensive try-catch blocks and validation",
                "priority": "short_term"
            }
        ],
        "improvement_recommendations": [
            {
                "area": "error handling",
                "recommendation": "Implement comprehensive error handling throughout the solution",
                "benefit": "Improved reliability and debugging capability",
                "effort": "medium",
                "priority": "high"
            }
        ],
        "final_assessment": {
            "approval_status": "conditional_approval",
            "confidence_level": "high",
            "readiness_for_production": "almost_ready",
            "summary": "Solution demonstrates good quality with minor areas for improvement",
            "next_steps": ["Implement recommended error handling improvements", "Add more comprehensive documentation"]
        }
    }
    response = AIMessage(content=json.dumps(response_data))
    response.response_metadata = {'usage': {'total_tokens': 1800}}
    return response


@pytest.mark.asyncio
async def test_quality_expert_node_success(sample_state, sample_llm_response, mock_factory):
    """Test quality expert node successful execution."""
    with patch('app.core.langgraph.agents.quality_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.quality_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = sample_llm_response

        result = await quality_expert_node(sample_state)

        assert "quality_output" in result
        assert "messages" in result
        assert "total_tokens" in result
        assert "total_cost" in result
        assert "current_phase" in result

        # Verify phase transition to P4
        assert result["current_phase"] == "P4"

        quality_output = result["quality_output"]
        assert "quality_assessment" in quality_output
        assert "component_review" in quality_output
        assert "acceptance_criteria_check" in quality_output
        assert "quality_issues" in quality_output
        assert "improvement_recommendations" in quality_output
        assert "final_assessment" in quality_output

        # Verify quality assessment structure
        assessment = quality_output["quality_assessment"]
        assert "overall_quality_score" in assessment
        assert "solution_completeness" in assessment
        assert "problem_alignment_score" in assessment
        assert assessment["overall_quality_score"] == "8/10"

        # Verify component review
        component_review = quality_output["component_review"]
        assert "orchestrator" in component_review
        assert "algorithm_expert" in component_review
        assert "code_implementation" in component_review
        assert "extension_analysis" in component_review

        # Verify acceptance criteria check
        acceptance_check = quality_output["acceptance_criteria_check"]
        assert "criteria_1" in acceptance_check
        assert "criteria_6" in acceptance_check
        assert acceptance_check["criteria_1"]["status"] == "met"

        # Verify final assessment
        final_assessment = quality_output["final_assessment"]
        assert "approval_status" in final_assessment
        assert "confidence_level" in final_assessment
        assert "readiness_for_production" in final_assessment
        assert final_assessment["approval_status"] == "conditional_approval"
        assert final_assessment["confidence_level"] == "high"

        # Verify token counting
        assert result["total_tokens"] > sample_state["total_tokens"]
        assert result["total_cost"] > sample_state["total_cost"]


@pytest.mark.asyncio
async def test_quality_expert_node_json_parse_error(sample_state, mock_factory):
    """Test quality expert node with JSON parsing error."""
    invalid_response = AIMessage(content="Invalid JSON response")
    invalid_response.response_metadata = {"usage": {"total_tokens": 200}}

    with patch('app.core.langgraph.agents.quality_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.quality_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = invalid_response

        result = await quality_expert_node(sample_state)

        assert "quality_output" in result
        quality_output = result["quality_output"]
        assert "error" in quality_output
        assert "raw_response" in quality_output
        assert quality_output["error"] == "Failed to parse JSON response"


@pytest.mark.asyncio
async def test_quality_expert_node_llm_failure(sample_state):
    """Test quality expert node with LLM call failure."""
    with patch('app.core.langgraph.agents.quality_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm:
        mock_llm.side_effect = Exception("LLM failed")

        result = await quality_expert_node(sample_state)

        assert "errors" in result
        assert "retry_count" in result
        assert len(result["errors"]) > 0
        assert "Quality Expert failed" in result["errors"][0]
        assert result["retry_count"] == 1


@pytest.mark.asyncio
async def test_quality_expert_node_minimal_inputs(sample_state, mock_factory):
    """Test quality expert node with minimal inputs."""
    # Clear all outputs except problem description
    for key in ["orchestrator_output", "algorithm_output", "constraint_output",
                "objective_output", "domain_output", "code_output", "extension_output"]:
        sample_state[key] = {}

    mock_response = AIMessage(
        content=json.dumps({
            "quality_assessment": {
                "overall_quality_score": "3/10",
                "solution_completeness": "20%",
                "problem_alignment_score": "4/10",
                "implementation_quality_score": "2/10",
                "readability_score": "3/10",
                "maintainability_score": "2/10"
            },
            "component_review": {},
            "acceptance_criteria_check": {},
            "quality_issues": [],
            "improvement_recommendations": [],
            "final_assessment": {
                "approval_status": "needs_improvement",
                "confidence_level": "low",
                "readiness_for_production": "no",
                "summary": "Solution incomplete, significant work needed",
                "next_steps": ["Implement missing components", "Add comprehensive testing"]
            }
        }),
        response_metadata={"usage": {"total_tokens": 500}}
    )

    with patch('app.core.langgraph.agents.quality_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.quality_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = mock_response

        result = await quality_expert_node(sample_state)

        assert "quality_output" in result
        assert result["current_phase"] == "P4"

        quality_output = result["quality_output"]
        final_assessment = quality_output["final_assessment"]
        assert final_assessment["approval_status"] == "needs_improvement"
        assert final_assessment["readiness_for_production"] == "no"


@pytest.mark.asyncio
async def test_quality_expert_node_token_extraction_fallback(sample_state, mock_factory):
    """Test token extraction fallback when metadata is missing."""
    mock_response = AIMessage(content='{"quality_assessment": {"overall_quality_score": "7/10"}}')
    # No response_metadata to test fallback

    with patch('app.core.langgraph.agents.quality_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.quality_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = mock_response

        result = await quality_expert_node(sample_state)

        assert "total_tokens" in result
        # Should use fallback calculation (content length // 4)
        assert result["total_tokens"] > sample_state["total_tokens"]


@pytest.mark.asyncio
async def test_quality_expert_node_cost_calculation(sample_state, mock_factory):
    """Test accurate cost calculation."""
    mock_response = AIMessage(
        content='{"quality_assessment": {"overall_quality_score": "8/10"}}',
        response_metadata={"usage": {"total_tokens": 2000}}
    )

    with patch('app.core.langgraph.agents.quality_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.quality_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = mock_response

        result = await quality_expert_node(sample_state)

        expected_cost = 2000 * 0.00001  # 0.02
        assert abs(result["total_cost"] - (sample_state["total_cost"] + expected_cost)) < 0.0001


@pytest.mark.asyncio
async def test_quality_expert_node_metrics_accumulation(sample_state, mock_factory):
    """Test proper accumulation of tokens and cost metrics."""
    sample_state["total_tokens"] = 1500
    sample_state["total_cost"] = 0.015

    mock_response = AIMessage(
        content='{"quality_assessment": {"overall_quality_score": "9/10"}}',
        response_metadata={"usage": {"total_tokens": 1200}}
    )

    with patch('app.core.langgraph.agents.quality_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.quality_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = mock_response

        result = await quality_expert_node(sample_state)

        assert result["total_tokens"] == 2700  # 1500 + 1200
        assert abs(result["total_cost"] - 0.027) < 0.0001  # 0.015 + 0.012


@pytest.mark.asyncio
async def test_quality_expert_node_comprehensive_assessment_structure(sample_state, mock_factory):
    """Test that the quality output has comprehensive assessment structure."""
    response_data = {
        "quality_assessment": {
            "overall_quality_score": "9/10",
            "solution_completeness": "95%",
            "problem_alignment_score": "10/10",
            "implementation_quality_score": "8/10",
            "readability_score": "9/10",
            "maintainability_score": "8/10"
        },
        "component_review": {
            "orchestrator": {
                "quality_score": "10/10",
                "strengths": ["Excellent analysis", "Clear structure"],
                "weaknesses": [],
                "status": "excellent"
            },
            "algorithm_expert": {
                "quality_score": "9/10",
                "strengths": ["Thorough algorithm analysis"],
                "weaknesses": ["Minor optimization opportunities"],
                "status": "excellent"
            },
            "code_implementation": {
                "quality_score": "8/10",
                "strengths": ["Clean code", "Good documentation"],
                "weaknesses": ["Could benefit from more tests"],
                "status": "good"
            }
        },
        "acceptance_criteria_check": {
            "criteria_1": {
                "description": "8个智能体节点全部实现，包含完整的异步函数逻辑",
                "status": "met",
                "evidence": "All nodes implemented correctly",
                "gaps": []
            },
            "criteria_4": {
                "description": "每个节点有单元测试，覆盖率>80%",
                "status": "met",
                "evidence": "Comprehensive test suite with >80% coverage",
                "gaps": []
            }
        },
        "quality_issues": [
            {
                "severity": "low",
                "category": "documentation",
                "description": "Some API endpoints lack detailed documentation",
                "impact": "Minor impact on developer experience",
                "recommendation": "Add comprehensive API documentation",
                "priority": "long_term"
            }
        ],
        "improvement_recommendations": [
            {
                "area": "performance",
                "recommendation": "Add performance monitoring and metrics",
                "benefit": "Better observability and optimization",
                "effort": "medium",
                "priority": "medium"
            }
        ],
        "final_assessment": {
            "approval_status": "approved",
            "confidence_level": "high",
            "readiness_for_production": "yes",
            "summary": "High-quality solution ready for production deployment",
            "next_steps": ["Deploy to production", "Monitor performance"]
        }
    }

    mock_response = AIMessage(content=json.dumps(response_data))
    mock_response.response_metadata = {"usage": {"total_tokens": 1500}}

    with patch('app.core.langgraph.agents.quality_expert._call_llm_with_retry',
               new_callable=AsyncMock) as mock_llm, \
         patch('app.core.langgraph.agents.quality_expert.ModelFactory.get_instance',
               return_value=mock_factory):
        mock_llm.return_value = mock_response

        result = await quality_expert_node(sample_state)

        quality_output = result["quality_output"]

        # Verify comprehensive structure
        assert "quality_assessment" in quality_output
        assert "component_review" in quality_output
        assert "acceptance_criteria_check" in quality_output
        assert "quality_issues" in quality_output
        assert "improvement_recommendations" in quality_output
        assert "final_assessment" in quality_output

        # Verify detailed quality assessment
        assessment = quality_output["quality_assessment"]
        assert assessment["overall_quality_score"] == "9/10"
        assert assessment["solution_completeness"] == "95%"
        assert assessment["problem_alignment_score"] == "10/10"

        # Verify component review details
        components = quality_output["component_review"]
        orchestrator = components["orchestrator"]
        assert orchestrator["quality_score"] == "10/10"
        assert len(orchestrator["strengths"]) > 0
        assert orchestrator["status"] == "excellent"

        # Verify acceptance criteria
        criteria = quality_output["acceptance_criteria_check"]
        assert criteria["criteria_1"]["status"] == "met"
        assert "evidence" in criteria["criteria_1"]

        # Verify quality issues
        issues = quality_output["quality_issues"]
        assert len(issues) > 0
        issue = issues[0]
        assert "severity" in issue
        assert "category" in issue
        assert "description" in issue
        assert "recommendation" in issue

        # Verify improvement recommendations
        recommendations = quality_output["improvement_recommendations"]
        assert len(recommendations) > 0
        rec = recommendations[0]
        assert "area" in rec
        assert "recommendation" in rec
        assert "benefit" in rec
        assert "effort" in rec

        # Verify final assessment
        final = quality_output["final_assessment"]
        assert final["approval_status"] == "approved"
        assert final["readiness_for_production"] == "yes"
        assert "summary" in final
        assert "next_steps" in final
        assert len(final["next_steps"]) > 0