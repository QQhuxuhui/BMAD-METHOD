/**
 * Workflow State Management
 * Story 1.9: 实时工作流监控面板MVP
 */

import { defineStore } from 'pinia'
import type {
  WorkflowEvent,
  WorkflowStatus,
  AgentExecution,
  PhaseInfo,
  WorkflowStateData
} from '@/types/workflow'

/**
 * 定义八大智能体
 */
const AGENTS: AgentExecution[] = [
  { name: 'Orchestrator', status: 'pending', order: 0 },
  { name: 'Algorithm Expert', status: 'pending', order: 1 },
  { name: 'Constraint Expert', status: 'pending', order: 2 },
  { name: 'Objective Expert', status: 'pending', order: 3 },
  { name: 'Domain Expert', status: 'pending', order: 4 },
  { name: 'Code Implementation Expert', status: 'pending', order: 5 },
  { name: 'Extension Expert', status: 'pending', order: 6 },
  { name: 'Quality Expert', status: 'pending', order: 7 }
]

/**
 * 定义五个Phase
 */
const PHASES: PhaseInfo[] = [
  {
    id: 0,
    name: 'Phase 0: 问题理解',
    description: 'Orchestrator分析问题并推荐算法',
    status: 'pending',
    agents: ['Orchestrator']
  },
  {
    id: 1,
    name: 'Phase 1: 算法选择',
    description: 'Algorithm Expert提供详细算法设计',
    status: 'pending',
    agents: ['Algorithm Expert']
  },
  {
    id: 2,
    name: 'Phase 2: 多维度分析',
    description: 'Constraint, Objective, Domain Experts并行分析',
    status: 'pending',
    agents: ['Constraint Expert', 'Objective Expert', 'Domain Expert']
  },
  {
    id: 3,
    name: 'Phase 3: 代码实现',
    description: 'Code Implementation Expert生成代码',
    status: 'pending',
    agents: ['Code Implementation Expert']
  },
  {
    id: 4,
    name: 'Phase 4: 扩展和质量',
    description: 'Extension和Quality Experts优化方案',
    status: 'pending',
    agents: ['Extension Expert', 'Quality Expert']
  }
]

export const useWorkflowStore = defineStore('workflow', {
  state: (): WorkflowStateData => ({
    workflowId: '',
    workflowName: '',
    status: 'idle',
    currentPhase: -1,
    progress: 0,
    startTime: 0,
    endTime: 0,
    agents: [...AGENTS],
    phases: [...PHASES],
    events: [],
    error: undefined
  }),

  getters: {
    /**
     * 工作流运行时长（秒）
     */
    duration: (state): number => {
      if (!state.startTime) return 0
      const end = state.endTime || Date.now()
      return Math.floor((end - state.startTime) / 1000)
    },

    /**
     * 当前活跃的智能体
     */
    activeAgent: (state): AgentExecution | undefined => {
      return state.agents.find(a => a.status === 'running')
    },

    /**
     * 已完成的智能体列表
     */
    completedAgents: (state): AgentExecution[] => {
      return state.agents.filter(a => a.status === 'completed')
    },

    /**
     * 失败的智能体列表
     */
    failedAgents: (state): AgentExecution[] => {
      return state.agents.filter(a => a.status === 'failed')
    },

    /**
     * 当前Phase信息
     */
    currentPhaseInfo: (state): PhaseInfo | undefined => {
      return state.phases.find(p => p.id === state.currentPhase)
    },

    /**
     * 是否正在运行
     */
    isRunning: (state): boolean => {
      return state.status === 'running'
    },

    /**
     * 是否已完成
     */
    isCompleted: (state): boolean => {
      return state.status === 'completed' || state.status === 'failed'
    },

    /**
     * 最新的输出事件
     */
    latestOutput: (state): WorkflowEvent | undefined => {
      return [...state.events]
        .reverse()
        .find(e => e.event === 'agent_output')
    }
  },

  actions: {
    /**
     * 处理接收到的事件
     */
    processEvent(event: WorkflowEvent) {
      console.log('[WorkflowStore] Processing event:', event.event, event.data)

      // 添加到事件历史
      this.events.push(event)

      // 根据事件类型更新状态
      switch (event.event) {
        case 'workflow_started':
          this.handleWorkflowStarted(event)
          break
        case 'phase_changed':
          this.handlePhaseChanged(event)
          break
        case 'agent_started':
          this.handleAgentStarted(event)
          break
        case 'agent_output':
          this.handleAgentOutput(event)
          break
        case 'agent_completed':
          this.handleAgentCompleted(event)
          break
        case 'agent_failed':
          this.handleAgentFailed(event)
          break
        case 'approval_required':
          this.handleApprovalRequired(event)
          break
        case 'workflow_paused':
          this.handleWorkflowPaused(event)
          break
        case 'workflow_resumed':
          this.handleWorkflowResumed(event)
          break
        case 'workflow_completed':
          this.handleWorkflowCompleted(event)
          break
        case 'workflow_failed':
          this.handleWorkflowFailed(event)
          break
      }

      // 更新进度
      this.updateProgress()
    },

    /**
     * 工作流开始
     */
    handleWorkflowStarted(event: WorkflowEvent) {
      this.workflowId = event.data.workflow_id
      this.status = 'running'
      this.startTime = new Date(event.data.timestamp).getTime()
      this.currentPhase = 0

      // 重置所有智能体和Phase状态
      this.agents = [...AGENTS]
      this.phases = [...PHASES]
      this.phases[0].status = 'running'

      console.log('[WorkflowStore] Workflow started:', this.workflowId)
    },

    /**
     * Phase变更
     */
    handlePhaseChanged(event: WorkflowEvent) {
      const phase = event.data.phase

      if (phase) {
        // 提取Phase编号 (P0 -> 0, P1 -> 1, etc.)
        const phaseNum = parseInt(phase.replace('P', ''))

        // 完成旧Phase
        if (this.currentPhase >= 0 && this.currentPhase < this.phases.length) {
          this.phases[this.currentPhase].status = 'completed'
        }

        // 进入新Phase
        this.currentPhase = phaseNum
        if (phaseNum >= 0 && phaseNum < this.phases.length) {
          this.phases[phaseNum].status = 'running'
        }

        console.log('[WorkflowStore] Phase changed to:', phase)
      }
    },

    /**
     * 智能体开始执行
     */
    handleAgentStarted(event: WorkflowEvent) {
      const agentName = event.data.agent_name

      if (agentName) {
        const agent = this.agents.find(a => a.name === agentName)
        if (agent) {
          agent.status = 'running'
          agent.startTime = event.data.timestamp
          console.log('[WorkflowStore] Agent started:', agentName)
        }
      }
    },

    /**
     * 智能体输出内容
     */
    handleAgentOutput(event: WorkflowEvent) {
      const agentName = event.data.agent_name

      if (agentName && event.data.agent_output) {
        const agent = this.agents.find(a => a.name === agentName)
        if (agent) {
          // 累积输出内容
          const newContent = event.data.agent_output.content || event.data.agent_output
          agent.output = (agent.output || '') + newContent
        }
      }
    },

    /**
     * 智能体完成执行
     */
    handleAgentCompleted(event: WorkflowEvent) {
      const agentName = event.data.agent_name

      if (agentName) {
        const agent = this.agents.find(a => a.name === agentName)
        if (agent) {
          agent.status = 'completed'
          agent.endTime = event.data.timestamp
          console.log('[WorkflowStore] Agent completed:', agentName)
        }
      }
    },

    /**
     * 智能体执行失败
     */
    handleAgentFailed(event: WorkflowEvent) {
      const agentName = event.data.agent_name

      if (agentName) {
        const agent = this.agents.find(a => a.name === agentName)
        if (agent) {
          agent.status = 'failed'
          agent.endTime = event.data.timestamp
          agent.error = event.data.error_message
          console.error('[WorkflowStore] Agent failed:', agentName, event.data.error_message)
        }
      }
    },

    /**
     * 需要审批
     */
    handleApprovalRequired(event: WorkflowEvent) {
      console.log('[WorkflowStore] Approval required at:', event.data.approval_point)
      // 这里可以添加审批相关的状态管理
    },

    /**
     * 工作流暂停
     */
    handleWorkflowPaused(event: WorkflowEvent) {
      this.status = 'paused'
      console.log('[WorkflowStore] Workflow paused')
    },

    /**
     * 工作流恢复
     */
    handleWorkflowResumed(event: WorkflowEvent) {
      this.status = 'running'
      console.log('[WorkflowStore] Workflow resumed')
    },

    /**
     * 工作流完成
     */
    handleWorkflowCompleted(event: WorkflowEvent) {
      this.status = 'completed'
      this.endTime = new Date(event.data.timestamp).getTime()
      this.progress = 100

      // 标记当前Phase为完成
      if (this.currentPhase >= 0 && this.currentPhase < this.phases.length) {
        this.phases[this.currentPhase].status = 'completed'
      }

      console.log('[WorkflowStore] Workflow completed')
    },

    /**
     * 工作流失败
     */
    handleWorkflowFailed(event: WorkflowEvent) {
      this.status = 'failed'
      this.endTime = new Date(event.data.timestamp).getTime()
      this.error = {
        message: event.data.error_message || '工作流执行失败',
        timestamp: this.endTime
      }

      // 标记当前Phase为失败
      if (this.currentPhase >= 0 && this.currentPhase < this.phases.length) {
        this.phases[this.currentPhase].status = 'failed'
      }

      console.error('[WorkflowStore] Workflow failed:', this.error.message)
    },

    /**
     * 更新整体进度
     */
    updateProgress() {
      const completed = this.completedAgents.length
      const total = this.agents.length

      if (total > 0) {
        this.progress = Math.floor((completed / total) * 100)
      }
    },

    /**
     * 重置状态
     */
    reset() {
      this.$reset()
      console.log('[WorkflowStore] State reset')
    }
  }
})
