"""Integration tests for checkpoint integrity validation.

This test module verifies that the checkpoint integrity validator
correctly validates PostgreSQL checkpoint data integrity.
"""

import pytest
import asyncio
from typing import Dict, Any
from uuid import uuid4

from app.core.langgraph.checkpoint_validator import CheckpointIntegrityValidator, validate_checkpoint_integrity
from app.core.langgraph.executor import run_workflow
from app.core.langgraph.workflow import create_bmad_workflow, create_checkpointer
from app.core.langgraph.state import create_initial_state
from app.core.logging import logger


class TestCheckpointIntegrityValidator:
    """Test suite for checkpoint integrity validation."""

    @pytest.mark.asyncio
    async def test_checkpoint_structure_validation(self):
        """Test checkpoint database structure validation."""
        thread_id = str(uuid4())

        try:
            # 创建一个简单的工作流并执行几步
            app = await create_bmad_workflow()

            initial_state = create_initial_state(
                problem_description="Test checkpoint validation",
                domain="testing",
                constraints=["test constraint"],
                thread_id=thread_id
            )

            config = {"configurable": {"thread_id": thread_id}}

            # 执行几步以创建checkpoint数据
            event_count = 0
            async for event in app.astream(initial_state, config):
                event_count += 1
                if event_count >= 3:  # 只执行几步
                    break

            # 验证checkpoint结构
            checkpointer = await create_checkpointer()
            validator = CheckpointIntegrityValidator(checkpointer)

            structure_results = await validator.validate_checkpoint_structure(thread_id)

            # 验证结果
            assert structure_results["thread_id"] == thread_id
            assert "tables_exist" in structure_results
            assert "row_counts" in structure_results
            assert "data_integrity" in structure_results
            assert "validation_status" in structure_results

            # 检查表是否存在
            for table in ["checkpoints", "checkpoint_blobs", "checkpoint_writes"]:
                assert table in structure_results["tables_exist"]
                assert isinstance(structure_results["tables_exist"][table], bool)

            logger.info("checkpoint_structure_validation_test_passed", thread_id=thread_id)

        except Exception as e:
            logger.error("checkpoint_structure_validation_test_failed", thread_id=thread_id, error=str(e))
            pytest.fail(f"Checkpoint structure validation test failed: {str(e)}")

    @pytest.mark.asyncio
    async def test_checkpoint_data_consistency_validation(self):
        """Test checkpoint data consistency validation."""
        thread_id = str(uuid4())

        try:
            # 创建工作流并执行
            app = await create_bmad_workflow()

            initial_state = create_initial_state(
                problem_description="Test data consistency validation",
                domain="testing",
                constraints=["test constraint"],
                thread_id=thread_id
            )

            config = {"configurable": {"thread_id": thread_id}}

            # 执行几步
            event_count = 0
            async for event in app.astream(initial_state, config):
                event_count += 1
                if event_count >= 3:
                    break

            # 验证数据一致性
            checkpointer = await create_checkpointer()
            validator = CheckpointIntegrityValidator(checkpointer)

            consistency_results = await validator.validate_checkpoint_data_consistency(thread_id)

            # 验证结果
            assert consistency_results["thread_id"] == thread_id
            assert "consistency_checks" in consistency_results
            assert "validation_status" in consistency_results

            # 检查checkpoint数据结构验证
            assert "checkpoint_data_structure" in consistency_results["consistency_checks"]

            logger.info("checkpoint_data_consistency_validation_test_passed", thread_id=thread_id)

        except Exception as e:
            logger.error("checkpoint_data_consistency_validation_test_failed", thread_id=thread_id, error=str(e))
            pytest.fail(f"Checkpoint data consistency validation test failed: {str(e)}")

    @pytest.mark.asyncio
    async def test_workflow_state_recovery_validation(self):
        """Test workflow state recovery validation."""
        thread_id = str(uuid4())

        try:
            # 创建工作流并执行
            app = await create_bmad_workflow()

            initial_state = create_initial_state(
                problem_description="Test state recovery validation",
                domain="testing",
                constraints=["test constraint"],
                thread_id=thread_id
            )

            config = {"configurable": {"thread_id": thread_id}}

            # 执行几步
            event_count = 0
            async for event in app.astream(initial_state, config):
                event_count += 1
                if event_count >= 2:
                    break

            # 验证状态恢复
            checkpointer = await create_checkpointer()
            validator = CheckpointIntegrityValidator(checkpointer)

            recovery_results = await validator.validate_workflow_state_recovery(thread_id)

            # 验证结果
            assert recovery_results["thread_id"] == thread_id
            assert "recovery_tests" in recovery_results
            assert "validation_status" in recovery_results

            # 检查恢复测试结果
            recovery_tests = recovery_results["recovery_tests"]
            assert "state_recovered" in recovery_tests
            assert isinstance(recovery_tests["state_recovered"], bool)

            logger.info("workflow_state_recovery_validation_test_passed", thread_id=thread_id)

        except Exception as e:
            logger.error("workflow_state_recovery_validation_test_failed", thread_id=thread_id, error=str(e))
            pytest.fail(f"Workflow state recovery validation test failed: {str(e)}")

    @pytest.mark.asyncio
    async def test_full_integrity_validation(self):
        """Test complete checkpoint integrity validation."""
        thread_id = str(uuid4())

        try:
            # 创建工作流并执行几步
            app = await create_bmad_workflow()

            initial_state = create_initial_state(
                problem_description="Test full integrity validation",
                domain="testing",
                constraints=["test constraint"],
                thread_id=thread_id
            )

            config = {"configurable": {"thread_id": thread_id}}

            # 执行几步
            event_count = 0
            async for event in app.astream(initial_state, config):
                event_count += 1
                if event_count >= 2:
                    break

            # 运行完整验证
            integrity_results = await validate_checkpoint_integrity(thread_id)

            # 验证结果结构
            assert integrity_results["thread_id"] == thread_id
            assert "validation_timestamp" in integrity_results
            assert "structure_validation" in integrity_results
            assert "consistency_validation" in integrity_results
            assert "recovery_validation" in integrity_results
            assert "overall_status" in integrity_results
            assert "summary" in integrity_results

            # 验证摘要
            summary = integrity_results["summary"]
            assert "total_tests" in summary
            assert "passed_tests" in summary
            assert "failed_tests" in summary
            assert "error_tests" in summary

            assert summary["total_tests"] == 3
            assert summary["passed_tests"] + summary["failed_tests"] + summary["error_tests"] == 3

            # 验证总体状态
            assert integrity_results["overall_status"] in ["passed", "failed", "error"]

            logger.info(
                "full_integrity_validation_test_passed",
                thread_id=thread_id,
                overall_status=integrity_results["overall_status"]
            )

        except Exception as e:
            logger.error("full_integrity_validation_test_failed", thread_id=thread_id, error=str(e))
            pytest.fail(f"Full integrity validation test failed: {str(e)}")

    @pytest.mark.asyncio
    async def test_integrity_validation_with_no_data(self):
        """Test integrity validation with thread_id that has no checkpoint data."""
        thread_id = str(uuid4())

        try:
            # 直接运行验证（没有执行工作流）
            integrity_results = await validate_checkpoint_integrity(thread_id)

            # 应该能正常运行，但可能显示失败（因为没有数据）
            assert integrity_results["thread_id"] == thread_id
            assert integrity_results["overall_status"] in ["passed", "failed", "error"]

            logger.info(
                "integrity_validation_no_data_test_passed",
                thread_id=thread_id,
                status=integrity_results["overall_status"]
            )

        except Exception as e:
            logger.error("integrity_validation_no_data_test_failed", thread_id=thread_id, error=str(e))
            pytest.fail(f"Integrity validation with no data test failed: {str(e)}")


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])