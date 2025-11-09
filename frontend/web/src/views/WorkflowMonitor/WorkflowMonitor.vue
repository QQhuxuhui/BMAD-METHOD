<template>
  <div class="workflow-monitor">
    <a-page-header
      title="工作流监控面板"
      sub-title="实时查看智能体执行状态和输出"
      @back="handleBack"
    >
      <template #extra>
        <a-space>
          <a-tag v-if="isDev" color="orange">
            <template #icon>
              <BugOutlined />
            </template>
            开发模式 (Mock数据)
          </a-tag>
          <a-button type="primary" @click="handleRefresh">
            <template #icon>
              <ReloadOutlined />
            </template>
            刷新
          </a-button>
        </a-space>
      </template>
    </a-page-header>

    <div class="monitor-content">
      <a-row :gutter="[16, 16]">
        <!-- 左侧列：状态卡片 + 智能体列表 -->
        <a-col :xs="24" :lg="8">
          <a-space direction="vertical" :size="16" style="width: 100%">
            <!-- 工作流状态卡片 -->
            <workflow-status-card
              :show-actions="isDev"
              @start="handleStart"
              @stop="handleStop"
              @reset="handleReset"
            />

            <!-- 智能体状态列表 -->
            <agent-status-list @agent-click="handleAgentClick" @view-output="handleViewOutput" />
          </a-space>
        </a-col>

        <!-- 右侧列：输出流 -->
        <a-col :xs="24" :lg="16">
          <output-stream />
        </a-col>
      </a-row>
    </div>

    <!-- 智能体输出详情Modal -->
    <a-modal
      v-model:open="outputModalVisible"
      title="智能体输出详情"
      width="80%"
      :footer="null"
      :destroy-on-close="true"
    >
      <div v-if="selectedAgent" class="agent-output-detail">
        <a-descriptions :column="2" bordered size="small">
          <a-descriptions-item label="智能体名称">
            {{ selectedAgent.name }}
          </a-descriptions-item>
          <a-descriptions-item label="执行状态">
            <a-tag :color="getAgentStatusColor(selectedAgent.status)">
              {{ getAgentStatusText(selectedAgent.status) }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="开始时间">
            {{ selectedAgent.startTime || '-' }}
          </a-descriptions-item>
          <a-descriptions-item label="结束时间">
            {{ selectedAgent.endTime || '-' }}
          </a-descriptions-item>
        </a-descriptions>

        <a-divider />

        <h4>输出内容：</h4>
        <pre class="output-content">{{ formatAgentOutput(selectedAgent.output) }}</pre>
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { useWorkflowStore } from '@/stores/workflow'
import { useWorkflowStream } from '@/hooks/useWorkflowStream'
import type { AgentExecution } from '@/types/workflow'
import WorkflowStatusCard from './components/WorkflowStatusCard.vue'
import AgentStatusList from './components/AgentStatusList.vue'
import OutputStream from './components/OutputStream.vue'
import { BugOutlined, ReloadOutlined } from '@ant-design/icons-vue'

// Router
const router = useRouter()

// Store
const workflowStore = useWorkflowStore()

// State
const isDev = computed(() => import.meta.env.DEV)
const outputModalVisible = ref(false)
const selectedAgent = ref<AgentExecution | null>(null)

// Workflow Stream Hook
const { status: streamStatus, connect, disconnect, reconnect } = useWorkflowStream(
  {
    workflowId: 'demo-workflow-001',
    autoConnect: false,
    onApprovalRequired: (context) => {
      message.warning('需要人工审批：' + JSON.stringify(context))
    },
    onError: (error) => {
      message.error('工作流执行错误：' + error.message)
    },
    onComplete: () => {
      message.success('工作流执行完成！')
    }
  },
  true // 使用Mock数据
)

// Lifecycle
onMounted(() => {
  console.log('[WorkflowMonitor] Component mounted')
})

onBeforeUnmount(() => {
  disconnect()
  console.log('[WorkflowMonitor] Component unmounted')
})

/**
 * 处理返回
 */
const handleBack = () => {
  router.back()
}

/**
 * 处理刷新
 */
const handleRefresh = () => {
  reconnect()
  message.info('重新连接工作流')
}

/**
 * 处理启动工作流
 */
const handleStart = () => {
  workflowStore.reset()
  connect()
  message.success('工作流已启动')
}

/**
 * 处理停止工作流
 */
const handleStop = () => {
  disconnect()
  message.info('工作流已停止')
}

/**
 * 处理重置
 */
const handleReset = () => {
  disconnect()
  workflowStore.reset()
  message.info('工作流已重置')
}

/**
 * 处理智能体点击
 */
const handleAgentClick = (agent: AgentExecution) => {
  console.log('[WorkflowMonitor] Agent clicked:', agent.name)
  if (agent.output) {
    selectedAgent.value = agent
    outputModalVisible.value = true
  }
}

/**
 * 处理查看输出
 */
const handleViewOutput = (agent: AgentExecution) => {
  selectedAgent.value = agent
  outputModalVisible.value = true
}

/**
 * 获取智能体状态颜色
 */
const getAgentStatusColor = (status: string) => {
  switch (status) {
    case 'running':
      return 'processing'
    case 'completed':
      return 'success'
    case 'failed':
      return 'error'
    default:
      return 'default'
  }
}

/**
 * 获取智能体状态文本
 */
const getAgentStatusText = (status: string) => {
  switch (status) {
    case 'running':
      return '执行中'
    case 'completed':
      return '已完成'
    case 'failed':
      return '失败'
    default:
      return '待执行'
  }
}

/**
 * 格式化智能体输出
 */
const formatAgentOutput = (output: any) => {
  if (!output) return '暂无输出'
  if (typeof output === 'string') return output
  return JSON.stringify(output, null, 2)
}
</script>

<style scoped lang="scss">
.workflow-monitor {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #f0f2f5;

  .monitor-content {
    flex: 1;
    padding: 16px;
    overflow-y: auto;
  }

  .agent-output-detail {
    .output-content {
      margin-top: 12px;
      padding: 16px;
      background-color: #f6f6f6;
      border-radius: 4px;
      font-family: 'Courier New', monospace;
      font-size: 13px;
      line-height: 1.6;
      max-height: 500px;
      overflow-y: auto;
      white-space: pre-wrap;
      word-wrap: break-word;
    }
  }
}
</style>
