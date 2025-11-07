<template>
  <div class="agent-execution-list">
    <a-card title="智能体执行状态">
      <a-steps
        :current="currentStepIndex"
        direction="vertical"
        :status="stepsStatus"
      >
        <a-step
          v-for="agent in agentList"
          :key="agent.name"
          :title="agent.name"
          :status="getStepStatus(agent.status)"
          :description="getStepDescription(agent)"
        >
          <template #icon>
            <template v-if="agent.status === 'running'">
              <a-spin size="small" />
            </template>
            <template v-else-if="agent.status === 'completed'">
              <CheckCircleOutlined style="color: #52c41a" />
            </template>
            <template v-else-if="agent.status === 'failed'">
              <CloseCircleOutlined style="color: #ff4d4f" />
            </template>
            <template v-else>
              <ClockCircleOutlined style="color: #d9d9d9" />
            </template>
          </template>

          <template #subTitle>
            <span v-if="agent.startTime" class="agent-time">
              {{ formatTime(agent.startTime) }}
            </span>
          </template>
        </a-step>
      </a-steps>

      <!-- 智能体详情抽屉 -->
      <a-drawer
        v-model:open="detailDrawerVisible"
        title="智能体执行详情"
        width="600"
        :body-style="{ padding: '24px' }"
      >
        <template v-if="selectedAgent">
          <a-descriptions :column="1" bordered>
            <a-descriptions-item label="智能体名称">
              {{ selectedAgent.name }}
            </a-descriptions-item>
            <a-descriptions-item label="状态">
              <a-tag :color="getStatusColor(selectedAgent.status)">
                {{ getStatusText(selectedAgent.status) }}
              </a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="开始时间" v-if="selectedAgent.startTime">
              {{ formatDateTime(selectedAgent.startTime) }}
            </a-descriptions-item>
            <a-descriptions-item label="结束时间" v-if="selectedAgent.endTime">
              {{ formatDateTime(selectedAgent.endTime) }}
            </a-descriptions-item>
            <a-descriptions-item label="执行时长" v-if="selectedAgent.endTime">
              {{ calculateDuration(selectedAgent.startTime, selectedAgent.endTime) }}
            </a-descriptions-item>
          </a-descriptions>

          <a-divider>输出结果</a-divider>

          <template v-if="selectedAgent.output">
            <a-card size="small">
              <pre class="agent-output">{{ JSON.stringify(selectedAgent.output, null, 2) }}</pre>
            </a-card>
          </template>
          <a-empty v-else description="暂无输出" />

          <template v-if="selectedAgent.error">
            <a-divider>错误信息</a-divider>
            <a-alert :message="selectedAgent.error" type="error" show-icon />
          </template>
        </template>
      </a-drawer>

      <!-- 点击步骤查看详情 -->
      <div class="agent-list-actions" style="margin-top: 24px">
        <a-button
          v-for="agent in agentList"
          :key="agent.name"
          size="small"
          type="link"
          @click="handleViewDetail(agent)"
          :disabled="!agent.startTime"
        >
          查看 {{ agent.name }} 详情
        </a-button>
      </div>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons-vue'
import dayjs from 'dayjs'
import type { AgentExecution, AgentStatus } from '@/types/workflow'

interface Props {
  agentExecutions: AgentExecution[]
}

const props = defineProps<Props>()

// State
const detailDrawerVisible = ref(false)
const selectedAgent = ref<AgentExecution | null>(null)

// 智能体列表（预定义顺序）
const predefinedAgents = [
  'Orchestrator',
  'Algorithm Expert',
  'Constraint Expert',
  'Objective Expert',
  'Domain Expert',
  'Code Implementation',
  'Extension Expert',
  'Quality Expert',
]

// 合并预定义列表和实际执行数据
const agentList = computed(() => {
  const executionMap = new Map(props.agentExecutions.map((e) => [e.name, e]))

  return predefinedAgents.map((name) => {
    const execution = executionMap.get(name)
    return (
      execution || {
        name,
        status: 'pending' as AgentStatus,
      }
    )
  })
})

// 当前步骤索引
const currentStepIndex = computed(() => {
  return agentList.value.findIndex((agent) => agent.status === 'running')
})

// 整体状态
const stepsStatus = computed(() => {
  const hasError = agentList.value.some((agent) => agent.status === 'failed')
  if (hasError) return 'error'

  const hasRunning = agentList.value.some((agent) => agent.status === 'running')
  if (hasRunning) return 'process'

  const allCompleted = agentList.value.every((agent) => agent.status === 'completed')
  if (allCompleted) return 'finish'

  return 'wait'
})

// 获取步骤状态
const getStepStatus = (status: AgentStatus) => {
  switch (status) {
    case 'completed':
      return 'finish'
    case 'running':
      return 'process'
    case 'failed':
      return 'error'
    default:
      return 'wait'
  }
}

// 获取步骤描述
const getStepDescription = (agent: AgentExecution) => {
  switch (agent.status) {
    case 'completed':
      return '已完成'
    case 'running':
      return '执行中...'
    case 'failed':
      return agent.error || '执行失败'
    default:
      return '等待执行'
  }
}

// 状态颜色映射
const getStatusColor = (status: AgentStatus) => {
  switch (status) {
    case 'completed':
      return 'success'
    case 'running':
      return 'processing'
    case 'failed':
      return 'error'
    default:
      return 'default'
  }
}

// 状态文本映射
const getStatusText = (status: AgentStatus) => {
  switch (status) {
    case 'completed':
      return '已完成'
    case 'running':
      return '执行中'
    case 'failed':
      return '失败'
    default:
      return '等待中'
  }
}

// 格式化时间
const formatTime = (time: string) => {
  return dayjs(time).format('HH:mm:ss')
}

const formatDateTime = (time: string) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

// 计算执行时长
const calculateDuration = (startTime?: string, endTime?: string) => {
  if (!startTime || !endTime) return '-'
  const duration = dayjs(endTime).diff(dayjs(startTime), 'second')
  if (duration < 60) return `${duration}秒`
  const minutes = Math.floor(duration / 60)
  const seconds = duration % 60
  return `${minutes}分${seconds}秒`
}

// 查看详情
const handleViewDetail = (agent: AgentExecution) => {
  selectedAgent.value = agent
  detailDrawerVisible.value = true
}
</script>

<style scoped lang="scss">
.agent-execution-list {
  .agent-time {
    font-size: 12px;
    color: rgba(0, 0, 0, 0.45);
    margin-left: 8px;
  }

  .agent-output {
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 12px;
    line-height: 1.5;
    max-height: 400px;
    overflow: auto;
    background: #f5f5f5;
    padding: 12px;
    border-radius: 4px;
  }

  .agent-list-actions {
    display: flex;
    flex-direction: column;
    gap: 8px;
    border-top: 1px solid #f0f0f0;
    padding-top: 16px;
  }
}
</style>
