import { ref, computed, watch, onUnmounted } from 'vue'
import { useEventSource } from '@vueuse/core'
import type {
  WorkflowEvent,
  UseWorkflowStreamOptions,
  WorkflowPhase,
  AgentExecution,
} from '@/types/workflow'

/**
 * SSE工作流实时监控Hook
 * 基于@vueuse/core的useEventSource封装业务逻辑
 */
export function useWorkflowStream(options: UseWorkflowStreamOptions) {
  const {
    workflowId,
    autoConnect = true,
    onApprovalRequired,
    onError,
    onComplete,
  } = options

  // State
  const events = ref<WorkflowEvent[]>([])
  const currentPhase = ref<WorkflowPhase>('P0')
  const currentAgent = ref<string | null>(null)
  const isApprovalRequired = ref(false)
  const approvalContext = ref<any>(null)
  const approvalPoint = ref<'P1' | 'P2' | 'P2.5' | null>(null)
  const agentExecutions = ref<Map<string, AgentExecution>>(new Map())

  // 构建SSE URL
  const token = localStorage.getItem('token')
  const baseURL = import.meta.env.VITE_API_BASE_URL || '/api'
  const url = computed(
    () => `${baseURL}/v1/workflows/${workflowId}/stream?token=${token || ''}`,
  )

  // 使用@vueuse的useEventSource
  const { data, status, error, close, open } = useEventSource(url, [], {
    immediate: autoConnect,
    withCredentials: true,
  })

  // 解析并处理SSE事件
  const parseEvent = (eventData: string) => {
    if (!eventData) return

    try {
      const event: WorkflowEvent = JSON.parse(eventData)
      events.value.push(event)

      // 根据event type更新状态
      switch (event.event) {
        case 'workflow_started':
          currentPhase.value = 'P0'
          agentExecutions.value.clear()
          break

        case 'phase_changed':
          if (event.data.phase) {
            currentPhase.value = event.data.phase as WorkflowPhase
          }
          break

        case 'agent_started':
          if (event.data.agent_name) {
            currentAgent.value = event.data.agent_name
            agentExecutions.value.set(event.data.agent_name, {
              name: event.data.agent_name,
              status: 'running',
              startTime: event.data.timestamp,
            })
          }
          break

        case 'agent_output':
          if (event.data.agent_name) {
            const execution = agentExecutions.value.get(event.data.agent_name)
            if (execution) {
              execution.output = event.data.agent_output
            }
          }
          break

        case 'agent_completed':
          if (event.data.agent_name) {
            const execution = agentExecutions.value.get(event.data.agent_name)
            if (execution) {
              execution.status = 'completed'
              execution.endTime = event.data.timestamp
            }
            if (currentAgent.value === event.data.agent_name) {
              currentAgent.value = null
            }
          }
          break

        case 'approval_required':
          isApprovalRequired.value = true
          approvalContext.value = event.data.approval_context
          approvalPoint.value = event.data.approval_point || null
          if (onApprovalRequired) {
            onApprovalRequired(event.data.approval_context)
          }
          break

        case 'workflow_completed':
          currentAgent.value = null
          if (onComplete) {
            onComplete()
          }
          close()
          break

        case 'workflow_failed':
          if (event.data.agent_name) {
            const execution = agentExecutions.value.get(event.data.agent_name)
            if (execution) {
              execution.status = 'failed'
              execution.error = event.data.error_message
            }
          }
          if (onError && event.data.error_message) {
            onError(new Error(event.data.error_message))
          }
          close()
          break
      }
    } catch (e) {
      console.error('Failed to parse SSE event:', e, 'Raw data:', eventData)
      if (onError) {
        onError(e as Error)
      }
    }
  }

  // 监听data变化并解析事件
  watch(data, (newData) => {
    if (newData) {
      parseEvent(String(newData))
    }
  })

  // 监听错误
  watch(error, (err) => {
    if (err && onError) {
      onError(new Error(String(err)))
    }
  })

  // 计算属性
  const isConnected = computed(() => status.value === 'OPEN')
  const isConnecting = computed(() => status.value === 'CONNECTING')
  const latestEvent = computed(() => events.value[events.value.length - 1])

  // 获取智能体执行列表（按执行顺序）
  const agentExecutionList = computed(() => {
    return Array.from(agentExecutions.value.values())
  })

  // Methods
  const connect = () => {
    open()
  }

  const disconnect = () => {
    close()
  }

  const clearEvents = () => {
    events.value = []
  }

  const resetApprovalState = () => {
    isApprovalRequired.value = false
    approvalContext.value = null
    approvalPoint.value = null
  }

  // 清理
  onUnmounted(() => {
    close()
  })

  return {
    // State
    events,
    currentPhase,
    currentAgent,
    isApprovalRequired,
    approvalContext,
    approvalPoint,
    agentExecutions: agentExecutionList,
    isConnected,
    isConnecting,
    latestEvent,
    error,
    status,
    // Methods
    connect,
    disconnect,
    clearEvents,
    resetApprovalState,
  }
}
