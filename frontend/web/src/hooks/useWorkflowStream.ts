/**
 * useWorkflowStream Hook
 * Story 1.9: 实时工作流监控面板MVP
 *
 * 提供工作流SSE流式接收功能（支持Mock和真实API）
 */

import { ref, onUnmounted, readonly, computed } from 'vue'
import type { Ref } from 'vue'
import type { WorkflowEvent, UseWorkflowStreamOptions } from '@/types/workflow'
import { mockSSEServer } from '@/mocks/mock-sse-server'
import { useWorkflowStore } from '@/stores/workflow'

export interface UseWorkflowStreamReturn {
  /** 连接状态 */
  status: Readonly<Ref<'idle' | 'connecting' | 'connected' | 'disconnected' | 'error'>>
  /** 错误信息 */
  error: Readonly<Ref<Error | null>>
  /** 是否正在运行 */
  isRunning: Readonly<Ref<boolean>>
  /** 开始连接 */
  connect: () => void
  /** 断开连接 */
  disconnect: () => void
  /** 重新连接 */
  reconnect: () => void
}

/**
 * 工作流SSE流Hook
 *
 * @param options 配置选项
 * @param useMock 是否使用Mock数据（默认：开发环境下为true）
 * @returns Hook返回值
 *
 * @example
 * ```ts
 * const { status, isRunning, connect, disconnect } = useWorkflowStream({
 *   workflowId: 'wf-001',
 *   autoConnect: true,
 *   onApprovalRequired: (context) => {
 *     console.log('需要审批:', context)
 *   }
 * })
 * ```
 */
export function useWorkflowStream(
  options: UseWorkflowStreamOptions,
  useMock = import.meta.env.DEV
): UseWorkflowStreamReturn {
  const workflowStore = useWorkflowStore()

  const status = ref<'idle' | 'connecting' | 'connected' | 'disconnected' | 'error'>('idle')
  const error = ref<Error | null>(null)

  let eventSource: EventSource | null = null
  let unsubscribeMock: (() => void) | null = null

  const isRunning = computed(() => status.value === 'connected' || status.value === 'connecting')

  /**
   * 处理接收到的事件
   */
  const handleEvent = (event: WorkflowEvent) => {
    console.log('[useWorkflowStream] Received event:', event.event, event.data)

    // 更新Store状态
    workflowStore.processEvent(event)

    // 处理特定事件类型
    switch (event.event) {
      case 'approval_required':
        if (options.onApprovalRequired) {
          options.onApprovalRequired(event.data.approval_context)
        }
        break

      case 'workflow_completed':
        if (options.onComplete) {
          options.onComplete()
        }
        disconnect()
        break

      case 'workflow_failed':
      case 'agent_failed':
        const err = new Error(event.data.error_message || '工作流执行失败')
        error.value = err
        if (options.onError) {
          options.onError(err)
        }
        break
    }
  }

  /**
   * 使用Mock SSE服务器连接
   */
  const connectMock = () => {
    console.log('[useWorkflowStream] Connecting to Mock SSE...')
    status.value = 'connecting'
    error.value = null

    try {
      // 重置Mock服务器
      mockSSEServer.reset('success')

      // 订阅事件
      unsubscribeMock = mockSSEServer.addEventListener(handleEvent)

      // 启动Mock服务器
      mockSSEServer.start()

      status.value = 'connected'
      console.log('[useWorkflowStream] Connected to Mock SSE')
    } catch (err) {
      status.value = 'error'
      error.value = err as Error
      console.error('[useWorkflowStream] Mock connection error:', err)

      if (options.onError) {
        options.onError(err as Error)
      }
    }
  }

  /**
   * 使用真实SSE API连接
   */
  const connectReal = () => {
    console.log('[useWorkflowStream] Connecting to real SSE...')
    status.value = 'connecting'
    error.value = null

    try {
      // 构建SSE URL
      const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      const url = `${baseUrl}/api/v1/workflows/${options.workflowId}/stream`

      console.log('[useWorkflowStream] SSE URL:', url)

      // 创建EventSource
      eventSource = new EventSource(url)

      eventSource.onopen = () => {
        status.value = 'connected'
        console.log('[useWorkflowStream] Connected to SSE')
      }

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data) as WorkflowEvent
          handleEvent(data)
        } catch (err) {
          console.error('[useWorkflowStream] Failed to parse SSE event:', err)
        }
      }

      eventSource.onerror = (err) => {
        console.error('[useWorkflowStream] SSE error:', err)
        status.value = 'error'
        error.value = new Error('SSE连接错误')

        if (options.onError) {
          options.onError(error.value)
        }

        eventSource?.close()
      }
    } catch (err) {
      status.value = 'error'
      error.value = err as Error
      console.error('[useWorkflowStream] Connection error:', err)

      if (options.onError) {
        options.onError(err as Error)
      }
    }
  }

  /**
   * 开始连接
   */
  const connect = () => {
    if (useMock) {
      connectMock()
    } else {
      connectReal()
    }
  }

  /**
   * 断开连接
   */
  const disconnect = () => {
    console.log('[useWorkflowStream] Disconnecting...')

    if (useMock) {
      mockSSEServer.stop()
      if (unsubscribeMock) {
        unsubscribeMock()
        unsubscribeMock = null
      }
    } else {
      eventSource?.close()
      eventSource = null
    }

    status.value = 'disconnected'
    console.log('[useWorkflowStream] Disconnected')
  }

  /**
   * 重新连接
   */
  const reconnect = () => {
    disconnect()
    setTimeout(() => {
      connect()
    }, 100)
  }

  // 自动连接
  if (options.autoConnect) {
    connect()
  }

  // 组件卸载时自动断开
  onUnmounted(() => {
    disconnect()
  })

  return {
    status: readonly(status),
    error: readonly(error),
    isRunning: readonly(isRunning),
    connect,
    disconnect,
    reconnect
  }
}
