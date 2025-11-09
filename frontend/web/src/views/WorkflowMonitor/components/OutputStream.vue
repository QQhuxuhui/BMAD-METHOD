<template>
  <a-card title="实时输出流" :bordered="false" class="output-stream">
    <template #extra>
      <a-space>
        <a-input-search
          v-model:value="searchText"
          placeholder="搜索输出内容..."
          style="width: 200px"
          size="small"
          allow-clear
        />
        <a-button size="small" @click="handleClear">
          <template #icon>
            <DeleteOutlined />
          </template>
          清空
        </a-button>
        <a-button size="small" @click="handleScrollToBottom">
          <template #icon>
            <VerticalAlignBottomOutlined />
          </template>
          滚动到底部
        </a-button>
      </a-space>
    </template>

    <div ref="streamContainer" class="stream-container">
      <a-empty v-if="filteredEvents.length === 0" description="暂无输出内容">
        <template #image>
          <FileTextOutlined :style="{ fontSize: '48px', color: '#d9d9d9' }" />
        </template>
      </a-empty>

      <div v-else class="events-list">
        <div
          v-for="(event, index) in filteredEvents"
          :key="index"
          class="event-item"
          :class="`event-type-${event.event}`"
        >
          <!-- 事件头部 -->
          <div class="event-header">
            <a-tag :color="getEventColor(event.event)" size="small">
              {{ getEventLabel(event.event) }}
            </a-tag>
            <span v-if="event.data.agent_name" class="agent-name">
              {{ event.data.agent_name }}
            </span>
            <span class="event-time">
              {{ formatTime(event.data.timestamp) }}
            </span>
          </div>

          <!-- 事件内容 -->
          <div v-if="event.event === 'agent_output'" class="event-content">
            <pre class="output-text">{{ formatOutput(event.data.agent_output) }}</pre>
          </div>

          <div v-else-if="event.data.error_message" class="event-content error">
            <ExclamationCircleOutlined class="error-icon" />
            {{ event.data.error_message }}
          </div>

          <div v-else-if="event.event === 'approval_required'" class="event-content approval">
            <InfoCircleOutlined class="approval-icon" />
            需要在 {{ event.data.approval_point }} 进行审批确认
          </div>
        </div>
      </div>
    </div>

    <template #actions>
      <div class="stream-footer">
        <span class="footer-info">
          共 {{ events.length }} 条事件
          <span v-if="searchText">（过滤后 {{ filteredEvents.length }} 条）</span>
        </span>
      </div>
    </template>
  </a-card>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { useWorkflowStore } from '@/stores/workflow'
import type { WorkflowEvent } from '@/types/workflow'
import {
  DeleteOutlined,
  VerticalAlignBottomOutlined,
  FileTextOutlined,
  ExclamationCircleOutlined,
  InfoCircleOutlined
} from '@ant-design/icons-vue'
import dayjs from 'dayjs'

// Store
const workflowStore = useWorkflowStore()

// Refs
const streamContainer = ref<HTMLElement>()
const searchText = ref('')

// Computed
const events = computed(() => workflowStore.events)

/**
 * 过滤后的事件列表
 */
const filteredEvents = computed(() => {
  if (!searchText.value) return events.value

  const keyword = searchText.value.toLowerCase()
  return events.value.filter(event => {
    const agentName = event.data.agent_name?.toLowerCase() || ''
    const content = JSON.stringify(event.data.agent_output || '').toLowerCase()
    const error = event.data.error_message?.toLowerCase() || ''

    return agentName.includes(keyword) || content.includes(keyword) || error.includes(keyword)
  })
})

/**
 * 监听事件变化，自动滚动到底部
 */
watch(
  events,
  () => {
    nextTick(() => {
      if (streamContainer.value) {
        streamContainer.value.scrollTop = streamContainer.value.scrollHeight
      }
    })
  },
  { deep: true }
)

/**
 * 获取事件颜色
 */
const getEventColor = (eventType: string) => {
  switch (eventType) {
    case 'workflow_started':
      return 'blue'
    case 'agent_started':
      return 'cyan'
    case 'agent_output':
      return 'default'
    case 'agent_completed':
      return 'green'
    case 'agent_failed':
    case 'workflow_failed':
      return 'red'
    case 'approval_required':
      return 'orange'
    case 'workflow_completed':
      return 'success'
    default:
      return 'default'
  }
}

/**
 * 获取事件标签
 */
const getEventLabel = (eventType: string) => {
  switch (eventType) {
    case 'workflow_started':
      return '工作流启动'
    case 'phase_changed':
      return '阶段切换'
    case 'agent_started':
      return '智能体启动'
    case 'agent_output':
      return '输出'
    case 'agent_completed':
      return '智能体完成'
    case 'agent_failed':
      return '智能体失败'
    case 'approval_required':
      return '等待审批'
    case 'workflow_paused':
      return '工作流暂停'
    case 'workflow_resumed':
      return '工作流恢复'
    case 'workflow_completed':
      return '工作流完成'
    case 'workflow_failed':
      return '工作流失败'
    default:
      return eventType
  }
}

/**
 * 格式化时间
 */
const formatTime = (timestamp: string) => {
  return dayjs(timestamp).format('HH:mm:ss.SSS')
}

/**
 * 格式化输出内容
 */
const formatOutput = (output: any) => {
  if (!output) return ''

  if (typeof output === 'object') {
    if (output.content) return output.content
    return JSON.stringify(output, null, 2)
  }

  return String(output)
}

/**
 * 清空输出
 */
const handleClear = () => {
  // 这里应该调用Store的清空方法，但为了不影响当前工作流，暂时不实现
  console.log('Clear output stream')
}

/**
 * 滚动到底部
 */
const handleScrollToBottom = () => {
  if (streamContainer.value) {
    streamContainer.value.scrollTo({
      top: streamContainer.value.scrollHeight,
      behavior: 'smooth'
    })
  }
}
</script>

<style scoped lang="scss">
.output-stream {
  height: 100%;
  display: flex;
  flex-direction: column;

  .stream-container {
    height: 500px;
    overflow-y: auto;
    padding: 12px;
    background-color: #fafafa;
    border-radius: 4px;

    &::-webkit-scrollbar {
      width: 8px;
    }

    &::-webkit-scrollbar-track {
      background: #f0f0f0;
      border-radius: 4px;
    }

    &::-webkit-scrollbar-thumb {
      background: #bfbfbf;
      border-radius: 4px;

      &:hover {
        background: #999;
      }
    }

    .events-list {
      .event-item {
        margin-bottom: 16px;
        padding: 12px;
        background: white;
        border-radius: 4px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        transition: all 0.3s;

        &:hover {
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .event-header {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 8px;
          font-size: 13px;

          .agent-name {
            font-weight: 500;
            color: rgba(0, 0, 0, 0.85);
          }

          .event-time {
            margin-left: auto;
            font-size: 12px;
            color: rgba(0, 0, 0, 0.45);
            font-family: 'Courier New', monospace;
          }
        }

        .event-content {
          font-size: 14px;
          line-height: 1.6;
          color: rgba(0, 0, 0, 0.75);

          .output-text {
            margin: 0;
            padding: 8px 12px;
            background-color: #f6f6f6;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.5;
            white-space: pre-wrap;
            word-wrap: break-word;
            overflow-x: auto;
          }

          &.error {
            color: #ff4d4f;
            display: flex;
            align-items: center;
            gap: 8px;

            .error-icon {
              font-size: 16px;
            }
          }

          &.approval {
            color: #fa8c16;
            display: flex;
            align-items: center;
            gap: 8px;

            .approval-icon {
              font-size: 16px;
            }
          }
        }
      }
    }
  }

  .stream-footer {
    padding: 8px 0;
    text-align: center;
    border-top: 1px solid #f0f0f0;

    .footer-info {
      font-size: 13px;
      color: rgba(0, 0, 0, 0.45);
    }
  }
}
</style>
