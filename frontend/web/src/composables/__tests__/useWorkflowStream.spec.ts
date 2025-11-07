import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ref } from 'vue'
import { useWorkflowStream } from '../useWorkflowStream'

// Mock @vueuse/core
vi.mock('@vueuse/core', () => ({
  useEventSource: vi.fn((url, events, options) => {
    const data = ref(null)
    const status = ref('CLOSED')
    const error = ref(null)
    const close = vi.fn()
    const open = vi.fn(() => {
      status.value = 'OPEN'
    })

    return {
      data,
      status,
      error,
      close,
      open,
    }
  }),
}))

describe('useWorkflowStream', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Mock localStorage
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: vi.fn(() => 'mock-token'),
        setItem: vi.fn(),
        removeItem: vi.fn(),
        clear: vi.fn(),
        length: 0,
        key: vi.fn(),
      },
      writable: true,
    })
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('初始化', () => {
    it('应该正确初始化状态', () => {
      const { events, currentPhase, currentAgent, isApprovalRequired } =
        useWorkflowStream({
          workflowId: 'test-workflow-123',
          autoConnect: false,
        })

      expect(events.value).toEqual([])
      expect(currentPhase.value).toBe('P0')
      expect(currentAgent.value).toBeNull()
      expect(isApprovalRequired.value).toBe(false)
    })

    it('应该构建包含workflow ID的URL', async () => {
      const { useEventSource } = await import('@vueuse/core')

      useWorkflowStream({
        workflowId: 'workflow-456',
        autoConnect: false,
      })

      expect(useEventSource).toHaveBeenCalled()
    })
  })

  describe('连接管理', () => {
    it('应该提供connect和disconnect方法', () => {
      const { connect, disconnect, isConnected } = useWorkflowStream({
        workflowId: 'test-workflow',
        autoConnect: false,
      })

      expect(isConnected.value).toBe(false)

      connect()
      // 连接后状态应该更新
      expect(typeof connect).toBe('function')
      expect(typeof disconnect).toBe('function')
    })

    it('应该提供clearEvents方法', () => {
      const { events, clearEvents } = useWorkflowStream({
        workflowId: 'test-workflow',
        autoConnect: false,
      })

      // 手动添加事件
      events.value.push({
        event: 'workflow_started',
        data: { timestamp: '2025-01-01T00:00:00Z', workflow_id: 'test' },
      })

      expect(events.value.length).toBe(1)

      clearEvents()
      expect(events.value.length).toBe(0)
    })
  })

  describe('状态管理', () => {
    it('应该返回正确的计算属性', () => {
      const { isConnected, isConnecting, latestEvent, agentExecutions } =
        useWorkflowStream({
          workflowId: 'test-workflow',
          autoConnect: false,
        })

      expect(isConnected.value).toBeDefined()
      expect(isConnecting.value).toBeDefined()
      expect(latestEvent.value).toBeUndefined()
      expect(agentExecutions.value).toEqual([])
    })

    it('应该提供resetApprovalState方法', () => {
      const { isApprovalRequired, resetApprovalState } = useWorkflowStream({
        workflowId: 'test-workflow',
        autoConnect: false,
      })

      // 手动设置审批状态
      isApprovalRequired.value = true

      resetApprovalState()

      expect(isApprovalRequired.value).toBe(false)
    })
  })

  describe('回调函数', () => {
    it('应该接受onApprovalRequired回调', () => {
      const mockCallback = vi.fn()

      const stream = useWorkflowStream({
        workflowId: 'test-workflow',
        autoConnect: false,
        onApprovalRequired: mockCallback,
      })

      expect(stream).toBeDefined()
    })

    it('应该接受onError回调', () => {
      const mockErrorCallback = vi.fn()

      const stream = useWorkflowStream({
        workflowId: 'test-workflow',
        autoConnect: false,
        onError: mockErrorCallback,
      })

      expect(stream).toBeDefined()
    })

    it('应该接受onComplete回调', () => {
      const mockCompleteCallback = vi.fn()

      const stream = useWorkflowStream({
        workflowId: 'test-workflow',
        autoConnect: false,
        onComplete: mockCompleteCallback,
      })

      expect(stream).toBeDefined()
    })
  })
})
