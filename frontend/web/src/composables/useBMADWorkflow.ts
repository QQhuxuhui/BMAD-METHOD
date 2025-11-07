/**
 * Vue 3 Composition API hook for BMAD workflow execution via LangServe.
 *
 * This composable provides an easy-to-use interface for executing BMAD workflows
 * with SSE streaming support using the LangServe API endpoints.
 *
 * @example
 * ```typescript
 * import { useBMADWorkflow } from '@/composables/useBMADWorkflow'
 *
 * const { runWorkflow, isStreaming, output, error } = useBMADWorkflow()
 *
 * await runWorkflow({
 *   problem_description: '优化配送路线',
 *   domain: 'logistics',
 *   constraints: ['时间窗口', '车辆容量']
 * })
 * ```
 */

import { ref, Ref } from 'vue'

/**
 * Workflow input interface.
 */
export interface WorkflowInput {
  problem_description: string
  domain?: string
  constraints?: string[]
}

/**
 * Workflow event interface.
 */
export interface WorkflowEvent {
  event: string
  data: Record<string, any>
  timestamp?: string
}

/**
 * Workflow result interface.
 */
export interface WorkflowResult {
  workflow_id: string
  status: string
  current_phase: string
  output_data?: Record<string, any>
  error_message?: string
  total_tokens: number
  total_cost: number
}

/**
 * Composable hook for BMAD workflow execution.
 */
export function useBMADWorkflow() {
  // State
  const isStreaming: Ref<boolean> = ref(false)
  const events: Ref<WorkflowEvent[]> = ref([])
  const result: Ref<WorkflowResult | null> = ref(null)
  const error: Ref<Error | null> = ref(null)

  // API configuration
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  const WORKFLOW_STREAM_URL = `${API_BASE_URL}/api/v1/bmad-workflow/stream`
  const WORKFLOW_INVOKE_URL = `${API_BASE_URL}/api/v1/bmad-workflow/invoke`

  /**
   * Get JWT token from local storage or session.
   *
   * @returns JWT token string
   */
  const getToken = (): string => {
    // TODO: Replace with your actual token retrieval logic
    return localStorage.getItem('jwt_token') || sessionStorage.getItem('jwt_token') || ''
  }

  /**
   * Run workflow with SSE streaming.
   *
   * This method creates a workflow and streams execution events in real-time
   * using Server-Sent Events (SSE).
   *
   * @param input - Workflow input data
   */
  const runWorkflowStream = async (input: WorkflowInput): Promise<void> => {
    isStreaming.value = true
    events.value = []
    error.value = null
    result.value = null

    try {
      const token = getToken()
      if (!token) {
        throw new Error('JWT token not found. Please login first.')
      }

      // Create EventSource for SSE streaming
      // Note: EventSource doesn't support custom headers directly,
      // so we need to use fetch with streaming response
      const response = await fetch(WORKFLOW_STREAM_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ input }),
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      // Read SSE stream
      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (!reader) {
        throw new Error('Response body is not readable')
      }

      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()

        if (done) {
          break
        }

        // Decode chunk and add to buffer
        buffer += decoder.decode(value, { stream: true })

        // Process complete SSE messages
        const lines = buffer.split('\n\n')
        buffer = lines.pop() || '' // Keep incomplete message in buffer

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.substring(6) // Remove 'data: ' prefix
            try {
              const event: WorkflowEvent = JSON.parse(data)
              events.value.push(event)

              // Check for completion events
              if (event.event === 'workflow_complete' || event.event === 'workflow_failed') {
                // Extract final result if available
                if (event.data) {
                  result.value = event.data as WorkflowResult
                }
              }
            } catch (e) {
              console.error('Failed to parse SSE event:', e, data)
            }
          }
        }
      }
    } catch (e) {
      error.value = e as Error
      console.error('Workflow stream error:', e)
    } finally {
      isStreaming.value = false
    }
  }

  /**
   * Run workflow synchronously (blocking until complete).
   *
   * This method invokes the workflow and waits for the final result,
   * without streaming intermediate events.
   *
   * @param input - Workflow input data
   * @returns Workflow execution result
   */
  const runWorkflowInvoke = async (input: WorkflowInput): Promise<WorkflowResult | null> => {
    isStreaming.value = true
    error.value = null
    result.value = null

    try {
      const token = getToken()
      if (!token) {
        throw new Error('JWT token not found. Please login first.')
      }

      const response = await fetch(WORKFLOW_INVOKE_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ input }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      result.value = data.output as WorkflowResult

      return result.value
    } catch (e) {
      error.value = e as Error
      console.error('Workflow invoke error:', e)
      return null
    } finally {
      isStreaming.value = false
    }
  }

  /**
   * Clear all state.
   */
  const reset = (): void => {
    isStreaming.value = false
    events.value = []
    result.value = null
    error.value = null
  }

  return {
    // State
    isStreaming,
    events,
    result,
    error,

    // Methods
    runWorkflowStream,
    runWorkflowInvoke,
    reset,
  }
}
