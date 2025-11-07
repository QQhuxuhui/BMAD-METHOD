<template>
  <div class="real-time-log">
    <a-card title="实时日志">
      <template #extra>
        <a-space>
          <!-- 事件类型过滤 -->
          <a-select
            v-model:value="selectedEventType"
            placeholder="过滤事件类型"
            style="width: 180px"
            allow-clear
          >
            <a-select-option value="">全部</a-select-option>
            <a-select-option
              v-for="type in eventTypes"
              :key="type"
              :value="type"
            >
              {{ getEventTypeLabel(type) }}
            </a-select-option>
          </a-select>

          <!-- 搜索 -->
          <a-input-search
            v-model:value="searchKeyword"
            placeholder="搜索日志..."
            style="width: 200px"
            allow-clear
          />

          <!-- 自动滚动开关 -->
          <a-switch
            v-model:checked="autoScroll"
            checked-children="自动滚动"
            un-checked-children="手动滚动"
          />

          <!-- 清空按钮 -->
          <a-button @click="handleClear" size="small">清空</a-button>
        </a-space>
      </template>

      <div class="log-container" ref="logContainerRef">
        <div class="log-list">
          <template v-if="filteredEvents.length > 0">
            <div
              v-for="(event, index) in filteredEvents"
              :key="index"
              class="log-item"
              :class="`log-type-${event.event}`"
            >
              <div class="log-timestamp">
                {{ formatTime(event.data.timestamp) }}
              </div>
              <div class="log-type">
                <a-tag :color="getEventColor(event.event)" size="small">
                  {{ getEventTypeLabel(event.event) }}
                </a-tag>
              </div>
              <div class="log-content">
                {{ getLogMessage(event) }}
              </div>
              <div class="log-actions">
                <a-button
                  type="link"
                  size="small"
                  @click="handleViewDetail(event)"
                >
                  详情
                </a-button>
              </div>
            </div>
          </template>
          <a-empty v-else description="暂无日志" />
        </div>
      </div>

      <!-- 日志统计 -->
      <div class="log-stats">
        <a-space>
          <span>总计: {{ events.length }} 条</span>
          <span v-if="selectedEventType || searchKeyword">
            过滤后: {{ filteredEvents.length }} 条
          </span>
        </a-space>
      </div>
    </a-card>

    <!-- 日志详情Modal -->
    <a-modal
      v-model:open="detailModalVisible"
      title="日志详情"
      width="800px"
      :footer="null"
    >
      <template v-if="selectedEvent">
        <a-descriptions :column="1" bordered>
          <a-descriptions-item label="事件类型">
            <a-tag :color="getEventColor(selectedEvent.event)">
              {{ getEventTypeLabel(selectedEvent.event) }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="时间">
            {{ formatDateTime(selectedEvent.data.timestamp) }}
          </a-descriptions-item>
          <a-descriptions-item label="工作流ID">
            {{ selectedEvent.data.workflow_id }}
          </a-descriptions-item>
          <a-descriptions-item label="阶段" v-if="selectedEvent.data.phase">
            {{ selectedEvent.data.phase }}
          </a-descriptions-item>
          <a-descriptions-item
            label="智能体"
            v-if="selectedEvent.data.agent_name"
          >
            {{ selectedEvent.data.agent_name }}
          </a-descriptions-item>
        </a-descriptions>

        <a-divider>事件数据</a-divider>
        <a-card size="small">
          <pre class="event-data">{{ JSON.stringify(selectedEvent.data, null, 2) }}</pre>
        </a-card>
      </template>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import dayjs from 'dayjs'
import type { WorkflowEvent, WorkflowEventType } from '@/types/workflow'

interface Props {
  events: WorkflowEvent[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'clear'): void
}>()

// State
const selectedEventType = ref<WorkflowEventType | ''>('')
const searchKeyword = ref('')
const autoScroll = ref(true)
const logContainerRef = ref<HTMLElement>()
const detailModalVisible = ref(false)
const selectedEvent = ref<WorkflowEvent | null>(null)

// 事件类型列表
const eventTypes: WorkflowEventType[] = [
  'workflow_started',
  'phase_changed',
  'agent_started',
  'agent_output',
  'agent_completed',
  'approval_required',
  'workflow_completed',
  'workflow_failed',
]

// 事件类型标签映射
const eventTypeLabels: Record<WorkflowEventType, string> = {
  workflow_started: '工作流启动',
  phase_changed: '阶段变更',
  agent_started: '智能体启动',
  agent_output: '智能体输出',
  agent_completed: '智能体完成',
  approval_required: '需要审批',
  workflow_completed: '工作流完成',
  workflow_failed: '工作流失败',
}

// 事件颜色映射
const eventColors: Record<WorkflowEventType, string> = {
  workflow_started: 'blue',
  phase_changed: 'cyan',
  agent_started: 'processing',
  agent_output: 'default',
  agent_completed: 'success',
  approval_required: 'warning',
  workflow_completed: 'success',
  workflow_failed: 'error',
}

// 过滤后的事件
const filteredEvents = computed(() => {
  let result = props.events

  // 按事件类型过滤
  if (selectedEventType.value) {
    result = result.filter((e) => e.event === selectedEventType.value)
  }

  // 按关键词搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter((e) => {
      const message = getLogMessage(e).toLowerCase()
      return (
        message.includes(keyword) ||
        e.event.includes(keyword) ||
        e.data.agent_name?.toLowerCase().includes(keyword)
      )
    })
  }

  return result
})

// 获取事件类型标签
const getEventTypeLabel = (type: WorkflowEventType) => {
  return eventTypeLabels[type] || type
}

// 获取事件颜色
const getEventColor = (type: WorkflowEventType) => {
  return eventColors[type] || 'default'
}

// 获取日志消息
const getLogMessage = (event: WorkflowEvent): string => {
  switch (event.event) {
    case 'workflow_started':
      return `工作流 ${event.data.workflow_id} 已启动`
    case 'phase_changed':
      return `阶段变更为 ${event.data.phase}`
    case 'agent_started':
      return `智能体 ${event.data.agent_name} 开始执行`
    case 'agent_output':
      return `智能体 ${event.data.agent_name} 产生输出`
    case 'agent_completed':
      return `智能体 ${event.data.agent_name} 执行完成`
    case 'approval_required':
      return `需要人工审批 (${event.data.approval_point})`
    case 'workflow_completed':
      return '工作流执行完成'
    case 'workflow_failed':
      return `工作流执行失败: ${event.data.error_message || '未知错误'}`
    default:
      return JSON.stringify(event.data)
  }
}

// 格式化时间
const formatTime = (time: string) => {
  return dayjs(time).format('HH:mm:ss.SSS')
}

const formatDateTime = (time: string) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

// 查看详情
const handleViewDetail = (event: WorkflowEvent) => {
  selectedEvent.value = event
  detailModalVisible.value = true
}

// 清空日志
const handleClear = () => {
  emit('clear')
}

// 自动滚动到底部
const scrollToBottom = () => {
  if (autoScroll.value && logContainerRef.value) {
    nextTick(() => {
      if (logContainerRef.value) {
        logContainerRef.value.scrollTop = logContainerRef.value.scrollHeight
      }
    })
  }
}

// 监听事件变化，自动滚动
watch(
  () => props.events.length,
  () => {
    scrollToBottom()
  },
)
</script>

<style scoped lang="scss">
.real-time-log {
  .log-container {
    max-height: 600px;
    overflow-y: auto;
    border: 1px solid #f0f0f0;
    border-radius: 4px;
    background: #fafafa;
  }

  .log-list {
    padding: 12px;
  }

  .log-item {
    display: grid;
    grid-template-columns: 100px 120px 1fr 80px;
    gap: 12px;
    align-items: center;
    padding: 8px 12px;
    margin-bottom: 8px;
    background: #fff;
    border-radius: 4px;
    border-left: 3px solid transparent;
    transition: all 0.3s;

    &:hover {
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }

    &.log-type-workflow_started {
      border-left-color: #1890ff;
    }

    &.log-type-phase_changed {
      border-left-color: #13c2c2;
    }

    &.log-type-agent_started {
      border-left-color: #1890ff;
    }

    &.log-type-agent_completed {
      border-left-color: #52c41a;
    }

    &.log-type-approval_required {
      border-left-color: #faad14;
    }

    &.log-type-workflow_completed {
      border-left-color: #52c41a;
    }

    &.log-type-workflow_failed {
      border-left-color: #ff4d4f;
    }

    .log-timestamp {
      font-size: 12px;
      color: rgba(0, 0, 0, 0.45);
      font-family: monospace;
    }

    .log-type {
      flex-shrink: 0;
    }

    .log-content {
      font-size: 13px;
      color: rgba(0, 0, 0, 0.85);
      word-break: break-word;
    }

    .log-actions {
      flex-shrink: 0;
      text-align: right;
    }
  }

  .log-stats {
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid #f0f0f0;
    font-size: 13px;
    color: rgba(0, 0, 0, 0.45);
  }

  .event-data {
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 12px;
    line-height: 1.5;
    max-height: 400px;
    overflow: auto;
    background: #f5f5f5;
    padding: 12px;
    border-radius: 4px;
  }
}
</style>
