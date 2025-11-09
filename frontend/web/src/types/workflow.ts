/**
 * 工作流监控相关的TypeScript类型定义
 * Story 1.9: 实时工作流监控面板MVP
 */

// SSE事件类型
export type WorkflowEventType =
  | 'workflow_started'
  | 'phase_changed'
  | 'agent_started'
  | 'agent_output'
  | 'agent_completed'
  | 'agent_failed'
  | 'approval_required'
  | 'workflow_paused'
  | 'workflow_resumed'
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
    /** 额外元数据 */
    metadata?: Record<string, any>
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

// ============================================
// Story 1.9 新增类型定义
// ============================================

/**
 * Phase信息
 */
export interface PhaseInfo {
  /** Phase编号 (0-4) */
  id: number
  /** Phase名称 */
  name: string
  /** Phase描述 */
  description: string
  /** Phase状态 */
  status: 'pending' | 'running' | 'completed' | 'failed'
  /** Phase包含的智能体列表 */
  agents: string[]
}

/**
 * 工作流整体状态
 */
export type WorkflowStatus = 'idle' | 'running' | 'paused' | 'completed' | 'failed'

/**
 * 工作流状态数据（用于Pinia Store）
 */
export interface WorkflowStateData {
  /** 工作流ID */
  workflowId: string
  /** 工作流名称 */
  workflowName?: string
  /** 整体状态 */
  status: WorkflowStatus
  /** 当前Phase (0-4) */
  currentPhase: number
  /** 整体进度 (0-100) */
  progress: number
  /** 开始时间 */
  startTime: number
  /** 结束时间 */
  endTime: number
  /** 智能体执行列表 */
  agents: AgentExecution[]
  /** Phase列表 */
  phases: PhaseInfo[]
  /** 所有事件记录 */
  events: WorkflowEvent[]
  /** 错误信息 */
  error?: {
    message: string
    timestamp: number
  }
}

/**
 * Mock SSE服务器配置
 */
export interface MockSSEConfig {
  /** 事件发送间隔（毫秒） */
  intervalMs?: number
  /** 是否自动开始 */
  autoStart?: boolean
  /** 模拟场景 */
  scenario?: 'success' | 'failure' | 'pause' | 'long-running'
}

/**
 * 工作流启动请求参数
 */
export interface WorkflowStartRequest {
  /** 用户输入/问题描述 */
  userInput: string
  /** 工作流配置 */
  config?: {
    /** 是否启用Human-in-Loop */
    enableHumanInLoop?: boolean
    /** 超时时间（秒） */
    timeout?: number
    /** 其他配置 */
    [key: string]: any
  }
}

/**
 * 工作流启动响应
 */
export interface WorkflowStartResponse {
  /** 工作流ID */
  workflowId: string
  /** SSE流URL */
  streamUrl: string
  /** 创建时间 */
  createdAt: number
}
