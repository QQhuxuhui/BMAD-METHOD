"""工作流中断处理和状态管理器

Story 1.5.4 实现：处理 LangGraph 工作流中断和恢复机制

主要功能：
- 管理工作流中断点状态
- 处理 P1 和 P2.5 审批点中断
- 支持从 checkpoint 加载和保存状态
- 协调 HumanApproval 记录和工作流状态
"""

import uuid
from datetime import datetime, UTC
from typing import Optional, Dict, Any, Tuple

from app.core.logging import logger
from app.models.workflow_execution import WorkflowExecution
from app.models.human_approval import HumanApproval, HumanApprovalCreate, HumanApprovalUpdate
from app.core.langgraph.state import WorkflowState


class WorkflowInterruptionManager:
    """工作流中断管理器

    负责处理工作流中断逻辑，包括：
    - 中断点检测和状态保存
    - HumanApproval 记录管理
    - 工作流恢复时的状态应用
    """

    def __init__(self):
        self.logger = logger

    async def prepare_interruption_state(
        self,
        state: WorkflowState,
        approval_point: str,
        context_data: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """准备工作流中断状态

        为指定的审批点准备中断所需的状态数据

        Args:
            state: 当前工作流状态
            approval_point: 审批点标识 ('P1', 'P2.5')
            context_data: 审批上下文数据

        Returns:
            Tuple[str, Dict[str, Any]]: (approval_id, updated_state)
        """
        try:
            # 生成唯一的审批 ID
            approval_id = str(uuid.uuid4())

            # 准备中断状态数据
            if context_data is None:
                context_data = self._extract_context_data(state, approval_point)

            updated_state = {
                'pending_approval': True,
                'approval_point': approval_point,
                'approval_checkpoint_id': approval_id,
                'approval_id': approval_id,  # for compatibility
                'context_data': context_data,
                'workflow_id': state.get('workflow_id'),
                'user_id': state.get('user_id'),
                'thread_id': state.get('thread_id'),
                'timestamp': datetime.now(UTC).isoformat(),
                'current_phase': f'{approval_point}_Approval_Pending'
            }

            self.logger.info(
                "workflow_interruption_prepared",
                approval_point=approval_point,
                approval_id=approval_id,
                thread_id=state.get('thread_id')
            )

            return approval_id, updated_state

        except Exception as e:
            self.logger.error(
                "interruption_preparation_failed",
                approval_point=approval_point,
                error=str(e)
            )
            raise

    def _extract_context_data(self, state: WorkflowState, approval_point: str) -> Dict[str, Any]:
        """从工作流状态中提取审批上下文数据

        Args:
            state: 工作流状态
            approval_point: 审批点

        Returns:
            Dict[str, Any]: 审批上下文数据
        """
        if approval_point == 'P1':
            return {
                'algorithm_output': state.get('algorithm_output'),
                'constraint_output': state.get('constraint_output'),
                'objective_output': state.get('objective_output'),
                'orchestrator_output': state.get('orchestrator_output'),
            }
        elif approval_point == 'P2.5':
            return {
                'code_impl_output': state.get('code_impl_output'),
                'extension_output': state.get('extension_output'),
                'domain_output': state.get('domain_output'),
            }
        else:
            return {}

    async def apply_user_decision_to_state(
        self,
        state: WorkflowState,
        user_decision: str,
        feedback: str,
        modified_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """将用户决策应用到工作流状态

        Args:
            state: 当前工作流状态
            user_decision: 用户决策 ('approved', 'rejected', 'modified')
            feedback: 用户反馈
            modified_data: 修改后的数据

        Returns:
            Dict[str, Any]: 更新后的状态
        """
        try:
            updated_state = {
                'pending_approval': False,
                'approval_decision': user_decision,
                'approval_feedback': feedback,
                'approval_resumed_at': datetime.now(UTC).isoformat()
            }

            # 如果用户修改了数据，应用到状态中
            if modified_data and user_decision == 'modified':
                updated_state['modified_data'] = modified_data

                # 应用特定字段的修改
                if 'algorithm' in modified_data:
                    updated_state['selected_algorithm'] = modified_data['algorithm']
                if 'constraints' in modified_data:
                    updated_state['user_constraints'] = modified_data['constraints']
                if 'objectives' in modified_data:
                    updated_state['optimization_objectives'] = modified_data['objectives']

            self.logger.info(
                "user_decision_applied",
                decision=user_decision,
                has_modifications=bool(modified_data),
                thread_id=state.get('thread_id')
            )

            return updated_state

        except Exception as e:
            self.logger.error(
                "decision_application_failed",
                decision=user_decision,
                error=str(e)
            )
            raise

    async def validate_interruption(
        self,
        workflow: WorkflowExecution,
        approval: HumanApproval
    ) -> bool:
        """验证中断的有效性

        Args:
            workflow: 工作流执行记录
            approval: 审批记录

        Returns:
            bool: 中断是否有效
        """
        try:
            # 检查工作流是否处于暂停状态
            if workflow.status != 'paused':
                self.logger.warning(
                    "workflow_not_paused_for_interruption",
                    workflow_id=str(workflow.id),
                    current_status=workflow.status
                )
                return False

            # 检查审批是否属于该工作流
            if approval.workflow_id != workflow.id:
                self.logger.warning(
                    "approval_workflow_mismatch",
                    approval_id=str(approval.id),
                    approval_workflow_id=str(approval.workflow_id),
                    expected_workflow_id=str(workflow.id)
                )
                return False

            # 检查审批是否处于待处理状态
            if approval.decision is not None:
                self.logger.warning(
                    "approval_already_decided",
                    approval_id=str(approval.id),
                    decision=approval.decision
                )
                return False

            return True

        except Exception as e:
            self.logger.error(
                "interruption_validation_failed",
                workflow_id=str(workflow.id),
                approval_id=str(approval.id),
                error=str(e)
            )
            return False

    def create_interruption_error_state(
        self,
        approval_point: str,
        error_message: str,
        thread_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """创建中断错误状态

        Args:
            approval_point: 审批点
            error_message: 错误信息
            thread_id: 线程ID

        Returns:
            Dict[str, Any]: 错误状态
        """
        return {
            'pending_approval': False,
            'approval_point': approval_point,
            'approval_decision': 'error',
            'approval_feedback': f'Error during {approval_point} approval: {error_message}',
            'approval_error': True,
            'thread_id': thread_id,
            'timestamp': datetime.now(UTC).isoformat()
        }


# 全局中断管理器实例
interruption_manager = WorkflowInterruptionManager()