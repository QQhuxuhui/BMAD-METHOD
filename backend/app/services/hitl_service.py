"""HITL (Human-in-the-Loop) 服务

Story 1.5.4 实现：提供高级 HITL 功能，协调中断管理、审批记录和工作流恢复

主要功能：
- 管理完整的 HITL 流程
- 协调中断管理器和 workflow_service
- 处理复杂的审批场景（修改、拒绝等）
- 提供 HITL 相关的业务逻辑
"""

import uuid
from datetime import datetime, UTC
from typing import Optional, Dict, Any, List, Tuple

from app.core.logging import logger
from app.core.workflow_interruption import interruption_manager
from app.models.workflow_execution import WorkflowExecution
from app.models.human_approval import HumanApproval, HumanApprovalCreate, HumanApprovalUpdate
from app.services.workflow_crud import human_approval_crud
from sqlalchemy.orm import Session


class HITLService:
    """HITL 服务类

    提供高级的 Human-in-the-Loop 功能，包括：
    - 审批点中断管理
    - 用户决策处理
    - 工作流状态协调
    - 复杂审批场景处理
    """

    def __init__(self):
        self.logger = logger
        self.interruption_manager = interruption_manager

    async def handle_interruption_start(
        self,
        session: Session,
        workflow: WorkflowExecution,
        approval_point: str,
        context_data: Optional[Dict[str, Any]] = None,
        workflow_state: Optional[Dict[str, Any]] = None
    ) -> HumanApproval:
        """处理审批中断开始

        创建 HumanApproval 记录并更新工作流状态

        Args:
            session: 数据库会话
            workflow: 工作流执行记录
            approval_point: 审批点标识
            context_data: 审批上下文数据
            workflow_state: 当前工作流状态

        Returns:
            HumanApproval: 创建的审批记录
        """
        try:
            # 准备中断状态
            if workflow_state:
                approval_id, interruption_state = await self.interruption_manager.prepare_interruption_state(
                    workflow_state, approval_point, context_data
                )
            else:
                approval_id = str(uuid.uuid4())

            # 创建 HumanApproval 记录
            approval_create = HumanApprovalCreate(
                workflow_id=workflow.id,
                user_id=workflow.user_id,
                approval_point=approval_point,
                context_data=context_data or {}
            )

            # 手动设置 approval_id（如果需要的话）
            approval = human_approval_crud.create(approval_create, session=session)

            self.logger.info(
                "hitl_interruption_created",
                approval_id=str(approval.id),
                approval_point=approval_point,
                workflow_id=str(workflow.id)
            )

            return approval

        except Exception as e:
            self.logger.error(
                "hitl_interruption_creation_failed",
                approval_point=approval_point,
                workflow_id=str(workflow.id),
                error=str(e)
            )
            raise

    async def handle_user_decision(
        self,
        session: Session,
        approval: HumanApproval,
        user_decision: str,
        feedback: str,
        modified_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """处理用户审批决策

        更新审批记录并准备恢复工作流的状态

        Args:
            session: 数据库会话
            approval: 审批记录
            user_decision: 用户决策 ('approved', 'rejected', 'modified')
            feedback: 用户反馈
            modified_data: 修改后的数据

        Returns:
            bool: 处理是否成功
        """
        try:
            # 更新审批记录
            approval_update = HumanApprovalUpdate(
                decision=user_decision,
                feedback=feedback,
                modified_data=modified_data,
                decided_at=datetime.now(UTC)
            )

            updated_approval = human_approval_crud.update(
                approval.id, approval_update, session=session
            )

            self.logger.info(
                "hitl_decision_processed",
                approval_id=str(approval.id),
                decision=user_decision,
                has_modifications=bool(modified_data)
            )

            return True

        except Exception as e:
            self.logger.error(
                "hitl_decision_processing_failed",
                approval_id=str(approval.id),
                decision=user_decision,
                error=str(e)
            )
            return False

    async def validate_resume_request(
        self,
        session: Session,
        workflow_id: uuid.UUID,
        user_id: int,
        approval_id: Optional[uuid.UUID] = None
    ) -> Tuple[bool, Optional[HumanApproval]]:
        """验证工作流恢复请求

        Args:
            session: 数据库会话
            workflow_id: 工作流ID
            user_id: 用户ID
            approval_id: 可选的审批ID

        Returns:
            Tuple[bool, Optional[HumanApproval]]: (是否有效, 审批记录)
        """
        try:
            # 查找待处理的审批记录
            if approval_id:
                approval = human_approval_crud.get(approval_id, session=session)
            else:
                approval = human_approval_crud.get_pending_approval(workflow_id, session=session)

            if not approval:
                self.logger.warning(
                    "hitl_no_pending_approval",
                    workflow_id=str(workflow_id)
                )
                return False, None

            # 验证审批记录属于指定用户的工作流
            if approval.workflow_id != workflow_id or approval.user_id != user_id:
                self.logger.warning(
                    "hitl_approval_permission_denied",
                    approval_id=str(approval.id),
                    requested_workflow_id=str(workflow_id),
                    requested_user_id=user_id
                )
                return False, None

            # 验证审批处于待处理状态
            if approval.decision is not None:
                self.logger.warning(
                    "hitl_approval_already_decided",
                    approval_id=str(approval.id),
                    decision=approval.decision
                )
                return False, None

            return True, approval

        except Exception as e:
            self.logger.error(
                "hitl_resume_validation_failed",
                workflow_id=str(workflow_id),
                error=str(e)
            )
            return False, None

    async def get_approval_history(
        self,
        session: Session,
        workflow_id: uuid.UUID,
        include_pending: bool = True
    ) -> List[HumanApproval]:
        """获取工作流的审批历史

        Args:
            session: 数据库会话
            workflow_id: 工作流ID
            include_pending: 是否包含待处理的审批

        Returns:
            List[HumanApproval]: 审批记录列表
        """
        try:
            approvals = human_approval_crud.get_by_workflow(
                workflow_id, session=session, include_pending=include_pending
            )

            self.logger.info(
                "hitl_approval_history_retrieved",
                workflow_id=str(workflow_id),
                count=len(approvals)
            )

            return approvals

        except Exception as e:
            self.logger.error(
                "hitl_approval_history_retrieval_failed",
                workflow_id=str(workflow_id),
                error=str(e)
            )
            return []

    async def check_for_expired_approvals(
        self,
        session: Session,
        timeout_hours: int = 24
    ) -> List[HumanApproval]:
        """检查过期的审批

        Args:
            session: 数据库会话
            timeout_hours: 超时时间（小时）

        Returns:
            List[HumanApproval]: 过期的审批列表
        """
        try:
            expired_approvals = human_approval_crud.get_expired_approvals(
                timeout_hours, session=session
            )

            if expired_approvals:
                self.logger.info(
                    "hitl_expired_approvals_found",
                    count=len(expired_approvals),
                    timeout_hours=timeout_hours
                )

            return expired_approvals

        except Exception as e:
            self.logger.error(
                "hitl_expired_approval_check_failed",
                error=str(e)
            )
            return []


# 全局 HITL 服务实例
hitl_service = HITLService()