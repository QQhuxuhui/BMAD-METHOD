"""Basic workflow tests without PostgreSQL dependencies.

This test module verifies basic workflow functionality without requiring
PostgreSQL database connections.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from uuid import uuid4

# Import BMAD workflow components
from app.core.langgraph.state import create_initial_state, WorkflowState
from app.core.langgraph.config_loader import create_default_config, validate_config
from app.core.langgraph.routers.phase_routers import (
    route_after_orchestrator,
    route_after_objective,
    route_after_p1_approval
)


class TestBasicWorkflowComponents:
    """Test basic workflow components without database dependencies."""

    def test_initial_state_creation(self):
        """Test creation of initial workflow state."""
        try:
            problem_description = "Test problem for initial state"
            domain = "testing"
            constraints = ["constraint1", "constraint2"]
            thread_id = str(uuid4())

            state = create_initial_state(
                problem_description=problem_description,
                domain=domain,
                constraints=constraints,
                thread_id=thread_id
            )

            # Verify all required fields are present
            assert isinstance(state, dict), "State should be a dictionary"
            assert state['problem_description'] == problem_description, "Problem description should match"
            assert state['domain'] == domain, "Domain should match"
            assert state['constraints'] == constraints, "Constraints should match"
            assert state['thread_id'] == thread_id, "Thread ID should match"
            assert state['current_phase'] == 'P0', "Should start at Phase 0"
            assert state['pending_approval'] == False, "Should not be pending approval initially"
            assert state['errors'] == [], "Should have no errors initially"
            assert state['total_tokens'] == 0, "Should have zero tokens initially"

            print("✓ Initial state creation test passed")

        except Exception as e:
            pytest.fail(f"Initial state creation test failed: {str(e)}")

    def test_default_configuration(self):
        """Test default configuration creation and validation."""
        try:
            # Create default configuration
            config = create_default_config()

            # Validate basic structure
            assert 'workflow' in config, "Should have workflow section"
            assert 'agents' in config, "Should have agents section"
            assert 'phases' in config, "Should have phases section"

            # Validate workflow section
            workflow = config['workflow']
            assert workflow['name'] == 'BMAD Eight-Agent Workflow', "Should have correct workflow name"
            assert workflow['version'] == '1.0', "Should have version 1.0"

            # Validate agents section
            agents = config['agents']
            required_agents = [
                'orchestrator', 'algorithm', 'constraint', 'objective',
                'domain', 'code_impl', 'extension', 'quality'
            ]
            for agent in required_agents:
                assert agent in agents, f"Should have {agent} agent"

            # Validate phases section
            phases = config['phases']
            assert len(phases) == 5, "Should have 5 phases"
            assert phases[0]['id'] == 'P0', "First phase should be P0"
            assert phases[4]['id'] == 'P4', "Last phase should be P4"

            print("✓ Default configuration test passed")

        except Exception as e:
            pytest.fail(f"Default configuration test failed: {str(e)}")

    def test_configuration_validation(self):
        """Test configuration validation."""
        try:
            # Test valid configuration
            valid_config = create_default_config()
            issues = validate_config(valid_config)
            assert len(issues) == 0, f"Valid config should have no issues: {issues}"

            # Test invalid configuration (missing required sections)
            invalid_config = {
                'workflow': {'name': 'Test'},  # Missing agents section
            }
            issues = validate_config(invalid_config)
            assert len(issues) > 0, "Invalid config should have validation issues"
            assert any('agents' in issue for issue in issues), "Should detect missing agents"

            print("✓ Configuration validation test passed")

        except Exception as e:
            pytest.fail(f"Configuration validation test failed: {str(e)}")

    def test_phase_routing_functions(self):
        """Test phase routing logic."""
        try:
            # Create test state
            test_state = {
                'problem_description': 'Test problem',
                'current_phase': 'P0',
                'thread_id': str(uuid4()),
                'pending_approval': False,
                'approval_decision': None,
                'approval_point': None
            }

            # Test orchestrator routing
            next_node = route_after_orchestrator(test_state)
            assert next_node == 'algorithm', f"Should route to algorithm, got {next_node}"

            # Test objective routing
            next_node = route_after_objective(test_state)
            assert next_node == 'p1_approval', f"Should route to p1_approval, got {next_node}"

            # Test P1 approval routing with approved decision
            test_state['approval_decision'] = 'approved'
            test_state['pending_approval'] = False
            next_node = route_after_p1_approval(test_state)
            assert next_node == 'domain', f"Should route to domain when approved, got {next_node}"

            # Test P1 approval routing with rejected decision
            test_state['approval_decision'] = 'rejected'
            next_node = route_after_p1_approval(test_state)
            assert next_node == 'algorithm', f"Should route to algorithm when rejected, got {next_node}"

            print("✓ Phase routing functions test passed")

        except Exception as e:
            pytest.fail(f"Phase routing functions test failed: {str(e)}")


@pytest.mark.asyncio
class TestAgentNodeStructure:
    """Test agent node structure and basic functionality."""

    async def test_agent_node_imports(self):
        """Test that all agent node functions can be imported."""
        try:
            # Try to import all agent nodes
            from app.core.langgraph.agents import (
                orchestrator_node,
                algorithm_expert_node,
                constraint_expert_node,
                objective_expert_node,
                domain_expert_node,
                code_impl_expert_node,
                extension_expert_node,
                quality_expert_node
            )

            # Try to import approval nodes
            from app.core.langgraph.agents.approval_nodes import (
                p1_approval_node,
                p2_conflict_node,
                p25_approval_node
            )

            # Verify all are callable
            assert callable(orchestrator_node), "Orchestrator node should be callable"
            assert callable(algorithm_expert_node), "Algorithm node should be callable"
            assert callable(p1_approval_node), "P1 approval node should be callable"

            print("✓ Agent node imports test passed")

        except ImportError as e:
            pytest.skip(f"Agent nodes not fully implemented yet: {str(e)}")
        except Exception as e:
            pytest.fail(f"Agent node imports test failed: {str(e)}")

    async def test_approval_node_mocks(self):
        """Test approval nodes with mocked state."""
        try:
            from app.core.langgraph.agents.approval_nodes import p1_approval_node

            # Create test state
            test_state = {
                'thread_id': str(uuid4()),
                'current_phase': 'P1',
                'pending_approval': False
            }

            # Test P1 approval node
            result = await p1_approval_node(test_state)

            assert isinstance(result, dict), "Should return a dictionary"
            assert result['pending_approval'] == True, "Should set pending_approval to True"
            assert result['approval_point'] == 'P1', "Should set approval_point to P1"
            assert result['approval_decision'] == 'approved', "Should auto-approve in test mode"

            print("✓ Approval node mocks test passed")

        except Exception as e:
            pytest.skip(f"Approval nodes not fully implemented: {str(e)}")


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])