<template>
  <div class="workflow-monitor">
    <a-page-header
      title="工作流监控面板"
      sub-title="智能体协作可视化 - 实时查看执行状态"
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
          <a-button v-if="isDev" @click="handleStart">
            <template #icon>
              <PlayCircleOutlined />
            </template>
            启动
          </a-button>
          <a-button v-if="isDev" @click="handleStop">
            <template #icon>
              <PauseCircleOutlined />
            </template>
            停止
          </a-button>
          <a-button v-if="isDev" @click="handleReset">
            <template #icon>
              <ReloadOutlined />
            </template>
            重置
          </a-button>
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
      <!-- 主要区域：工作流协作图 -->
      <div class="graph-section">
        <workflow-graph :height="graphHeight" @node-click="handleNodeClick" />
      </div>

      <!-- 底部区域：状态 + 输出流 -->
      <div class="bottom-section">
        <a-row :gutter="[16, 16]">
          <!-- 左侧：工作流状态卡片（简化版） -->
          <a-col :xs="24" :lg="6">
            <workflow-status-card
              :show-actions="false"
              compact
              @start="handleStart"
              @stop="handleStop"
              @reset="handleReset"
            />
          </a-col>

          <!-- 右侧：输出流 -->
          <a-col :xs="24" :lg="18">
            <output-stream :max-height="300" />
          </a-col>
        </a-row>
      </div>
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
import OutputStream from './components/OutputStream.vue'
import WorkflowGraph from './components/WorkflowGraph.vue'
import {
  BugOutlined,
  ReloadOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
} from '@ant-design/icons-vue'

// Router
const router = useRouter()

// Store
const workflowStore = useWorkflowStore()

// State
const isDev = computed(() => import.meta.env.DEV)
const outputModalVisible = ref(false)
const selectedAgent = ref<AgentExecution | null>(null)

/**
 * 计算图形高度
 * 屏幕高度 - Header高度 - 底部区域高度 - padding
 */
const graphHeight = computed(() => {
  const screenHeight = window.innerHeight
  const headerHeight = 120 // 约120px
  const bottomHeight = 350 // 底部区域约350px
  const padding = 48 // 上下padding
  return Math.max(500, screenHeight - headerHeight - bottomHeight - padding)
})

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
 * 处理节点点击（从WorkflowGraph emit）
 */
const handleNodeClick = (agentId: string) => {
  console.log('[WorkflowMonitor] Node clicked:', agentId)

  // 从Store获取智能体数据
  const agent = workflowStore.agents.find((a) => a.id === agentId)
  if (agent) {
    selectedAgent.value = agent
    outputModalVisible.value = true
  } else {
    message.warning('未找到智能体信息')
  }
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
    display: flex;
    flex-direction: column;
    gap: 16px;
    overflow: hidden;

    .graph-section {
      flex: 1;
      min-height: 500px;
      background: white;
      border-radius: 4px;
      overflow: hidden;
    }

    .bottom-section {
      flex-shrink: 0;
      max-height: 350px;
    }
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
