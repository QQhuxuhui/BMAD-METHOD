<template>
  <a-card title="智能体执行状态" :bordered="false" class="agent-status-list">
    <a-list :data-source="agents" :split="false">
      <template #renderItem="{ item: agent }">
        <a-list-item
          :class="['agent-item', { active: agent.status === 'running' }]"
          @click="handleAgentClick(agent)"
        >
          <a-list-item-meta>
            <template #avatar>
              <a-badge :status="getStatusBadge(agent.status)" :dot="agent.status === 'running'">
                <a-avatar :style="getAvatarStyle(agent.status)">
                  <template #icon>
                    <component :is="getStatusIcon(agent.status)" :spin="agent.status === 'running'" />
                  </template>
                </a-avatar>
              </a-badge>
            </template>

            <template #title>
              <div class="agent-title">
                <span class="agent-name">{{ agent.name }}</span>
                <a-tag :color="getStatusColor(agent.status)" class="status-tag">
                  {{ getStatusText(agent.status) }}
                </a-tag>
              </div>
            </template>

            <template #description>
              <div class="agent-description">
                <div v-if="agent.startTime" class="agent-time">
                  <ClockCircleOutlined class="time-icon" />
                  <span v-if="agent.status === 'running'">
                    进行中: {{ formatElapsed(agent.startTime) }}
                  </span>
                  <span v-else-if="agent.endTime">
                    用时: {{ formatDuration(agent.startTime, agent.endTime) }}
                  </span>
                  <span v-else>
                    开始于 {{ formatTime(agent.startTime) }}
                  </span>
                </div>

                <div v-if="agent.error" class="agent-error">
                  <ExclamationCircleOutlined class="error-icon" />
                  <span>{{ agent.error }}</span>
                </div>

                <div v-if="agent.output && showPreview" class="agent-output-preview">
                  {{ truncateOutput(agent.output) }}
                </div>
              </div>
            </template>
          </a-list-item-meta>

          <template #actions>
            <a-button
              v-if="agent.output"
              type="link"
              size="small"
              @click.stop="handleViewOutput(agent)"
            >
              查看输出
            </a-button>
          </template>
        </a-list-item>
      </template>

      <template #header>
        <div class="list-header">
          <a-space>
            <span class="header-label">进度:</span>
            <span class="header-value">{{ completedCount }} / {{ totalCount }}</span>
          </a-space>
          <a-switch
            v-model:checked="showPreview"
            checked-children="显示预览"
            un-checked-children="隐藏预览"
            size="small"
          />
        </div>
      </template>
    </a-list>
  </a-card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useWorkflowStore } from '@/stores/workflow'
import type { AgentExecution } from '@/types/workflow'
import {
  ClockCircleOutlined,
  ExclamationCircleOutlined,
  LoadingOutlined,
  CheckCircleFilled,
  CloseCircleFilled,
  MinusCircleOutlined,
  RobotOutlined
} from '@ant-design/icons-vue'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'

dayjs.extend(relativeTime)
dayjs.locale('zh-cn')

// Emits
const emit = defineEmits<{
  agentClick: [agent: AgentExecution]
  viewOutput: [agent: AgentExecution]
}>()

// Store
const workflowStore = useWorkflowStore()

// State
const showPreview = ref(true)

// Computed
const agents = computed(() => workflowStore.agents)
const completedCount = computed(() => workflowStore.completedAgents.length)
const totalCount = computed(() => agents.value.length)

/**
 * 获取状态Badge类型
 */
const getStatusBadge = (status: string) => {
  switch (status) {
    case 'running':
      return 'processing'
    case 'completed':
      return 'success'
    case 'failed':
      return 'error'
    case 'pending':
      return 'default'
    default:
      return 'default'
  }
}

/**
 * 获取Avatar样式
 */
const getAvatarStyle = (status: string) => {
  const baseStyle = {
    fontSize: '18px'
  }

  switch (status) {
    case 'running':
      return { ...baseStyle, backgroundColor: '#1890ff' }
    case 'completed':
      return { ...baseStyle, backgroundColor: '#52c41a' }
    case 'failed':
      return { ...baseStyle, backgroundColor: '#ff4d4f' }
    case 'pending':
      return { ...baseStyle, backgroundColor: '#d9d9d9' }
    default:
      return { ...baseStyle, backgroundColor: '#d9d9d9' }
  }
}

/**
 * 获取状态图标
 */
const getStatusIcon = (status: string) => {
  switch (status) {
    case 'running':
      return LoadingOutlined
    case 'completed':
      return CheckCircleFilled
    case 'failed':
      return CloseCircleFilled
    case 'pending':
      return MinusCircleOutlined
    default:
      return RobotOutlined
  }
}

/**
 * 获取状态颜色
 */
const getStatusColor = (status: string) => {
  switch (status) {
    case 'running':
      return 'processing'
    case 'completed':
      return 'success'
    case 'failed':
      return 'error'
    case 'pending':
      return 'default'
    default:
      return 'default'
  }
}

/**
 * 获取状态文本
 */
const getStatusText = (status: string) => {
  switch (status) {
    case 'running':
      return '执行中'
    case 'completed':
      return '已完成'
    case 'failed':
      return '失败'
    case 'pending':
      return '待执行'
    default:
      return '未知'
  }
}

/**
 * 格式化时间
 */
const formatTime = (timestamp: string) => {
  return dayjs(timestamp).format('HH:mm:ss')
}

/**
 * 格式化已用时间
 */
const formatElapsed = (startTime: string) => {
  return dayjs(startTime).fromNow(true)
}

/**
 * 格式化时长
 */
const formatDuration = (startTime: string, endTime: string) => {
  const start = dayjs(startTime)
  const end = dayjs(endTime)
  const seconds = end.diff(start, 'second')

  if (seconds < 60) return `${seconds}秒`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}分${seconds % 60}秒`

  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  return `${hours}时${minutes}分`
}

/**
 * 截断输出预览
 */
const truncateOutput = (output: any) => {
  const text = typeof output === 'string' ? output : JSON.stringify(output)
  const maxLength = 100
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
}

/**
 * 处理智能体点击
 */
const handleAgentClick = (agent: AgentExecution) => {
  emit('agentClick', agent)
}

/**
 * 处理查看输出
 */
const handleViewOutput = (agent: AgentExecution) => {
  emit('viewOutput', agent)
}
</script>

<style scoped lang="scss">
.agent-status-list {
  .list-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;

    .header-label {
      font-size: 14px;
      color: rgba(0, 0, 0, 0.45);
    }

    .header-value {
      font-size: 16px;
      font-weight: 600;
      color: #1890ff;
    }
  }

  .agent-item {
    padding: 12px 16px;
    cursor: pointer;
    transition: all 0.3s;
    border-radius: 4px;

    &:hover {
      background-color: #fafafa;
    }

    &.active {
      background-color: #e6f7ff;
      border-left: 3px solid #1890ff;
      animation: pulse 2s infinite;
    }

    .agent-title {
      display: flex;
      align-items: center;
      justify-content: space-between;

      .agent-name {
        font-size: 15px;
        font-weight: 500;
        color: rgba(0, 0, 0, 0.85);
      }

      .status-tag {
        margin-left: 8px;
        font-size: 12px;
      }
    }

    .agent-description {
      .agent-time {
        display: flex;
        align-items: center;
        font-size: 13px;
        color: rgba(0, 0, 0, 0.65);
        margin-bottom: 4px;

        .time-icon {
          margin-right: 4px;
        }
      }

      .agent-error {
        display: flex;
        align-items: center;
        font-size: 12px;
        color: #ff4d4f;
        margin-bottom: 4px;

        .error-icon {
          margin-right: 4px;
        }
      }

      .agent-output-preview {
        font-size: 12px;
        color: rgba(0, 0, 0, 0.45);
        margin-top: 8px;
        line-height: 1.4;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }
  }

  @keyframes pulse {
    0%,
    100% {
      box-shadow: 0 0 0 0 rgba(24, 144, 255, 0.4);
    }
    50% {
      box-shadow: 0 0 0 6px rgba(24, 144, 255, 0);
    }
  }
}
</style>
