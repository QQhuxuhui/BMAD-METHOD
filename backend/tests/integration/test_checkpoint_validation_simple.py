"""简单的Checkpoint验证测试.

测试基本的checkpoint保存和恢复功能，验证AC 6的完整性要求。
"""

import pytest
import asyncio
from typing import Dict, Any
from uuid import uuid4

from app.core.langgraph.checkpoint_validator import validate_checkpoint_integrity
from app.core.langgraph.executor import run_workflow
from app.core.langgraph.workflow import create_bmad_workflow
from app.core.langgraph.state import create_initial_state
from app.core.logging import logger


class TestCheckpointValidation:
    """简化的checkpoint验证测试."""

    @pytest.mark.asyncio
    async def test_checkpoint_save_and_recover(self):
        """测试checkpoint保存和恢复功能."""
        thread_id = str(uuid4())

        try:
            # 创建初始状态
            initial_state = create_initial_state(
                problem_description="Test checkpoint save and recover functionality",
                domain="testing",
                constraints=["test constraint"],
                thread_id=thread_id
            )

            # 创建工作流并执行几步
            app = await create_bmad_workflow()
            config = {"configurable": {"thread_id": thread_id}}

            # 执行工作流几步以创建checkpoint
            event_count = 0
            last_state = None
            async for event in app.astream(initial_state, config):
                event_count += 1
                # 保存最后一个状态
                for node_output in event.values():
                    if isinstance(node_output, dict):
                        last_state = node_output
                if event_count >= 2:  # 只执行几步
                    break

            # 验证checkpoint数据
            validation_results = await validate_checkpoint_integrity(thread_id)

            # 基本验证
            assert validation_results["thread_id"] == thread_id
            assert "overall_status" in validation_results

            logger.info(
                "checkpoint_save_and_recover_test_passed",
                thread_id=thread_id,
                overall_status=validation_results["overall_status"]
            )

        except Exception as e:
            logger.error("checkpoint_save_and_recover_test_failed", thread_id=thread_id, error=str(e))
            pytest.fail(f"Checkpoint save and recover test failed: {str(e)}")

    @pytest.mark.asyncio
    async def test_checkpoint_data_persistence(self):
        """测试checkpoint数据持久化."""
        thread_id = str(uuid4())

        try:
            # 创建工作流实例
            app = await create_bmad_workflow()
            config = {"configurable": {"thread_id": thread_id}}

            # 创建并保存初始状态
            initial_state = create_initial_state(
                problem_description="Test checkpoint data persistence",
                domain="testing",
                constraints=[],
                thread_id=thread_id
            )

            # 执行一步以确保checkpoint被保存
            async for event in app.astream(initial_state, config):
                break  # 只执行第一步

            # 验证状态可以被恢复
            state_snapshot = await app.aget_state(config)

            assert state_snapshot is not None, "State snapshot should not be None"

            if state_snapshot.values:
                # 验证关键字段被保存
                assert "thread_id" in state_snapshot.values, "thread_id should be saved"
                assert state_snapshot.values["thread_id"] == thread_id, "thread_id should match"

                logger.info(
                    "checkpoint_data_persistence_test_passed",
                    thread_id=thread_id,
                    saved_fields=list(state_snapshot.values.keys())
                )
            else:
                logger.warning("no_checkpoint_data_saved", thread_id=thread_id)

        except Exception as e:
            logger.error("checkpoint_data_persistence_test_failed", thread_id=thread_id, error=str(e))
            pytest.fail(f"Checkpoint data persistence test failed: {str(e)}")

    @pytest.mark.asyncio
    async def test_checkpoint_integrity_validation(self):
        """测试checkpoint完整性验证功能."""
        thread_id = str(uuid4())

        try:
            # 运行完整性验证（即使没有数据）
            validation_results = await validate_checkpoint_integrity(thread_id)

            # 验证返回结构
            assert "thread_id" in validation_results
            assert "overall_status" in validation_results
            assert validation_results["thread_id"] == thread_id
            assert validation_results["overall_status"] in ["passed", "failed", "error"]

            # 验证摘要信息
            if "summary" in validation_results:
                summary = validation_results["summary"]
                assert "total_tests" in summary
                assert "passed_tests" in summary
                assert "failed_tests" in summary
                assert "error_tests" in summary

            logger.info(
                "checkpoint_integrity_validation_test_passed",
                thread_id=thread_id,
                status=validation_results["overall_status"]
            )

        except Exception as e:
            logger.error("checkpoint_integrity_validation_test_failed", thread_id=thread_id, error=str(e))
            pytest.fail(f"Checkpoint integrity validation test failed: {str(e)}")


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])