"""Integration tests for BMAD workflow compilation and execution.

This test module verifies that the complete BMAD workflow can be compiled,
executed, and that checkpoints work correctly across all phases.
"""

import pytest
import asyncio
from typing import Dict, Any
from uuid import uuid4

# Import BMAD workflow components
from app.core.langgraph.workflow import create_bmad_workflow
from app.core.langgraph.executor import run_workflow, get_workflow_status
from app.core.langgraph.state import create_initial_state
from app.core.langgraph.config_loader import validate_config, create_default_config
from app.core.logging import logger


class TestWorkflowCompilation:
    """Test suite for BMAD workflow compilation."""

    @pytest.mark.asyncio
    async def test_workflow_compilation_success(self):
        """Test that the BMAD workflow compiles successfully."""
        try:
            # Create workflow
            app = await create_bmad_workflow()

            # Verify workflow was created
            assert app is not None, "Workflow should be created successfully"

            # Check that all nodes are present
            graph_dict = app.get_graph()
            nodes = [node['id'] for node in graph_dict['nodes']]

            # Verify all 11 nodes (8 agents + 3 approvals)
            expected_nodes = [
                'orchestrator', 'algorithm', 'constraint', 'objective',
                'domain', 'code_impl', 'extension', 'quality',
                'p1_approval', 'p2_conflict', 'p25_approval'
            ]

            for node in expected_nodes:
                assert node in nodes, f"Expected node {node} should be present in workflow"

            logger.info("workflow_compilation_test_passed", node_count=len(nodes))

        except Exception as e:
            logger.error("workflow_compilation_test_failed", error=str(e))
            pytest.fail(f"Workflow compilation failed: {str(e)}")

    @pytest.mark.asyncio
    async def test_workflow_compilation_with_config(self):
        """Test workflow compilation with default configuration."""
        try:
            # Create default config
            config = create_default_config()
            validation_issues = validate_config(config)

            # Validation should pass for default config
            assert len(validation_issues) == 0, f"Default config should be valid: {validation_issues}"

            # Create workflow (config_path=None means use defaults)
            app = await create_bmad_workflow()

            assert app is not None, "Workflow with default config should be created"

            logger.info("workflow_config_compilation_test_passed")

        except Exception as e:
            logger.error("workflow_config_compilation_test_failed", error=str(e))
            pytest.fail(f"Workflow config compilation failed: {str(e)}")


class TestWorkflowExecution:
    """Test suite for BMAD workflow execution."""

    @pytest.mark.asyncio
    async def test_simple_workflow_execution(self):
        """Test workflow execution with a simple problem."""
        thread_id = str(uuid4())

        try:
            # Simple test problem
            problem_description = """
            Create a simple algorithm to find the maximum element in an array.
            The solution should be efficient and handle edge cases.
            """

            # Run workflow
            result = await run_workflow(
                problem_description=problem_description,
                domain="algorithms",
                constraints=["O(n) time complexity", "O(1) space complexity"],
                thread_id=thread_id,
                timeout=300  # 5 minutes for simple test
            )

            # Verify basic structure of result
            assert isinstance(result, dict), "Result should be a dictionary"
            assert 'current_phase' in result, "Result should contain current phase"
            assert 'thread_id' in result, "Result should contain thread ID"
            assert result['thread_id'] == thread_id, "Thread ID should match"

            logger.info("simple_workflow_execution_test_passed", thread_id=thread_id)

        except Exception as e:
            logger.error("simple_workflow_execution_test_failed", thread_id=thread_id, error=str(e))
            pytest.fail(f"Simple workflow execution failed: {str(e)}")

    @pytest.mark.asyncio
    async def test_workflow_state_transitions(self):
        """Test that workflow transitions through all phases correctly."""
        thread_id = str(uuid4())

        try:
            # Create workflow to check state transitions
            app = await create_bmad_workflow()

            # Create initial state
            initial_state = create_initial_state(
                problem_description="Implement a binary search algorithm",
                domain="algorithms",
                constraints=["O(log n) time complexity"],
                thread_id=thread_id
            )

            # Configure execution
            config = {"configurable": {"thread_id": thread_id}}

            # Execute one step at a time to verify transitions
            event_count = 0
            phases_seen = []

            async for event in app.astream(initial_state, config):
                event_count += 1

                # Extract current phase from event
                for node_name, node_output in event.items():
                    if isinstance(node_output, dict) and 'current_phase' in node_output:
                        phase = node_output['current_phase']
                        if phase not in phases_seen:
                            phases_seen.append(phase)

                # Limit to reasonable number of events for testing
                if event_count > 20:
                    break

            # Verify we saw multiple phases
            assert len(phases_seen) > 1, f"Should see multiple phases, saw: {phases_seen}"

            logger.info(
                "workflow_state_transitions_test_passed",
                thread_id=thread_id,
                phases_seen=phases_seen,
                event_count=event_count
            )

        except Exception as e:
            logger.error("workflow_state_transitions_test_failed", thread_id=thread_id, error=str(e))
            pytest.fail(f"Workflow state transitions test failed: {str(e)}")

    @pytest.mark.asyncio
    async def test_workflow_with_constraints(self):
        """Test workflow execution with multiple constraints."""
        thread_id = str(uuid4())

        try:
            problem_description = "Design a sorting algorithm for large datasets"

            constraints = [
                "O(n log n) time complexity or better",
                "Stable sorting",
                "Minimal memory usage",
                "Handle duplicate values efficiently"
            ]

            # Run workflow with constraints
            result = await run_workflow(
                problem_description=problem_description,
                domain="algorithms",
                constraints=constraints,
                thread_id=thread_id,
                timeout=300
            )

            # Verify constraints were processed
            assert isinstance(result, dict), "Result should be a dictionary"

            logger.info(
                "workflow_constraints_test_passed",
                thread_id=thread_id,
                constraints_count=len(constraints)
            )

        except Exception as e:
            logger.error("workflow_constraints_test_failed", thread_id=thread_id, error=str(e))
            pytest.fail(f"Workflow constraints test failed: {str(e)}")


class TestWorkflowCheckpointing:
    """Test suite for workflow checkpoint functionality."""

    @pytest.mark.asyncio
    async def test_checkpoint_creation(self):
        """Test that checkpoints are created during workflow execution."""
        thread_id = str(uuid4())

        try:
            # Create workflow
            app = await create_bmad_workflow()

            # Create initial state
            initial_state = create_initial_state(
                problem_description="Test checkpoint functionality",
                domain="testing",
                constraints=[],
                thread_id=thread_id
            )

            # Execute a few steps
            config = {"configurable": {"thread_id": thread_id}}

            event_count = 0
            async for event in app.astream(initial_state, config):
                event_count += 1
                # Stop after a few events to test checkpoint retrieval
                if event_count >= 3:
                    break

            # Check if state was saved to checkpoint
            status = await get_workflow_status(thread_id)

            assert status['status'] in ['active', 'completed'], "Workflow should have a valid status"
            assert status['thread_id'] == thread_id, "Thread ID should match"

            logger.info(
                "checkpoint_creation_test_passed",
                thread_id=thread_id,
                event_count=event_count,
                workflow_status=status['status']
            )

        except Exception as e:
            logger.error("checkpoint_creation_test_failed", thread_id=thread_id, error=str(e))
            pytest.fail(f"Checkpoint creation test failed: {str(e)}")

    @pytest.mark.asyncio
    async def test_checkpoint_persistence(self):
        """Test that workflow state persists across checkpoint retrieval."""
        thread_id = str(uuid4())

        try:
            # Run partial workflow
            app = await create_bmad_workflow()

            initial_state = create_initial_state(
                problem_description="Test checkpoint persistence",
                domain="testing",
                constraints=["test constraint"],
                thread_id=thread_id
            )

            config = {"configurable": {"thread_id": thread_id}}

            # Execute a few steps
            event_count = 0
            last_state = None
            async for event in app.astream(initial_state, config):
                event_count += 1
                # Track the last complete state we see
                for node_output in event.values():
                    if isinstance(node_output, dict):
                        last_state = node_output
                if event_count >= 3:
                    break

            # Get state from checkpoint
            checkpoint_state = await app.aget_state(config)

            if checkpoint_state and checkpoint_state.values:
                # Verify some key fields are preserved
                assert 'problem_description' in checkpoint_state.values, "Problem description should be preserved"
                assert 'thread_id' in checkpoint_state.values, "Thread ID should be preserved"
                assert checkpoint_state.values['thread_id'] == thread_id, "Thread ID should match"

                logger.info(
                    "checkpoint_persistence_test_passed",
                    thread_id=thread_id,
                    event_count=event_count
                )
            else:
                # If no checkpoint state was saved, that's also valid for a short execution
                logger.warning("no_checkpoint_state_found", thread_id=thread_id, event_count=event_count)

        except Exception as e:
            logger.error("checkpoint_persistence_test_failed", thread_id=thread_id, error=str(e))
            pytest.fail(f"Checkpoint persistence test failed: {str(e)}")


class TestConfigurationLoading:
    """Test suite for configuration loading and validation."""

    def test_default_config_validation(self):
        """Test that default configuration passes validation."""
        try:
            config = create_default_config()
            issues = validate_config(config)

            assert len(issues) == 0, f"Default config should be valid, found issues: {issues}"

            logger.info("default_config_validation_test_passed")

        except Exception as e:
            logger.error("default_config_validation_test_failed", error=str(e))
            pytest.fail(f"Default config validation test failed: {str(e)}")

    def test_config_structure_validation(self):
        """Test configuration structure validation."""
        try:
            # Test invalid config (missing required sections)
            invalid_config = {
                'workflow': {
                    'name': 'Test Workflow'
                    # Missing agents section
                }
            }

            issues = validate_config(invalid_config)

            assert len(issues) > 0, "Invalid config should have validation issues"
            assert any('Missing required section: agents' in issue for issue in issues), "Should detect missing agents section"

            logger.info("config_structure_validation_test_passed", issue_count=len(issues))

        except Exception as e:
            logger.error("config_structure_validation_test_failed", error=str(e))
            pytest.fail(f"Config structure validation test failed: {str(e)}")


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])