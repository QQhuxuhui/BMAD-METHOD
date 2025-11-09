/**
 * Mock SSE服务器
 * Story 1.9: 实时工作流监控面板MVP
 *
 * 模拟Server-Sent Events流式推送工作流事件
 */

import type { WorkflowEvent, MockSSEConfig } from '@/types/workflow'
import { getScenarioEvents } from './workflow-events'

export type EventListener = (event: WorkflowEvent) => void

/**
 * Mock SSE服务器类
 */
export class MockSSEServer {
  private events: WorkflowEvent[] = []
  private eventIndex = 0
  private intervalId: number | null = null
  private listeners: EventListener[] = []
  private config: Required<MockSSEConfig>

  constructor(config: MockSSEConfig = {}) {
    this.config = {
      intervalMs: config.intervalMs ?? 1500,
      autoStart: config.autoStart ?? false,
      scenario: config.scenario ?? 'success'
    }

    this.loadScenario(this.config.scenario)

    if (this.config.autoStart) {
      this.start()
    }
  }

  /**
   * 加载指定场景的事件数据
   */
  loadScenario(scenario: 'success' | 'failure' | 'pause' | 'long-running') {
    this.events = getScenarioEvents(scenario)
    this.eventIndex = 0
  }

  /**
   * 开始发送事件流
   */
  start(intervalMs?: number) {
    if (this.intervalId !== null) {
      console.warn('Mock SSE Server already running')
      return
    }

    const interval = intervalMs ?? this.config.intervalMs

    console.log(`[Mock SSE] Starting with ${this.events.length} events, interval: ${interval}ms`)

    this.intervalId = window.setInterval(() => {
      if (this.eventIndex < this.events.length) {
        const event = this.events[this.eventIndex]

        // 更新事件时间戳为当前时间
        event.data.timestamp = new Date().toISOString()

        console.log(`[Mock SSE] Sending event ${this.eventIndex + 1}/${this.events.length}:`, event.event)

        // 通知所有监听器
        this.listeners.forEach(listener => {
          try {
            listener(event)
          } catch (error) {
            console.error('[Mock SSE] Listener error:', error)
          }
        })

        this.eventIndex++
      } else {
        console.log('[Mock SSE] All events sent, stopping')
        this.stop()
      }
    }, interval)
  }

  /**
   * 停止发送事件流
   */
  stop() {
    if (this.intervalId !== null) {
      clearInterval(this.intervalId)
      this.intervalId = null
      console.log('[Mock SSE] Stopped')
    }
  }

  /**
   * 暂停事件流
   */
  pause() {
    this.stop()
    console.log(`[Mock SSE] Paused at event ${this.eventIndex}/${this.events.length}`)
  }

  /**
   * 恢复事件流
   */
  resume() {
    if (this.eventIndex < this.events.length) {
      this.start()
      console.log('[Mock SSE] Resumed')
    } else {
      console.warn('[Mock SSE] No more events to send')
    }
  }

  /**
   * 添加事件监听器
   */
  addEventListener(listener: EventListener): () => void {
    this.listeners.push(listener)

    // 返回取消监听的函数
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener)
    }
  }

  /**
   * 移除事件监听器
   */
  removeEventListener(listener: EventListener) {
    this.listeners = this.listeners.filter(l => l !== listener)
  }

  /**
   * 移除所有监听器
   */
  removeAllListeners() {
    this.listeners = []
  }

  /**
   * 重置服务器状态
   */
  reset(scenario?: 'success' | 'failure' | 'pause' | 'long-running') {
    this.stop()
    this.eventIndex = 0
    this.listeners = []

    if (scenario) {
      this.loadScenario(scenario)
    }

    console.log('[Mock SSE] Reset complete')
  }

  /**
   * 跳到指定事件索引
   */
  seekTo(index: number) {
    if (index >= 0 && index < this.events.length) {
      const wasRunning = this.intervalId !== null
      this.stop()
      this.eventIndex = index
      if (wasRunning) {
        this.start()
      }
      console.log(`[Mock SSE] Seeked to event ${index}`)
    } else {
      console.warn(`[Mock SSE] Invalid event index: ${index}`)
    }
  }

  /**
   * 手动发送下一个事件（用于调试）
   */
  sendNext() {
    if (this.eventIndex < this.events.length) {
      const event = this.events[this.eventIndex]
      event.data.timestamp = new Date().toISOString()

      this.listeners.forEach(listener => listener(event))
      this.eventIndex++

      console.log(`[Mock SSE] Manually sent event ${this.eventIndex}/${this.events.length}`)
      return true
    }
    return false
  }

  /**
   * 获取服务器状态
   */
  getStatus() {
    return {
      isRunning: this.intervalId !== null,
      currentIndex: this.eventIndex,
      totalEvents: this.events.length,
      progress: this.events.length > 0 ? (this.eventIndex / this.events.length) * 100 : 0,
      remainingEvents: this.events.length - this.eventIndex,
      listenerCount: this.listeners.length
    }
  }

  /**
   * 设置发送间隔
   */
  setInterval(intervalMs: number) {
    this.config.intervalMs = intervalMs
    if (this.intervalId !== null) {
      this.stop()
      this.start(intervalMs)
    }
  }

  /**
   * 获取所有事件（用于预览）
   */
  getAllEvents(): WorkflowEvent[] {
    return [...this.events]
  }

  /**
   * 获取指定范围的事件
   */
  getEvents(start: number, end?: number): WorkflowEvent[] {
    return this.events.slice(start, end)
  }
}

/**
 * 创建并导出单例实例
 */
export const mockSSEServer = new MockSSEServer({
  scenario: 'success',
  autoStart: false
})

/**
 * 用于调试的全局访问
 */
if (import.meta.env.DEV) {
  ;(window as any).__mockSSEServer = mockSSEServer
  console.log('[Mock SSE] Server instance available at window.__mockSSEServer')
}
