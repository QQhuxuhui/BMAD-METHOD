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
          <a-button v-ripple v-if="isDev" @click="handleStart">
            <template #icon>
              <PlayCircleOutlined />
            </template>
            启动
          </a-button>
          <a-button v-ripple v-if="isDev" @click="handleStop">
            <template #icon>
              <PauseCircleOutlined />
            </template>
            停止
          </a-button>
          <a-button v-ripple v-if="isDev" @click="handleReset">
            <template #icon>
              <ReloadOutlined />
            </template>
            重置
          </a-button>
          <a-button v-ripple type="primary" @click="handleRefresh">
            <template #icon>
              <ReloadOutlined />
            </template>
            刷新
          </a-button>
        </a-space>
      </template>
    </a-page-header>

    <div class="monitor-content">
      <!-- 顶部：紧凑状态栏 -->
      <div class="status-bar">
        <workflow-status-card
          :show-actions="false"
          compact
          :horizontal="true"
          @start="handleStart"
          @stop="handleStop"
          @reset="handleReset"
        />
      </div>

      <!-- 主体：实时输出流（占主要区域） -->
      <div class="main-section">
        <output-stream />
      </div>

      <!-- 底部：横向流程图（可折叠） -->
      <div class="graph-section" :class="{ collapsed: graphCollapsed }">
        <div class="graph-header">
          <span class="graph-title">
            <DeploymentUnitOutlined />
            工作流协作图
          </span>
          <a-button v-ripple size="small" type="text" @click="toggleGraph">
            <template #icon>
              <UpOutlined v-if="!graphCollapsed" />
              <DownOutlined v-else />
            </template>
            {{ graphCollapsed ? '展开' : '收起' }}
          </a-button>
        </div>
        <div v-show="!graphCollapsed" class="graph-container">
          <workflow-graph :height="graphHeight" :horizontal="true" @node-click="handleNodeClick" />
        </div>
      </div>
    </div>

    <!-- 智能体输出详情Modal -->
    <a-modal
      v-model:open="outputModalVisible"
      :title="`智能体详情 - ${selectedAgentConfig?.nameCn || ''}`"
      width="80%"
      :footer="null"
      :destroy-on-close="true"
      :transition-name="'modal-fade'"
    >
      <div
        v-if="selectedAgent && selectedAgentConfig"
        v-motion
        :initial="{ opacity: 0, y: 20 }"
        :enter="{ opacity: 1, y: 0, transition: { duration: 300, ease: 'easeOut' } }"
        :leave="{ opacity: 0, y: -20, transition: { duration: 200 } }"
        class="agent-output-detail"
      >
        <!-- 智能体基本信息 -->
        <div class="agent-header">
          <span class="agent-icon">{{ selectedAgentConfig.icon }}</span>
          <div class="agent-info">
            <h3 class="agent-name">
              {{ selectedAgentConfig.nameCn }}
              <span class="agent-name-en">({{ selectedAgentConfig.nameEn }})</span>
            </h3>
            <p class="agent-description">{{ selectedAgentConfig.description }}</p>
          </div>
        </div>

        <a-divider />

        <!-- 执行状态信息 -->
        <a-descriptions :column="2" bordered size="small">
          <a-descriptions-item label="所属阶段">
            <a-tag color="blue">
              {{ getPhaseConfig(selectedAgentConfig.phase)?.name }}
            </a-tag>
            {{ getPhaseConfig(selectedAgentConfig.phase)?.description }}
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

        <!-- 输出内容 -->
        <h4>输出内容：</h4>
        <div v-if="selectedAgent.output"
             class="output-content markdown-body"
             v-html="formatAgentOutput(selectedAgent.output)">
        </div>
        <a-empty v-else description="暂无输出内容" />
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
import { getAgentConfig, type AgentConfig } from '@/config/agents'
import { getPhaseConfig } from '@/config/phases'
import WorkflowStatusCard from './components/WorkflowStatusCard.vue'
import OutputStream from './components/OutputStream.vue'
import WorkflowGraph from './components/WorkflowGraph.vue'
import {
  BugOutlined,
  ReloadOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  DeploymentUnitOutlined,
  UpOutlined,
  DownOutlined,
} from '@ant-design/icons-vue'
import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'
import { vRipple } from '@/directives/ripple'

// Configure marked with highlight.js
marked.setOptions({
  highlight: (code, lang) => {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(code, { language: lang }).value
      } catch (err) {
        console.error('Highlight error:', err)
      }
    }
    return hljs.highlightAuto(code).value
  },
  breaks: true,
  gfm: true
})

// Router
const router = useRouter()

// Store
const workflowStore = useWorkflowStore()

// State
const isDev = computed(() => import.meta.env.DEV)
const outputModalVisible = ref(false)
const selectedAgent = ref<AgentExecution | null>(null)
const selectedAgentConfig = ref<AgentConfig | null>(null)
const graphCollapsed = ref(false) // 流程图折叠状态

// 响应式屏幕尺寸(带防抖)
const windowWidth = ref(window.innerWidth)
const windowHeight = ref(window.innerHeight)

/**
 * 防抖函数
 */
const debounce = <T extends (...args: any[]) => void>(fn: T, delay: number) => {
  let timeoutId: ReturnType<typeof setTimeout>
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => fn(...args), delay)
  }
}

/**
 * 处理窗口大小变化(防抖300ms)
 */
const handleResize = debounce(() => {
  windowWidth.value = window.innerWidth
  windowHeight.value = window.innerHeight
}, 300)

/**
 * 计算图形高度
 * 屏幕高度 - Header高度 - 底部区域高度 - padding
 * 使用防抖后的窗口尺寸
 */
const graphHeight = computed(() => {
  // 移动端优化
  if (windowWidth.value < 768) {
    // 小屏幕：减少图形高度,为底部面板留更多空间
    const headerHeight = 120
    const bottomHeight = 500 // 移动端底部需要更多空间(垂直布局)
    const padding = 32
    return Math.max(400, windowHeight.value - headerHeight - bottomHeight - padding)
  }

  // 桌面端
  const headerHeight = 120
  const bottomHeight = 350
  const padding = 48
  return Math.max(500, windowHeight.value - headerHeight - bottomHeight - padding)
})

/**
 * 计算输出流高度
 * 根据屏幕尺寸动态调整
 * 使用防抖后的窗口宽度
 */
const outputStreamHeight = computed(() => {
  // 移动端：更高的输出流
  if (windowWidth.value < 768) {
    return 400
  }

  // 平板端
  if (windowWidth.value < 1024) {
    return 350
  }

  // 桌面端
  return 300
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
  // 添加窗口大小变化监听器
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  disconnect()
  // 移除窗口大小变化监听器
  window.removeEventListener('resize', handleResize)
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
 * 切换流程图展开/收起
 */
const toggleGraph = () => {
  graphCollapsed.value = !graphCollapsed.value
}

/**
 * 处理节点点击（从WorkflowGraph emit）
 */
const handleNodeClick = (agentId: string) => {
  console.log('[WorkflowMonitor] Node clicked:', agentId)

  // 从Store获取智能体执行数据
  const agent = workflowStore.agents.find((a) => a.id === agentId)
  // 从配置获取智能体静态信息
  const agentConfig = getAgentConfig(agentId)

  if (agent && agentConfig) {
    selectedAgent.value = agent
    selectedAgentConfig.value = agentConfig
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
 * 格式化智能体输出（支持Markdown）
 */
const formatAgentOutput = (output: any): string => {
  if (!output) return ''

  let text = ''
  if (typeof output === 'object') {
    if (output.content) {
      text = output.content
    } else {
      text = '```json\n' + JSON.stringify(output, null, 2) + '\n```'
    }
  } else {
    text = String(output)
  }

  try {
    return marked.parse(text) as string
  } catch (err) {
    console.error('Markdown parse error:', err)
    return text
  }
}
</script>

<style scoped lang="scss">
// Modal淡入淡出动画
:deep(.modal-fade-enter-active),
:deep(.modal-fade-leave-active) {
  transition: opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

:deep(.modal-fade-enter-from),
:deep(.modal-fade-leave-to) {
  opacity: 0;
}

.workflow-monitor {
  // 全屏布局,抵消MainLayout的padding和margin
  // 上下: -24px (抵消内层div padding)
  // 左右: -40px (抵消内层div padding 24px + 外层layout-content margin 16px)
  margin: -24px -40px;
  // 高度计算: 100vh - Header(64px) - layoutContent上下margin(32px) - Footer(90px)
  height: calc(100vh - 186px);
  display: flex;
  flex-direction: column;
  background-color: #f0f2f5;

  .monitor-content {
    flex: 1;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    overflow: hidden;

    // 顶部状态栏（紧凑）
    .status-bar {
      flex-shrink: 0;
      height: auto;
    }

    // 主体区域（输出流，占据主要空间）
    .main-section {
      flex: 1;
      min-height: 0; // 重要：允许flex子元素正确收缩
      overflow: hidden;
    }

    // 底部流程图区域（可折叠）
    .graph-section {
      flex-shrink: 0;
      background: white;
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
      overflow: hidden;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

      &:not(.collapsed) {
        height: 250px; // 默认展开高度
      }

      &.collapsed {
        height: 48px; // 折叠时只显示header
      }

      .graph-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 16px;
        background: linear-gradient(135deg, #f5f7fa 0%, #e8edf5 100%);
        border-bottom: 1px solid #e8e8e8;
        cursor: pointer;
        user-select: none;

        .graph-title {
          display: flex;
          align-items: center;
          gap: 8px;
          font-weight: 500;
          font-size: 14px;
          color: rgba(0, 0, 0, 0.85);

          .anticon {
            color: #1890ff;
          }
        }

        &:hover {
          background: linear-gradient(135deg, #e8edf5 0%, #dce5f2 100%);
        }
      }

      .graph-container {
        height: calc(100% - 48px);
        overflow: hidden;
      }
    }

    // 移动端优化
    @media (max-width: 768px) {
      padding: 12px;
      gap: 8px;

      .graph-section {
        &:not(.collapsed) {
          height: 200px; // 移动端减小高度
        }
      }
    }
  }

  .agent-output-detail {
    .agent-header {
      display: flex;
      align-items: flex-start;
      gap: 16px;
      padding: 16px;
      background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
      border-radius: 8px;
      margin-bottom: 16px;

      .agent-icon {
        font-size: 48px;
        line-height: 1;
      }

      .agent-info {
        flex: 1;

        .agent-name {
          margin: 0 0 8px 0;
          font-size: 20px;
          font-weight: 600;
          color: rgba(0, 0, 0, 0.85);

          .agent-name-en {
            font-size: 14px;
            font-weight: 400;
            color: rgba(0, 0, 0, 0.45);
            margin-left: 8px;
          }
        }

        .agent-description {
          margin: 0;
          font-size: 14px;
          color: rgba(0, 0, 0, 0.65);
          line-height: 1.6;
        }
      }

      // 移动端优化
      @media (max-width: 768px) {
        flex-direction: column;
        align-items: center;
        text-align: center;
        padding: 12px;
        gap: 12px;

        .agent-icon {
          font-size: 40px;
        }

        .agent-info {
          .agent-name {
            font-size: 18px;

            .agent-name-en {
              display: block;
              margin-left: 0;
              margin-top: 4px;
            }
          }

          .agent-description {
            font-size: 13px;
          }
        }
      }
    }

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

      // Markdown样式增强
      :deep(h1),
      :deep(h2),
      :deep(h3),
      :deep(h4) {
        margin-top: 16px;
        margin-bottom: 8px;
        font-weight: 600;
      }

      :deep(pre) {
        background-color: #282c34;
        border-radius: 4px;
        padding: 12px;
        overflow-x: auto;
      }

      :deep(code) {
        font-family: 'Courier New', monospace;
        font-size: 12px;
      }

      :deep(p) {
        margin: 8px 0;
      }

      :deep(ul),
      :deep(ol) {
        padding-left: 24px;
        margin: 8px 0;
      }
    }
  }
}
</style>
