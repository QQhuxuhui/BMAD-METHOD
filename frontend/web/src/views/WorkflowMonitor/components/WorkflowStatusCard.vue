<template>
  <a-card title="工作流状态" :bordered="false" class="workflow-status-card">
    <template #extra>
      <a-tag :color="statusColor" class="status-tag">
        <template #icon>
          <component :is="statusIcon" :spin="status === 'running'" />
        </template>
        {{ statusText }}
      </a-tag>
    </template>

    <a-space direction="vertical" :size="16" style="width: 100%">
      <!-- 进度条 -->
      <div class="progress-section">
        <div class="progress-header">
          <span class="progress-label">整体进度</span>
          <span class="progress-value">{{ progress }}%</span>
        </div>
        <a-progress
          :percent="progress"
          :status="progressStatus"
          :stroke-color="progressColor"
          :show-info="false"
        />
      </div>

      <!-- 统计信息 -->
      <a-row :gutter="16">
        <a-col :span="8">
          <a-statistic
            title="当前阶段"
            :value="currentPhaseText"
            :value-style="{ color: '#1890ff', fontSize: '20px' }"
          >
            <template #prefix>
              <RocketOutlined />
            </template>
          </a-statistic>
        </a-col>

        <a-col :span="8">
          <a-statistic
            title="运行时长"
            :value="formatDuration(duration)"
            :value-style="{ color: '#52c41a', fontSize: '20px' }"
          >
            <template #prefix>
              <ClockCircleOutlined />
            </template>
          </a-statistic>
        </a-col>

        <a-col :span="8">
          <a-statistic
            title="完成智能体"
            :value="`${completedCount}/${totalCount}`"
            :value-style="{ color: '#722ed1', fontSize: '20px' }"
          >
            <template #prefix>
              <CheckCircleOutlined />
            </template>
          </a-statistic>
        </a-col>
      </a-row>

      <!-- 错误信息 -->
      <a-alert
        v-if="error"
        type="error"
        :message="error.message"
        show-icon
        closable
        class="error-alert"
      />

      <!-- 操作按钮（开发模式） -->
      <div v-if="isDev" class="actions">
        <a-space>
          <a-button
            type="primary"
            :icon="h(PlayCircleOutlined)"
            :disabled="isRunning"
            @click="handleStart"
          >
            启动工作流
          </a-button>
          <a-button
            danger
            :icon="h(StopOutlined)"
            :disabled="!isRunning"
            @click="handleStop"
          >
            停止
          </a-button>
          <a-button :icon="h(ReloadOutlined)" @click="handleReset">
            重置
          </a-button>
        </a-space>
      </div>
    </a-space>
  </a-card>
</template>

<script setup lang="ts">
import { computed, h } from 'vue'
import { useWorkflowStore } from '@/stores/workflow'
import {
  CheckCircleOutlined,
  ClockCircleOutlined,
  RocketOutlined,
  LoadingOutlined,
  CheckCircleFilled,
  CloseCircleFilled,
  PauseCircleFilled,
  PlayCircleOutlined,
  StopOutlined,
  ReloadOutlined
} from '@ant-design/icons-vue'

// Props
interface Props {
  /** 是否显示操作按钮（开发模式） */
  showActions?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showActions: import.meta.env.DEV
})

// Emits
const emit = defineEmits<{
  start: []
  stop: []
  reset: []
}>()

// Store
const workflowStore = useWorkflowStore()

// Computed
const status = computed(() => workflowStore.status)
const progress = computed(() => workflowStore.progress)
const duration = computed(() => workflowStore.duration)
const error = computed(() => workflowStore.error)
const currentPhaseInfo = computed(() => workflowStore.currentPhaseInfo)
const completedCount = computed(() => workflowStore.completedAgents.length)
const totalCount = computed(() => workflowStore.agents.length)
const isRunning = computed(() => workflowStore.isRunning)
const isDev = computed(() => import.meta.env.DEV && props.showActions)

/**
 * 状态文本
 */
const statusText = computed(() => {
  switch (status.value) {
    case 'idle':
      return '待启动'
    case 'running':
      return '运行中'
    case 'paused':
      return '已暂停'
    case 'completed':
      return '已完成'
    case 'failed':
      return '执行失败'
    default:
      return '未知状态'
  }
})

/**
 * 状态颜色
 */
const statusColor = computed(() => {
  switch (status.value) {
    case 'idle':
      return 'default'
    case 'running':
      return 'processing'
    case 'paused':
      return 'warning'
    case 'completed':
      return 'success'
    case 'failed':
      return 'error'
    default:
      return 'default'
  }
})

/**
 * 状态图标
 */
const statusIcon = computed(() => {
  switch (status.value) {
    case 'running':
      return LoadingOutlined
    case 'paused':
      return PauseCircleFilled
    case 'completed':
      return CheckCircleFilled
    case 'failed':
      return CloseCircleFilled
    default:
      return CheckCircleOutlined
  }
})

/**
 * 进度条状态
 */
const progressStatus = computed(() => {
  if (status.value === 'failed') return 'exception'
  if (status.value === 'completed') return 'success'
  return 'active'
})

/**
 * 进度条颜色
 */
const progressColor = computed(() => {
  if (status.value === 'failed') return '#ff4d4f'
  if (status.value === 'completed') return '#52c41a'
  return {
    '0%': '#108ee9',
    '100%': '#87d068'
  }
})

/**
 * 当前Phase文本
 */
const currentPhaseText = computed(() => {
  if (currentPhaseInfo.value) {
    return `Phase ${currentPhaseInfo.value.id}`
  }
  return status.value === 'idle' ? '未开始' : '-'
})

/**
 * 格式化时长
 */
const formatDuration = (seconds: number): string => {
  if (seconds === 0) return '00:00:00'

  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60

  return [hours, minutes, secs].map(v => String(v).padStart(2, '0')).join(':')
}

/**
 * 处理启动
 */
const handleStart = () => {
  emit('start')
}

/**
 * 处理停止
 */
const handleStop = () => {
  emit('stop')
}

/**
 * 处理重置
 */
const handleReset = () => {
  emit('reset')
}
</script>

<style scoped lang="scss">
.workflow-status-card {
  .status-tag {
    font-size: 14px;
    font-weight: 500;
    padding: 4px 12px;
  }

  .progress-section {
    .progress-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;

      .progress-label {
        font-size: 14px;
        color: rgba(0, 0, 0, 0.65);
      }

      .progress-value {
        font-size: 16px;
        font-weight: 600;
        color: #1890ff;
      }
    }
  }

  .error-alert {
    margin-top: 8px;
  }

  .actions {
    padding-top: 8px;
    border-top: 1px solid #f0f0f0;
  }

  :deep(.ant-statistic-title) {
    font-size: 13px;
    margin-bottom: 4px;
  }

  :deep(.ant-statistic-content) {
    font-size: 20px;
  }
}
</style>
