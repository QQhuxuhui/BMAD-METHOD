"""BMAD Eight-Agent System - Checkpoint Integrity Validation.

This module provides functions to validate checkpoint data integrity,
ensuring that workflow state is properly persisted and can be recovered.
"""

import asyncio
from typing import Dict, Any, List, Optional
from uuid import uuid4
import json

from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.core.langgraph.state import WorkflowState, create_initial_state
from app.core.langgraph.workflow import create_bmad_workflow
from app.core.logging import logger


class CheckpointIntegrityValidator:
    """Validates checkpoint data integrity for BMAD workflows."""

    def __init__(self, checkpointer: AsyncPostgresSaver):
        """Initialize validator with checkpointer instance.

        Args:
            checkpointer: PostgreSQL checkpointer instance
        """
        self.checkpointer = checkpointer

    async def validate_checkpoint_structure(
        self, thread_id: str
    ) -> Dict[str, Any]:
        """验证checkpoint功能的基本结构.

        通过检查checkpoint保存和恢复来验证基本功能。

        Args:
            thread_id: Thread identifier for the workflow

        Returns:
            Dict[str, Any]: Validation results with structure integrity info
        """
        try:
            logger.info("checkpoint_structure_validation_started", thread_id=thread_id)

            results = {
                "thread_id": thread_id,
                "checkpointer_status": "unknown",
                "data_integrity": {},
                "validation_status": "unknown"
            }

            # 检查checkpointer是否正常工作
            try:
                # 尝试获取状态（即使不存在也应该正常返回）
                config = {"configurable": {"thread_id": thread_id}}

                # 创建一个临时的工作流来测试checkpointer
                app = await create_bmad_workflow()
                state_snapshot = await app.aget_state(config)

                results["checkpointer_status"] = "functional"
                results["has_data"] = state_snapshot and state_snapshot.values is not None

            except Exception as e:
                logger.error("checkpointer_functionality_test_failed", error=str(e))
                results["checkpointer_status"] = "error"
                results["error"] = str(e)

            # 验证数据完整性
            integrity_issues = []

            if results["checkpointer_status"] != "functional":
                integrity_issues.append("Checkpointer is not functional")

            if not results.get("has_data", False):
                integrity_issues.append("No checkpoint data found (workflow may not have executed)")

            results["data_integrity"]["issues"] = integrity_issues
            results["data_integrity"]["is_valid"] = len(integrity_issues) == 0
            results["validation_status"] = "passed" if len(integrity_issues) == 0 else "failed"

            logger.info(
                "checkpoint_structure_validation_completed",
                thread_id=thread_id,
                status=results["validation_status"],
                issues_count=len(integrity_issues)
            )

            return results

        except Exception as e:
            logger.error("checkpoint_structure_validation_failed", thread_id=thread_id, error=str(e))
            return {
                "thread_id": thread_id,
                "validation_status": "error",
                "error": str(e)
            }

    async def validate_checkpoint_data_consistency(
        self, thread_id: str
    ) -> Dict[str, Any]:
        """验证checkpoint数据一致性.

        通过验证工作流状态的保存和恢复来测试数据一致性。

        Args:
            thread_id: Thread identifier for the workflow

        Returns:
            Dict[str, Any]: Data consistency validation results
        """
        try:
            logger.info("checkpoint_data_consistency_validation_started", thread_id=thread_id)

            results = {
                "thread_id": thread_id,
                "consistency_checks": {},
                "validation_status": "unknown"
            }

            # 测试数据一致性
            try:
                # 创建工作流实例
                app = await create_bmad_workflow()
                config = {"configurable": {"thread_id": thread_id}}

                # 获取当前状态
                state_snapshot = await app.aget_state(config)

                if state_snapshot and state_snapshot.values:
                    state_data = state_snapshot.values

                    # 验证必要字段
                    required_fields = ["thread_id"]
                    missing_fields = [field for field in required_fields if field not in state_data]

                    # 验证数据类型
                    thread_id_match = state_data.get("thread_id") == thread_id
                    state_is_dict = isinstance(state_data, dict)

                    results["consistency_checks"]["state_recovered"] = True
                    results["consistency_checks"]["missing_fields"] = missing_fields
                    results["consistency_checks"]["thread_id_match"] = thread_id_match
                    results["consistency_checks"]["state_is_dict"] = state_is_dict
                    results["consistency_checks"]["state_keys"] = list(state_data.keys())
                else:
                    results["consistency_checks"]["state_recovered"] = False
                    results["consistency_checks"]["reason"] = "No state snapshot found"

            except Exception as e:
                results["consistency_checks"]["state_recovered"] = False
                results["consistency_checks"]["error"] = str(e)

            # 确定验证状态
            state_recovered = results["consistency_checks"].get("state_recovered", False)
            thread_id_match = results["consistency_checks"].get("thread_id_match", False)

            results["validation_status"] = "passed" if state_recovered and thread_id_match else "failed"

            logger.info(
                "checkpoint_data_consistency_validation_completed",
                thread_id=thread_id,
                status=results["validation_status"]
            )

            return results

        except Exception as e:
            logger.error("checkpoint_data_consistency_validation_failed", thread_id=thread_id, error=str(e))
            return {
                "thread_id": thread_id,
                "validation_status": "error",
                "error": str(e)
            }

    async def validate_workflow_state_recovery(
        self, thread_id: str
    ) -> Dict[str, Any]:
        """验证工作流状态恢复功能.

        Args:
            thread_id: Thread identifier for the workflow

        Returns:
            Dict[str, Any]: State recovery validation results
        """
        try:
            logger.info("workflow_state_recovery_validation_started", thread_id=thread_id)

            results = {
                "thread_id": thread_id,
                "recovery_tests": {},
                "validation_status": "unknown"
            }

            # 创建工作流实例
            app = await create_bmad_workflow()
            config = {"configurable": {"thread_id": thread_id}}

            # 测试状态恢复
            try:
                state_snapshot = await app.aget_state(config)

                if state_snapshot and state_snapshot.values:
                    recovered_state = state_snapshot.values

                    # 验证必要字段
                    required_fields = ["thread_id", "problem_description", "current_phase"]
                    missing_fields = [field for field in required_fields if field not in recovered_state]

                    results["recovery_tests"]["state_recovered"] = True
                    results["recovery_tests"]["missing_fields"] = missing_fields
                    results["recovery_tests"]["recovered_fields"] = list(recovered_state.keys())
                    results["recovery_tests"]["thread_id_match"] = recovered_state.get("thread_id") == thread_id
                else:
                    results["recovery_tests"]["state_recovered"] = False
                    results["recovery_tests"]["error"] = "No state snapshot found"

            except Exception as e:
                results["recovery_tests"]["state_recovered"] = False
                results["recovery_tests"]["error"] = str(e)

            # 测试工作流继续执行
            if results["recovery_tests"].get("state_recovered", False):
                try:
                    # 尝试继续执行（但不实际运行，只检查是否能获取下一个节点）
                    next_node = state_snapshot.next if state_snapshot else None
                    results["recovery_tests"]["can_continue"] = next_node is not None
                    results["recovery_tests"]["next_node"] = next_node
                except Exception as e:
                    results["recovery_tests"]["can_continue"] = False
                    results["recovery_tests"]["continue_error"] = str(e)

            results["validation_status"] = "passed" if results["recovery_tests"].get("state_recovered", False) else "failed"

            logger.info(
                "workflow_state_recovery_validation_completed",
                thread_id=thread_id,
                status=results["validation_status"]
            )

            return results

        except Exception as e:
            logger.error("workflow_state_recovery_validation_failed", thread_id=thread_id, error=str(e))
            return {
                "thread_id": thread_id,
                "validation_status": "error",
                "error": str(e)
            }

    async def run_full_integrity_validation(
        self, thread_id: str
    ) -> Dict[str, Any]:
        """运行完整的checkpoint完整性验证.

        Args:
            thread_id: Thread identifier for the workflow

        Returns:
            Dict[str, Any]: Complete validation results
        """
        logger.info("full_checkpoint_integrity_validation_started", thread_id=thread_id)

        # 运行所有验证测试
        structure_validation = await self.validate_checkpoint_structure(thread_id)
        consistency_validation = await self.validate_checkpoint_data_consistency(thread_id)
        recovery_validation = await self.validate_workflow_state_recovery(thread_id)

        # 汇总结果
        all_results = {
            "thread_id": thread_id,
            "validation_timestamp": asyncio.get_event_loop().time(),
            "structure_validation": structure_validation,
            "consistency_validation": consistency_validation,
            "recovery_validation": recovery_validation,
            "overall_status": "unknown",
            "summary": {
                "total_tests": 3,
                "passed_tests": 0,
                "failed_tests": 0,
                "error_tests": 0
            }
        }

        # 计算总体状态
        tests = [
            structure_validation.get("validation_status", "error"),
            consistency_validation.get("validation_status", "error"),
            recovery_validation.get("validation_status", "error")
        ]

        for test_status in tests:
            if test_status == "passed":
                all_results["summary"]["passed_tests"] += 1
            elif test_status == "failed":
                all_results["summary"]["failed_tests"] += 1
            else:
                all_results["summary"]["error_tests"] += 1

        # 确定总体状态
        if all_results["summary"]["failed_tests"] == 0 and all_results["summary"]["error_tests"] == 0:
            all_results["overall_status"] = "passed"
        elif all_results["summary"]["error_tests"] > 0:
            all_results["overall_status"] = "error"
        else:
            all_results["overall_status"] = "failed"

        logger.info(
            "full_checkpoint_integrity_validation_completed",
            thread_id=thread_id,
            overall_status=all_results["overall_status"],
            passed=all_results["summary"]["passed_tests"],
            failed=all_results["summary"]["failed_tests"],
            errors=all_results["summary"]["error_tests"]
        )

        return all_results


async def validate_checkpoint_integrity(thread_id: str) -> Dict[str, Any]:
    """便捷函数：验证checkpoint完整性.

    Args:
        thread_id: Thread identifier for the workflow

    Returns:
        Dict[str, Any]: Complete validation results
    """
    try:
        from app.core.langgraph.workflow import create_checkpointer

        # 创建checkpointer
        checkpointer = await create_checkpointer()

        # 创建验证器并运行验证
        validator = CheckpointIntegrityValidator(checkpointer)
        results = await validator.run_full_integrity_validation(thread_id)

        return results

    except Exception as e:
        logger.error("checkpoint_integrity_validation_failed", thread_id=thread_id, error=str(e))
        return {
            "thread_id": thread_id,
            "overall_status": "error",
            "error": str(e)
        }


# Export functions
__all__ = [
    'CheckpointIntegrityValidator',
    'validate_checkpoint_integrity'
]