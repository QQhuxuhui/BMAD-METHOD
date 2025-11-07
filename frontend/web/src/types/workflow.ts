// SSE事件类型
export type WorkflowEventType =
  | 'workflow_started'
  | 'phase_changed'
  | 'agent_started'
  | 'agent_output'
  | 'agent_completed'
  | 'approval_required'
  | 'workflow_completed'
  | 'workflow_failed'

// SSE事件数据结构
export interface WorkflowEvent {
  event: WorkflowEventType
  data: {
    timestamp: string
    workflow_id: string
    phase?: string
    agent_name?: string
    agent_output?: any
    approval_point?: 'P1' | 'P2' | 'P2.5'
    approval_context?: any
    error_message?: string
  }
}

// 审批决策
export interface ApprovalDecision {
  decision: 'approved' | 'rejected' | 'modified'
  feedback?: string
  modified_data?: Record<string, any>
}

// 审批点类型
export type ApprovalPoint = 'P1' | 'P2' | 'P2.5'

// 智能体状态
export type AgentStatus = 'pending' | 'running' | 'completed' | 'failed'

// 智能体执行信息
export interface AgentExecution {
  name: string
  status: AgentStatus
  startTime?: string
  endTime?: string
  output?: any
  error?: string
}

// 工作流阶段
export type WorkflowPhase = 'P0' | 'P1' | 'P2' | 'P2.5' | 'P3' | 'P4'

// useWorkflowStream配置选项
export interface UseWorkflowStreamOptions {
  workflowId: string
  autoConnect?: boolean
  onApprovalRequired?: (context: any) => void
  onError?: (error: Error) => void
  onComplete?: () => void
}
