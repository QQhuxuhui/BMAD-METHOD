<template>
  <div class="workflow-history">
    <a-card title="执行历史">
      <template #extra>
        <a-space>
          <!-- 时间范围过滤 -->
          <a-range-picker
            v-model:value="timeRange"
            :show-time="true"
            format="YYYY-MM-DD HH:mm:ss"
            style="width: 380px"
          />

          <!-- 导出按钮 -->
          <a-button @click="handleExport" size="small">
            <template #icon>
              <DownloadOutlined />
            </template>
            导出
          </a-button>

          <!-- 回放按钮（可选） -->
          <a-button
            v-if="enablePlayback"
            @click="handleStartPlayback"
            size="small"
            :disabled="filteredHistory.length === 0"
          >
            <template #icon>
              <PlayCircleOutlined />
            </template>
            回放
          </a-button>
        </a-space>
      </template>

      <!-- 历史记录表格 -->
      <a-table
        :columns="columns"
        :data-source="filteredHistory"
        :pagination="pagination"
        :loading="loading"
        row-key="id"
        size="small"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'event'">
            <a-tag :color="getEventColor(record.event)">
              {{ getEventTypeLabel(record.event) }}
            </a-tag>
          </template>

          <template v-else-if="column.key === 'timestamp'">
            {{ formatDateTime(record.data.timestamp) }}
          </template>

          <template v-else-if="column.key === 'agent'">
            <span v-if="record.data.agent_name">
              {{ record.data.agent_name }}
            </span>
            <span v-else class="text-muted">-</span>
          </template>

          <template v-else-if="column.key === 'phase'">
            <a-tag v-if="record.data.phase" color="blue">
              {{ record.data.phase }}
            </a-tag>
            <span v-else class="text-muted">-</span>
          </template>

          <template v-else-if="column.key === 'actions'">
            <a-button type="link" size="small" @click="handleViewDetail(record)">
              查看详情
            </a-button>
          </template>
        </template>
      </a-table>

      <!-- 统计信息 -->
      <div class="history-stats">
        <a-space>
          <span>总事件数: {{ events.length }}</span>
          <a-divider type="vertical" />
          <span>智能体执行: {{ agentEventCount }}</span>
          <a-divider type="vertical" />
          <span>阶段变更: {{ phaseChangeCount }}</span>
          <a-divider type="vertical" />
          <span>审批事件: {{ approvalEventCount }}</span>
        </a-space>
      </div>
    </a-card>

    <!-- 详情Drawer -->
    <a-drawer
      v-model:open="detailDrawerVisible"
      title="事件详情"
      width="700"
      :body-style="{ padding: '24px' }"
    >
      <template v-if="selectedEvent">
        <a-descriptions :column="1" bordered size="small">
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
            <a-tag color="blue">{{ selectedEvent.data.phase }}</a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="智能体" v-if="selectedEvent.data.agent_name">
            {{ selectedEvent.data.agent_name }}
          </a-descriptions-item>
          <a-descriptions-item
            label="审批点"
            v-if="selectedEvent.data.approval_point"
          >
            <a-tag color="warning">{{ selectedEvent.data.approval_point }}</a-tag>
          </a-descriptions-item>
        </a-descriptions>

        <a-divider>事件数据</a-divider>

        <a-tabs>
          <a-tab-pane key="formatted" tab="格式化视图">
            <a-card size="small">
              <pre class="event-data">{{ formatJSON(selectedEvent.data) }}</pre>
            </a-card>
          </a-tab-pane>
          <a-tab-pane key="raw" tab="原始数据">
            <a-card size="small">
              <pre class="event-data">{{ JSON.stringify(selectedEvent, null, 2) }}</pre>
            </a-card>
          </a-tab-pane>
        </a-tabs>
      </template>
    </a-drawer>

    <!-- 回放Modal -->
    <a-modal
      v-model:open="playbackModalVisible"
      title="工作流回放"
      width="800px"
      :footer="null"
      :destroy-on-close="true"
    >
      <div class="playback-controls">
        <a-space>
          <a-button
            @click="playbackState.isPlaying ? pausePlayback() : resumePlayback()"
          >
            <template #icon>
              <PlayCircleOutlined v-if="!playbackState.isPlaying" />
              <PauseCircleOutlined v-else />
            </template>
            {{ playbackState.isPlaying ? '暂停' : '播放' }}
          </a-button>
          <a-button @click="stopPlayback">
            <template #icon>
              <StopOutlined />
            </template>
            停止
          </a-button>

          <a-divider type="vertical" />

          <span>速度:</span>
          <a-select v-model:value="playbackState.speed" style="width: 100px">
            <a-select-option :value="1">1x</a-select-option>
            <a-select-option :value="2">2x</a-select-option>
            <a-select-option :value="5">5x</a-select-option>
            <a-select-option :value="10">10x</a-select-option>
          </a-select>
        </a-space>
      </div>

      <a-progress
        :percent="playbackProgress"
        :show-info="true"
        :format="() => `${playbackState.currentIndex + 1} / ${filteredHistory.length}`"
        style="margin: 16px 0"
      />

      <a-card
        v-if="playbackState.currentEvent"
        title="当前事件"
        size="small"
        style="margin-top: 16px"
      >
        <a-descriptions :column="1" size="small">
          <a-descriptions-item label="类型">
            <a-tag :color="getEventColor(playbackState.currentEvent.event)">
              {{ getEventTypeLabel(playbackState.currentEvent.event) }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="时间">
            {{ formatDateTime(playbackState.currentEvent.data.timestamp) }}
          </a-descriptions-item>
          <a-descriptions-item
            label="智能体"
            v-if="playbackState.currentEvent.data.agent_name"
          >
            {{ playbackState.currentEvent.data.agent_name }}
          </a-descriptions-item>
        </a-descriptions>
      </a-card>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { message } from 'ant-design-vue'
import {
  DownloadOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  StopOutlined,
} from '@ant-design/icons-vue'
import dayjs, { Dayjs } from 'dayjs'
import type { WorkflowEvent, WorkflowEventType } from '@/types/workflow'

interface Props {
  events: WorkflowEvent[]
  loading?: boolean
  enablePlayback?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  enablePlayback: true,
})

// State
const timeRange = ref<[Dayjs, Dayjs] | null>(null)
const detailDrawerVisible = ref(false)
const selectedEvent = ref<WorkflowEvent | null>(null)
const playbackModalVisible = ref(false)
const playbackState = ref({
  isPlaying: false,
  currentIndex: 0,
  currentEvent: null as WorkflowEvent | null,
  speed: 1,
  timer: null as number | null,
})

// 表格列定义
const columns = [
  { title: '时间', key: 'timestamp', width: 180 },
  { title: '事件类型', key: 'event', width: 120 },
  { title: '阶段', key: 'phase', width: 80 },
  { title: '智能体', key: 'agent', width: 150 },
  { title: '操作', key: 'actions', width: 100 },
]

// 分页配置
const pagination = ref({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showTotal: (total: number) => `共 ${total} 条`,
})

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

// 过滤后的历史记录
const filteredHistory = computed(() => {
  let result = props.events.map((event, index) => ({
    ...event,
    id: index,
  }))

  // 按时间范围过滤
  if (timeRange.value) {
    const [start, end] = timeRange.value
    result = result.filter((e) => {
      const timestamp = dayjs(e.data.timestamp)
      return timestamp.isAfter(start) && timestamp.isBefore(end)
    })
  }

  // 更新分页总数
  pagination.value.total = result.length

  return result
})

// 统计信息
const agentEventCount = computed(() => {
  return props.events.filter(
    (e) => e.event === 'agent_started' || e.event === 'agent_completed',
  ).length
})

const phaseChangeCount = computed(() => {
  return props.events.filter((e) => e.event === 'phase_changed').length
})

const approvalEventCount = computed(() => {
  return props.events.filter((e) => e.event === 'approval_required').length
})

// 回放进度
const playbackProgress = computed(() => {
  if (filteredHistory.value.length === 0) return 0
  return Math.round(
    ((playbackState.value.currentIndex + 1) / filteredHistory.value.length) * 100,
  )
})

// 获取事件类型标签
const getEventTypeLabel = (type: WorkflowEventType) => {
  return eventTypeLabels[type] || type
}

// 获取事件颜色
const getEventColor = (type: WorkflowEventType) => {
  return eventColors[type] || 'default'
}

// 格式化时间
const formatDateTime = (time: string) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

// 格式化JSON
const formatJSON = (data: any): string => {
  try {
    return JSON.stringify(data, null, 2)
  } catch (e) {
    return String(data)
  }
}

// 查看详情
const handleViewDetail = (event: WorkflowEvent) => {
  selectedEvent.value = event
  detailDrawerVisible.value = true
}

// 导出历史
const handleExport = () => {
  try {
    const dataStr = JSON.stringify(filteredHistory.value, null, 2)
    const blob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `workflow-history-${dayjs().format('YYYY-MM-DD-HHmmss')}.json`
    link.click()
    URL.revokeObjectURL(url)
    message.success('导出成功')
  } catch (error) {
    message.error('导出失败')
    console.error('Export failed:', error)
  }
}

// 开始回放
const handleStartPlayback = () => {
  playbackState.value.currentIndex = 0
  playbackState.value.currentEvent = filteredHistory.value[0] || null
  playbackState.value.isPlaying = true
  playbackModalVisible.value = true
  startPlaybackTimer()
}

// 暂停回放
const pausePlayback = () => {
  playbackState.value.isPlaying = false
  if (playbackState.value.timer) {
    clearInterval(playbackState.value.timer)
    playbackState.value.timer = null
  }
}

// 继续回放
const resumePlayback = () => {
  playbackState.value.isPlaying = true
  startPlaybackTimer()
}

// 停止回放
const stopPlayback = () => {
  pausePlayback()
  playbackState.value.currentIndex = 0
  playbackState.value.currentEvent = null
  playbackModalVisible.value = false
}

// 开始回放定时器
const startPlaybackTimer = () => {
  if (playbackState.value.timer) {
    clearInterval(playbackState.value.timer)
  }

  const interval = 1000 / playbackState.value.speed

  playbackState.value.timer = window.setInterval(() => {
    if (playbackState.value.currentIndex < filteredHistory.value.length - 1) {
      playbackState.value.currentIndex++
      playbackState.value.currentEvent =
        filteredHistory.value[playbackState.value.currentIndex] || null
    } else {
      pausePlayback()
      message.success('回放完成')
    }
  }, interval)
}
</script>

<style scoped lang="scss">
.workflow-history {
  .text-muted {
    color: rgba(0, 0, 0, 0.25);
  }

  .history-stats {
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid #f0f0f0;
    font-size: 13px;
    color: rgba(0, 0, 0, 0.65);
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
    margin: 0;
  }

  .playback-controls {
    padding: 16px;
    background: #f5f5f5;
    border-radius: 4px;
  }
}
</style>
